# GoodPaper

GoodPaper 是一个面向论文作者的开源排版辅助工具。

它解决的不是“帮你写论文”，而是更具体的一件事：
**拿着目标模板，对现有稿件做格式检查、初步排版修复、批量出报告。**

当前项目更适合这些场景：
- 会议 / 期刊投稿前的格式自查
- 学生论文或实验室稿件的模板合规检查
- 教师、助教、编辑做批量格式巡检
- 基于已有出版社模板做第一轮自动排版

## 当前能力

- 上传 `.docx` / `.docm` 模板做检查
- 检查论文稿件与模板语义样式是否匹配
- 自动识别并处理这些常见结构：
  - title
  - author
  - affiliation / address
  - abstract
  - keywords
  - heading level 1 / 2
  - first paragraph after heading
  - table caption
  - figure caption
  - displayed equation
  - references heading and reference items
- 生成基础自动排版结果（`.docx`）
- 批量检查并导出报告（JSON / CSV / ZIP）
- 本地 Web UI
- CLI

## 开源版说明

这个仓库现在默认是 **开源可用版**：
- 默认不强制激活
- 不内置商业 secret
- 不提交本地设备、license、运行产物
- 不内置第三方模板文件

也就是说：
**别人 clone 下来后，可以直接运行；如果要用具体模板，需要自己上传模板文件。**

## 为什么不内置模板文件？

很多出版社 / 会议模板（例如某些 `.docm` / `.dotm` 模板）本身可能有分发限制。
为了避免版权和再分发风险，开源仓库默认不直接附带第三方模板。

你可以用两种方式使用 GoodPaper：
1. **直接上传你自己的模板文件**（推荐）
2. 在 `template_packages/` 下面自己配置模板包

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 启动 Web UI

```bash
python3 app.py serve
```

打开：

```bash
http://127.0.0.1:8765
```

## CLI 用法

### 查看模板包

```bash
python3 app.py list-packages
```

如果仓库里没有可用模板包，可以直接在下面命令里传 `--template`。

### 检查论文

```bash
python3 app.py check --paper path/to/paper.docx --template path/to/template.docm
```

### 自动排版

```bash
python3 app.py format \
  --paper path/to/paper.docx \
  --output outputs/paper-formatted.docx \
  --template path/to/template.docm
```

### 检查并修复

```bash
python3 app.py check-and-format \
  --paper path/to/paper.docx \
  --output outputs/paper-formatted.docx \
  --template path/to/template.docm
```

### 批量检查

```bash
python3 app.py batch-check \
  --input-dir path/to/folder \
  --output-dir outputs/batch-report \
  --template path/to/template.docm
```

## 模板包

如果你想做内置模板包，可以参考：

```text
template_packages/
  your_package/
    manifest.json
```

manifest 示例：

```json
{
  "package_id": "your_template",
  "name": "Your Template",
  "description": "Your local template package.",
  "version": "0.1.0",
  "default": true,
  "template_file": "../../path/to/your-template.docm",
  "semantic_styles": {
    "title": "papertitle",
    "author": "author",
    "address": "address",
    "abstract": "abstract",
    "keywords": "keywords",
    "heading_1": "heading1",
    "heading_2": "heading2",
    "first_paragraph": "p1a",
    "table_caption": "tablecaption",
    "figure_caption": "figurecaption",
    "equation": "equation",
    "references": "referenceitem"
  }
}
```

## 项目现状

当前仍然是一个 **MVP / Beta**，优点是方向清楚、能本地跑、功能闭环已经成型；
但它还不是一个成熟的“论文排版平台”。

还可以继续补的方向包括：
- 单元测试
- 更稳定的 DOCX / DOCM 边界处理
- 更多出版社 / 会议模板适配
- 更细的段落级修复建议
- UI 体验优化
- 插件化模板包系统

## 商业化 / 私有分发

仓库里保留了可选的激活能力代码，方便你后续做私有部署或商业分发。
但在当前开源版里，默认是关闭强制激活的。

如果你要启用私有分发：
- 自己准备 `config/vendor.json`
- 或设置环境变量 `GOODPAPER_VENDOR_SECRET`
- 并在部署环境里设置 `GOODPAPER_REQUIRE_ACTIVATION=1`

## License

MIT
