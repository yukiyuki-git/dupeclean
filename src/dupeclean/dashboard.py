"""File deduplication statistics dashboard for DupeClean.

Generate interactive dashboard data for dedup statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class DashboardWidget:
    """A dashboard widget."""

    widget_type: str  # "metric", "chart", "table", "gauge"
    title: str
    data: dict = field(default_factory=dict)


@dataclass
class Dashboard:
    """A dedup statistics dashboard."""

    title: str
    widgets: list[DashboardWidget] = field(default_factory=list)

    def add_metric(self, title: str, value: str, subtitle: str = "") -> None:
        self.widgets.append(
            DashboardWidget(
                widget_type="metric",
                title=title,
                data={"value": value, "subtitle": subtitle},
            )
        )

    def add_gauge(self, title: str, value: float, max_value: float = 100.0) -> None:
        self.widgets.append(
            DashboardWidget(
                widget_type="gauge",
                title=title,
                data={"value": value, "max": max_value},
            )
        )

    def add_chart(self, title: str, labels: list[str], values: list[float]) -> None:
        self.widgets.append(
            DashboardWidget(
                widget_type="chart",
                title=title,
                data={"labels": labels, "values": values},
            )
        )

    def add_table(self, title: str, headers: list[str], rows: list[list[str]]) -> None:
        self.widgets.append(
            DashboardWidget(
                widget_type="table",
                title=title,
                data={"headers": headers, "rows": rows},
            )
        )

    def render(self) -> str:
        """Render dashboard as text."""
        lines = [self.title, "=" * len(self.title), ""]

        for widget in self.widgets:
            lines.append(f"  {widget.title}")
            lines.append("  " + "-" * len(widget.title))

            if widget.widget_type == "metric":
                value = widget.data.get("value", "")
                subtitle = widget.data.get("subtitle", "")
                lines.append(f"    {value}")
                if subtitle:
                    lines.append(f"    {subtitle}")

            elif widget.widget_type == "gauge":
                value = widget.data.get("value", 0)
                max_val = widget.data.get("max", 100)
                pct = (value / max_val * 100) if max_val > 0 else 0
                filled = int(pct / 100 * 30)
                bar = "█" * filled + "░" * (30 - filled)
                lines.append(f"    [{bar}] {pct:.1f}%")

            elif widget.widget_type == "chart":
                labels = widget.data.get("labels", [])
                values = widget.data.get("values", [])
                max_val = max(values) if values else 1
                for label, val in zip(labels, values, strict=True):
                    bar_len = int(val / max_val * 20) if max_val > 0 else 0
                    bar = "█" * bar_len
                    lines.append(f"    {label:<15s} {bar} {val}")

            elif widget.widget_type == "table":
                headers = widget.data.get("headers", [])
                rows = widget.data.get("rows", [])
                if headers:
                    lines.append(f"    {'  '.join(headers)}")
                    lines.append("    " + "-" * (len(headers) * 20))
                for row in rows:
                    lines.append(f"    {'  '.join(row)}")

            lines.append("")

        return "\n".join(lines)


def create_dashboard(
    files: list[FileInfo],
    groups: list[DuplicateGroup],
) -> Dashboard:
    """Create a dashboard from analysis results."""
    dashboard = Dashboard(title="DupeClean Dashboard")

    # Metrics
    total_size = sum(f.size for f in files)
    total_wasted = sum(g.wasted_space for g in groups)
    dashboard.add_metric("Total Files", f"{len(files):,}")
    dashboard.add_metric("Total Size", format_size(total_size))
    dashboard.add_metric("Duplicate Groups", f"{len(groups):,}")
    dashboard.add_metric("Wasted Space", format_size(total_wasted))

    # Gauge
    if total_size > 0:
        waste_pct = total_wasted / total_size * 100
        dashboard.add_gauge("Waste %", waste_pct)

    # Size distribution chart
    size_buckets = {"<1KB": 0, "1-64KB": 0, "64KB-1MB": 0, "1-16MB": 0, ">16MB": 0}
    for fi in files:
        if fi.size < 1024:
            size_buckets["<1KB"] += 1
        elif fi.size < 65536:
            size_buckets["1-64KB"] += 1
        elif fi.size < 1048576:
            size_buckets["64KB-1MB"] += 1
        elif fi.size < 16777216:
            size_buckets["1-16MB"] += 1
        else:
            size_buckets[">16MB"] += 1

    dashboard.add_chart(
        "Size Distribution",
        list(size_buckets.keys()),
        list(size_buckets.values()),
    )

    return dashboard
