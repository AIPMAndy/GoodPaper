<div align="center">

# GoodPaper

### 论文归论文，格式交给工具。

开源 Word 论文格式检查与基础自动排版工具  
**先检查，再按模板做有限修改，最后人工复核。**

[快速运行](#三五分钟本地启动) · [功能边界](#二目前支持什么) · [安全说明](#五安全与数据保护) · [在线介绍页源码](docs/index.html) · [提交问题](https://github.com/AIPMAndy/GoodPaper/issues)

**作者：[AI 酋长 Andy](https://metaver.vip/) · 微信 AIPMAndy**

</div>

---

写论文最离谱的一件事，就是把大量时间花在格式上。字体、字号、行距、页边距、三线表，一个个调完还要重新检查。GoodPaper 希望把可重复的机械劳动交给工具，把有限的时间留给论文内容和真正的研究。

> **现阶段是 MVP（最小可用版本）**：主要对 **Word 模板的段落样式**、标题/摘要/关键词/图题/表题样式及部分引用编号进行规则检查，可生成一份保留原稿的基础排版副本。不是通用的 Word/PDF 校稿器，不保证论文符合学校/期刊全部要求。

## 一、三分钟本地启动

要求：**Python 3.10–3.12**、Windows/macOS/Linux、可运行的终端，推荐使用虚拟环境。

~~~bash
git clone https://github.com/AIPMAndy/GoodPaper.git
cd GoodPaper
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py serve
~~~

浏览器打开 **http://127.0.0.1:8787**。内置 Web 服务使用 Python 标准库的 \`http.server\`，**不依赖 FastAPI 或 uvicorn**。默认只监听本机，论文文件不会因为启动该服务而自动上传到公有云。

如果只想使用命令行：

~~~bash
python app.py template
python app.py check manuscript.docx
python app.py check manuscript.docx --package demo_template
python app.py check manuscript.docx --template my-university-template.docx
python app.py format manuscript.docx -o manuscript_formatted.docx
python app.py format manuscript.docx -t my-university-template.docx -o formatted.docx
~~~

默认模板来自 \`template_packages/\`，**演示模板不等于你的学校/期刊的官方模板**。优先提供自己有权使用的 .docx 模板，并根据具体投稿要求检查。

## 二、目前支持什么

| 功能 | 当前状态 | 精确说明 |
|---|---|---|
| .docx 单篇检查 | ✅ 已实现 | 对模板样式 ID、标题/摘要/关键词、图表题注段落和文内引用编号做启发式检查 |
| 检查结果/修复建议 | ✅ 已实现 | 报告列出严重程度、问题段落与建议；不代表全量学术合规评分 |
| 基础自动排版 | ✅ 部分实现 | 主要把符合启发式规则的段落映射为模板样式，另存新 .docx |
| 批量检查导出 | ✅ 已实现 | 下载 ZIP，内有 JSON/CSV 汇总；一次最多 10 个文件 |
| 模板包与自备模板 | ✅ 已实现 | 带 manifest 的模板包，或本地上传 .docx Word 文件 |
| 参考文献检查 | 🚧 部分实现 | 主要为编号及引用一致性的有限检测；不是完整 GB/T 7714 引文著录校验 |
| 图片、表格、三线表结构检查 | 🧪 待完善 | 图题/表题样式检查不等于图像分辨率、表格边框和三线表修复 |
| 字号、行距、页边距等全量扫描 | 🧪 待完善 | 当前不能保证覆盖所有段落直接格式、节设置与对象格式 |
| Word 修订差异预览 / PDF | 🧪 待完善 | 需要经过实际文档保真度测试后再开放 |

**警告：自动排版对复杂编号、公式、域代码、交叉引用、图表和页眉页脚的影响尚不能保证为零**。原文应先备份。输出新文件后请在 Word/WPS 中逐页比对；若发现版式异常，请回退使用原件并提交脱敏复现样例。

## 三、最稳妥的使用流程

1. 用 **学校/期刊提供的官方模板副本**作为基准；不清楚模板来源时不要冒用官方认证。
2. 点击「检查论文」，先看报告中的真实问题和段落定位。
3. 只有确认需要基础样式修复时，才选择「自动排版」，始终输出新文件。
4. 重新检查新文件，并在 Word/WPS 中人工确认正文、参考文献、三线表、图片、公式、页眉页脚、目录与页码。
5. 需要批量处理时先用两三份脱敏样例测试，避免在未核验情况下处理整批论文。

## 四、目录与技术架构

~~~text
app.py                          CLI / 本地 Web 启动入口
goodpaper_mvp/
  core.py                       规则检查、样式映射与 DOCX 处理
  server.py                     Python 标准库 HTTP 服务（本机）
  upload_guard.py               上传体积、文件类型及 ZIP 元信息校验
  templates.py                  模板包发现与解析
  licensing.py                  可选私有分发激活机制
  reports.py                    检查报告与批量报告
  static/index.html             苹果风本地 Web 界面
template_packages/              演示样式包（不对应特定学校）
docs/index.html                 静态产品介绍页（不提供上传处理）
tests/                          pytest 回归测试
audit/                           对抗式审查与待验证清单
~~~

技术：Python 3.10–3.12、[python-docx](https://python-docx.readthedocs.io/)、lxml、标准库 HTTP、原生 HTML/CSS/JavaScript。**不需要数据库、不需要第三方登录**。

## 五、安全与数据保护

- 默认仅通过 **127.0.0.1:8787** 访问。本机处理不等于可以安全地对公网开放；请勿把开发服务器直接暴露到互联网。
- Web 输入仅支持 .docx；单文件上限 **20 MiB**、请求体上限 **50 MiB**，批量最多 **10 份**，并校验 ZIP 元数据。它们不能替代恶意文档沙箱。
- 上传文件仅写入本机临时目录，操作完成后由临时目录上下文清理；对临时副本的处理不等于对任何外部备份负责。
- 敏感论文、未公开实验资料和他人作品请遵循所在机构的数据处理要求；不要把真实保密资料提交到公开 Issue。
- 默认开源模式可直接使用；\`config/vendor.example.json\` 用于可选私有分发模式，**它不是免费的功能必须购买邀请码的证据**。
- 更详细威胁模型、保留风险及部署建议请阅读 [SECURITY.md](SECURITY.md)。

## 六、研发路线与贡献

优先级按「防止文档损坏 → 提高检测真实性 → 改善解释性 → 扩充规则」排序。

- [x] CLI、模板包、基础诊断、批量报告、本地 Web
- [x] 修正 CLI \`format\` 参数调用、避免覆盖原论文、保留原文编号定义
- [x] 上传体积/文件数量限制、本地监听边界、高清晰度界面与说明
- [ ] 从实际高校或期刊授权模板中逐项建立字体、字号、行距、页边距基准测试
- [ ] 完整 GB/T 7714 参考文献格式规则，支持人工确认例外
- [ ] 三线表结构、图像分辨率、域代码与交叉引用保护
- [ ] 排版前后差异报告与复杂文档回归样本库
- [ ] 正式产品级认证、运维、日志与访问控制后再评估远程部署

开发者运行：

~~~bash
python -m pip install pytest pytest-cov
python -m pytest tests -q
~~~

[贡献指南](CONTRIBUTING.md) · [报告 Bug](https://github.com/AIPMAndy/GoodPaper/issues/new) · [2026-10-22 对抗式审核](audit/REDTEAM-2026-10-22.md)

## 七、作者与联系

**AI 酋长 Andy** · [个人官网 metaver.vip](https://metaver.vip/) · **微信 AIPMAndy**

GoodPaper 保持免费开源。AI 产品、效率工具落地和职业发展相关的个性化咨询属于可选服务，需事先确认范围与收费；**不影响本项目的免费使用**。

**License：[Apache License 2.0](LICENSE)**。项目与 Word、WPS 或特定学校/期刊没有官方认证或背书关系。
