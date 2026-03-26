# GoodPaper

> 学术论文格式检查与自动排版工具

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- 📄 **格式检查**：字体、字号、行距、缩进、页边距等
- 📊 **图表检查**：表格标题、三线表样式、图片分辨率
- 📚 **参考文献**：GB/T 7714 格式校验、引用一致性
- 🔧 **自动排版**：一键修复格式问题
- 🎯 **合规评分**：0-100 分直观反馈
- 🌐 **Web 界面**：可视化报告，支持导出

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 Web 服务

```bash
python app.py serve
# 或
uvicorn goodpaper_mvp.fastapi_server:app --reload
```

访问 http://localhost:8787 使用 Web 界面

### CLI 使用

```bash
# 检查论文格式
python app.py check paper.docx

# 自动排版
python app.py format paper.docx -o output.docx

# 查看可用模板
python app.py template
```

## 📁 项目结构

```
GoodPaper/
├── app.py                      # 主入口 (CLI + Web)
├── goodpaper_mvp/
│   ├── core_cli.py            # 核心检查逻辑
│   ├── severity.py            # 严重等级分层
│   ├── scoring.py             # 合规评分引擎
│   ├── fastapi_server.py      # Web API
│   ├── static/
│   │   └── index.html         # 前端页面
│   └── checkers/              # 检查插件
│       ├── table_checker.py
│       ├── figure_checker.py
│       └── reference_checker.py
├── tests/                     # 单元测试
└── requirements.txt
```

## 🛠️ 技术栈

- **后端**: Python + FastAPI + python-docx
- **前端**: HTML5 + CSS3 + Vanilla JS
- **检查引擎**: 插件化架构，支持扩展

## 📈 开发路线

- [x] Sprint 1: 严重等级分层 + 评分系统 + Web 界面
- [ ] Sprint 2: 图表检查 + 参考文献检查
- [ ] Sprint 3: FastAPI 迁移 + CI/CD
- [ ] Sprint 4: 自动排版增强 + diff 预览
- [ ] Sprint 5: 模板编辑器 + 内置模板

## 🤝 贡献

欢迎 Issue 和 PR！

## 📄 License

MIT License
