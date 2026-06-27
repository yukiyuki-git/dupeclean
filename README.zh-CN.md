# DupeClean

<p align="center">
  <strong>🔍 智能磁盘分析与重复文件查找工具，配备现代化 TUI 界面</strong>
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>中文</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/TUI-Textual-purple.svg" alt="Textual TUI">
</p>

DupeClean 是一款快速、现代化的终端工具，用于分析磁盘使用情况和查找重复文件。它将 `ncdu` 的目录导航能力与智能重复检测和精美的交互式 TUI 界面完美结合。

## ✨ 功能特性

- **📊 磁盘使用分析** — 按大小排序的交互式目录树
- **🔍 智能去重** — 多阶段哈希（xxhash → MD5 → SHA256），快速精准检测
- **🗂️ 文件类型统计** — 按文件类型可视化空间分布
- **📦 大文件查找** — 快速识别占用空间的大文件
- **🧹 清理向导** — 安全删除、移动或硬链接重复文件
- **📈 报告导出** — 生成 JSON、CSV 或 HTML 报告
- **⚡ 极速扫描** — 多线程扫描，支持增量更新
- **🖱️ 完整 TUI** — 支持鼠标操作、键盘快捷键和流畅动画

## 📦 安装

```bash
pip install dupeclean
```

或使用 [pipx](https://pypa.github.io/pipx/)（推荐用于 CLI 工具）：

```bash
pipx install dupeclean
```

## 🚀 使用方法

```bash
# 分析当前目录（TUI 模式）
dupeclean

# 分析指定路径
dupeclean /path/to/analyze

# 仅查找重复文件
dupeclean --duplicates /path

# 显示前 20 个最大文件
dupeclean --top 20 /path

# 生成 HTML 报告
dupeclean --report html /path

# CLI 模式（无 TUI）
dupeclean --cli /path

# 快速扫描（仅按大小检测，不哈希）
dupeclean --quick /path

# 启动 REST API 服务
dupeclean --api

# 磁盘健康检查
dupeclean --health /path

# 磁盘空间预测
dupeclean --forecast /path

# 文件熵分析（检测加密/压缩文件）
dupeclean --entropy /path

# 查找相似文件名
dupeclean --fuzzy /path

# 搜索文件
dupeclean --search "*.log" /path
```

### 键盘快捷键

| 按键 | 操作 |
|------|------|
| `↑/↓` 或 `j/k` | 导航 |
| `Enter` | 打开目录 / 选择 |
| `Backspace` | 返回上级 |
| `d` | 切换重复文件视图 |
| `s` | 按大小排序 |
| `n` | 按名称排序 |
| `D` | 标记删除 |
| `x` | 执行清理 |
| `r` | 刷新 |
| `q` | 退出 |
| `?` | 帮助 |

## 🏗️ 项目架构

```
src/dupeclean/
├── cli.py              # CLI 入口
├── scanner.py          # 文件系统扫描器
├── hasher.py           # 多阶段文件哈希器
├── dedup.py            # 重复检测引擎
├── analyzer.py         # 高级分析编排器
├── models.py           # 数据模型
├── report.py           # 报告生成（JSON/CSV/HTML）
├── cleanup.py          # 安全文件清理操作
├── config.py           # 配置管理
├── utils.py            # 工具函数
├── compare.py          # 目录对比
├── entropy.py          # 文件熵分析
├── forecast.py         # 磁盘空间预测
├── fuzzy.py            # 相似文件名检测
├── health.py           # 磁盘健康检查
├── watcher.py          # 目录监控
├── age.py              # 文件年龄分析
├── cache.py            # SQLite 缓存
├── categories.py       # 文件分类
├── checksums.py        # 校验和验证
├── batch.py            # 批量操作
├── benchmark.py        # 性能基准测试
├── suggestions.py      # 智能建议
├── progress.py         # 进度条
├── api.py              # REST API 服务器
└── tui/
    ├── app.py          # 主 Textual 应用
    ├── themes.py       # 颜色主题
    └── screens/
        ├── main.py     # 主仪表盘
        ├── browse.py   # 目录浏览器
        ├── duplicates.py # 重复文件组
        ├── treemap.py  # 树状图可视化
        ├── stats.py    # 统计屏幕
        └── help.py     # 帮助屏幕
```

## ⚙️ 配置

DupeClean 会在以下位置查找配置文件：
- `~/.config/dupeclean/config.toml`（Linux/macOS）
- `%APPDATA%/dupeclean/config.toml`（Windows）

```toml
[scanner]
follow_symlinks = false    # 是否跟随符号链接
skip_hidden = false        # 是否跳过隐藏文件
threads = 4                # 扫描线程数
ignore_patterns = [".git", "node_modules", "__pycache__", ".venv"]

[hasher]
quick_hash_size = 4096     # 快速哈希字节数（第1阶段）
medium_hash_size = 65536   # 中等哈希字节数（第2阶段）
algorithm = "xxhash"       # 哈希算法：xxhash, md5, sha256

[display]
size_format = "binary"     # 大小格式：binary (1024) 或 decimal (1000)
theme = "default"          # 主题：default, dark, monokai, dracula
show_hidden = false        # 是否显示隐藏文件
```

## 🧪 开发

```bash
git clone https://github.com/yukiyuki-git/dupeclean.git
cd dupeclean
pip install -e ".[dev]"
pytest
ruff check src/ tests/
```

## 📋 开发路线

- [x] 核心扫描引擎
- [x] 多阶段去重
- [x] 交互式 TUI
- [x] 报告导出
- [x] 清理向导
- [x] 目录对比
- [x] REST API
- [x] Web 仪表盘
- [x] Shell 自动补全（bash/zsh/fish）
- [x] 磁盘健康检查
- [x] 文件熵分析
- [x] 相似文件名检测
- [ ] 监控模式（实时变更检测）
- [ ] 插件系统
- [ ] 云存储支持（S3、GCS）
- [ ] SQLite 增量扫描缓存

## 📄 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。

## 🙏 致谢

- [Textual](https://textual.textualize.io/) — 现代 TUI 框架
- [Rich](https://rich.readthedocs.io/) — 终端格式化
- [ncdu](https://dev.yorhel.nl/ncdu) — 磁盘使用界面的灵感来源
- [fclones](https://github.com/pkolaczk/fclones) — 去重策略的灵感来源
