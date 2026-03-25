<div align="center">

# 📄 GoodPaper

**Open-source paper formatting helper for `.docx` / `.docm` manuscripts.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/AIPMAndy/GoodPaper?style=social)](https://github.com/AIPMAndy/GoodPaper/stargazers)

**Check → Format → Re-check** your academic papers in one command.

[Quick Start](#quick-start) • [CLI Examples](#cli-examples) • [Web UI](#web-ui-features) • [Template Packages](#template-packages)

</div>

---

## 🆚 Why GoodPaper?

| Feature | Manual Formatting | LaTeX | **GoodPaper** |
|---------|:-----------------:|:-----:|:-------------:|
| Learning Curve | ⚠️ Medium | ❌ Steep | ✅ **Zero** |
| Template Compliance | ❌ Manual check | ✅ Good | ✅ **Automated** |
| Batch Processing | ❌ One by one | ⚠️ Script needed | ✅ **Built-in** |
| Word Compatibility | ✅ Native | ❌ Export needed | ✅ **Native** |
| First-pass Auto-fix | ❌ Manual | ❌ Manual | ✅ **Automatic** |
| Structured Reports | ❌ None | ⚠️ Log files | ✅ **JSON/CSV** |
| **100% Free & Open** | - | - | ✅ **Yes** |

**GoodPaper** is the only tool that combines **Word-native workflow** with **automated formatting compliance checking** — no LaTeX learning curve, no manual checking.

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Clone & install
git clone https://github.com/AIPMAndy/GoodPaper.git
cd GoodPaper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Check a paper
python3 app.py check --paper mypaper.docx --package example_template

# 3. Auto-format
python3 app.py format --paper mypaper.docx --output fixed.docx --package example_template
```

---

## ✨ What GoodPaper Can Do

### 📋 Check Paper Format
Detect mismatches between your manuscript and target template:
- Title / Author / Abstract formatting
- Heading levels (H1, H2)
- Table & figure captions
- References style
- First paragraph after headings

### 🔧 Auto-Format
Generate first-pass formatted `.docx` with one command:
- Applies correct styles automatically
- Preserves your content
- Ready for manual polish

### 📊 Batch Processing
Check entire folders of papers:
- Export structured reports (JSON/CSV)
- Perfect for labs, courses, editorial workflows
- Identify common issues across submissions

### 🌐 Web UI
Local web interface at `http://127.0.0.1:8765`:
- Upload template & manuscript
- Visual check results
- Download formatted papers
- Batch report ZIP download

---

## 📖 CLI Examples

### List Available Templates
```bash
python3 app.py list-packages
```

### Check Single Paper
```bash
python3 app.py check \
  --paper path/to/paper.docx \
  --template path/to/template.docm
```

### Check & Format in One Step
```bash
python3 app.py check-and-format \
  --paper path/to/paper.docx \
  --output outputs/paper-formatted.docx \
  --template path/to/template.docm
```

### Batch Check Folder
```bash
python3 app.py batch-check \
  --input-dir path/to/folder \
  --output-dir outputs/batch-report \
  --template path/to/template.docm
```

---

## 🎯 Use Cases

- **Conference/Journal Submission** - Check compliance before upload
- **Teaching & Labs** - Batch-review student papers
- **Editorial Workflows** - First-pass formatting automation
- **Template Migration** - Convert papers between templates

---

## 🏗️ Architecture

```
GoodPaper/
├── goodpaper_mvp/          # Core library
│   ├── core.py             # Document analysis & formatting
│   ├── templates.py        # Template package management
│   ├── reports.py          # Batch report generation
│   ├── server.py           # Web UI server
│   └── licensing.py        # Optional activation
├── template_packages/      # Template definitions
│   ├── example_template/   # Example academic template
│   ├── example_academic/   # Another example
│   └── demo_template/      # Demo template
├── app.py                  # CLI entry point
└── requirements.txt        # Dependencies
```

---

## 📝 Template Packages

Define reusable template packages under `template_packages/`:

```json
{
  "package_id": "my_conference",
  "name": "My Conference Template",
  "template_file": "template.docm",
  "default": true,
  "semantic_styles": {
    "title": "papertitle",
    "author": "author",
    "abstract": "abstract",
    "heading_1": "heading1",
    "heading_2": "heading2"
  }
}
```

---

## 🚧 Roadmap

- [x] Core document analysis
- [x] Auto-formatting engine
- [x] CLI interface
- [x] Web UI
- [x] Batch processing
- [ ] More publisher templates
- [ ] Plugin system for custom rules
- [ ] CI/CD integration
- [ ] Docker support

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache 2.0 — free to use, modify, and distribute.

---

<div align="center">

**If GoodPaper helps your research, please give us a ⭐ Star!**

[![Star History Chart](https://api.star-history.com/svg?repos=AIPMAndy/GoodPaper&type=Date)](https://star-history.com/#AIPMAndy/GoodPaper&Date)

</div>
