"""Report generation for DupeClean."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .analyzer import AnalysisResult
from .models import format_duration, format_size


class ReportGenerator:
    def __init__(self, result: AnalysisResult) -> None:
        self.result = result

    def generate(self, format: str, output: Optional[Path] = None) -> Optional[str]:
        if format == "json":
            content = self._json_report()
        elif format == "csv":
            content = self._csv_report()
        elif format == "html":
            content = self._html_report()
        else:
            return None
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
        return content

    def _json_report(self) -> str:
        data = {
            "generated_at": datetime.now().isoformat(),
            "directory": str(self.result.root),
            "summary": {
                "total_size": self.result.stats.total_size,
                "total_size_display": format_size(self.result.stats.total_size),
                "total_files": self.result.stats.total_files,
                "total_dirs": self.result.stats.total_dirs,
                "duplicate_groups": self.result.stats.duplicate_groups,
                "duplicate_files": self.result.stats.duplicate_files,
                "wasted_space": self.result.stats.wasted_space,
                "wasted_space_display": format_size(self.result.stats.wasted_space),
                "dupe_percentage": round(self.result.stats.dupe_percentage, 2),
                "scan_duration": round(self.result.stats.scan_duration, 2),
            },
            "top_extensions": [
                {"extension": ext, "count": count, "total_size": size}
                for ext, count, size in self.result.top_extensions[:20]
            ],
            "largest_files": [
                {"path": str(f.path), "size": f.size, "size_display": f.size_display, "extension": f.ext}
                for f in self.result.largest_files[:50]
            ],
            "duplicate_groups": [
                {
                    "group_id": g.group_id, "hash": g.hash_value, "file_size": g.file_size,
                    "file_size_display": g.size_display, "count": g.count,
                    "wasted_space": g.wasted_space, "wasted_space_display": g.wasted_display,
                    "files": [str(f.path) for f in g.files],
                }
                for g in self.result.top_duplicates
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _csv_report(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Group ID", "File Path", "Size", "Extension", "Hash", "Modified"])
        for group in self.result.top_duplicates:
            for fi in group.files:
                writer.writerow([
                    group.group_id, str(fi.path), fi.size, fi.ext,
                    group.hash_value, datetime.fromtimestamp(fi.mtime).isoformat(),
                ])
        return output.getvalue()

    def _html_report(self) -> str:
        r = self.result
        s = r.stats
        ext_rows = ""
        for ext, count, size in r.top_extensions[:15]:
            pct = (size / s.total_size * 100) if s.total_size > 0 else 0
            ext_rows += f'<tr><td>.{ext or "(none)"}</td><td>{count:,}</td><td>{format_size(size)}</td><td>{pct:.1f}%</td></tr>'
        largest_rows = ""
        for fi in r.largest_files[:20]:
            largest_rows += f'<tr><td title="{fi.path}">{fi.path.name}</td><td>{fi.size_display}</td><td>{fi.ext or "-"}</td><td class="path">{fi.path.parent}</td></tr>'
        dup_rows = ""
        for g in r.top_duplicates[:20]:
            files_list = "<br>".join(str(f.path) for f in g.files)
            dup_rows += f'<tr><td>{g.group_id}</td><td>{g.count}</td><td>{g.size_display}</td><td>{g.wasted_display}</td><td class="files">{files_list}</td></tr>'
        warn = 'warn' if s.wasted_space > 0 else 'good'
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DupeClean Report — {r.root}</title>
<style>
:root{{--bg:#1a1b26;--fg:#c0caf5;--accent:#7aa2f7;--red:#f7768e;--green:#9ece6a;--border:#292e42;--card:#24283b}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--fg);line-height:1.6;padding:2rem}}
h1{{color:var(--accent);margin-bottom:.5rem;font-size:1.8rem}}
.subtitle{{color:#565f89;margin-bottom:2rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:2rem}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1.2rem}}
.card .label{{color:#565f89;font-size:.85rem;text-transform:uppercase}}
.card .value{{font-size:1.8rem;font-weight:700;color:var(--accent)}}
.card .value.warn{{color:var(--red)}}
.card .value.good{{color:var(--green)}}
table{{width:100%;border-collapse:collapse;margin-bottom:2rem}}
th{{text-align:left;padding:.8rem;border-bottom:2px solid var(--border);color:var(--accent);font-size:.85rem;text-transform:uppercase}}
td{{padding:.6rem .8rem;border-bottom:1px solid var(--border)}}
tr:hover{{background:rgba(122,162,247,.05)}}
.path{{color:#565f89;font-size:.85rem;word-break:break-all}}
.files{{font-size:.8rem;color:#a9b1d6;word-break:break-all}}
h2{{color:var(--fg);margin:1.5rem 0 1rem;font-size:1.3rem}}
.footer{{text-align:center;color:#565f89;margin-top:3rem;font-size:.85rem}}
</style>
</head>
<body>
<h1>🔍 DupeClean Report</h1>
<p class="subtitle">{r.root} — generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
<div class="grid">
<div class="card"><div class="label">Total Size</div><div class="value">{format_size(s.total_size)}</div></div>
<div class="card"><div class="label">Files</div><div class="value">{s.total_files:,}</div></div>
<div class="card"><div class="label">Duplicate Groups</div><div class="value {'warn' if s.duplicate_groups > 0 else 'good'}">{s.duplicate_groups:,}</div></div>
<div class="card"><div class="label">Wasted Space</div><div class="value {warn}">{format_size(s.wasted_space)}</div></div>
<div class="card"><div class="label">Scan Time</div><div class="value">{format_duration(s.scan_duration)}</div></div>
</div>
<h2>📁 File Types</h2>
<table><thead><tr><th>Extension</th><th>Count</th><th>Size</th><th>% of Total</th></tr></thead><tbody>{ext_rows}</tbody></table>
<h2>📦 Largest Files</h2>
<table><thead><tr><th>Name</th><th>Size</th><th>Type</th><th>Location</th></tr></thead><tbody>{largest_rows}</tbody></table>
<h2>🔄 Duplicate Groups</h2>
<table><thead><tr><th>#</th><th>Files</th><th>Each</th><th>Wasted</th><th>Paths</th></tr></thead><tbody>{dup_rows}</tbody></table>
<div class="footer">Generated by DupeClean v0.1.0</div>
</body></html>"""
