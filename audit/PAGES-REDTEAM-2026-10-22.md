# GoodPaper GitHub Pages 上线审核｜2026-10-22

## 真正的产品定位

静态 GitHub Pages = 免费产品说明 + 安装指南 + 开源项目/作者入口，不是真实论文上传、检查和排版服务；真实计算发生在使用者电脑上通过 \`python app.py serve\` 启动的本机网页中。

## 9 项对抗式验收点

| 编号 | 红队攻击 | 当前应对 |
|---|---|---|
| 01 | 页面像旧式 README，缺少品牌认知 | 大标题、仿纸张版式演示、轻质感卡片、暗色解释区和作者展示 |
| 02 | 用户误以为可以在线上传论文 | 首屏、本地部署与 FAQ 均明确静态展示性质；页面根本没有上传组件 |
| 03 | 假的扫描分数被当成真实准确率 | 预览图标明示例、没有任何真实准确率/检测模型承诺 |
| 04 | 微信导流伤害免费开源信任 | AI 酋长 Andy 官网和微信均可选；开源本身无需联系作者 |
| 05 | Windows 用户按 macOS 命令操作 | 提供 macOS/Linux 和 Windows PowerShell 两组安装命令 |
| 06 | 静态链接/移动端导航失效 | 测试锚点存在和关键链接，增加 580px/820px 响应式规则 |
| 07 | 跨平台浏览器复制失败 | Clipboard API + 文本选中复制 fallback；失败有文本提示 |
| 08 | 推代码就谎称 GitHub Pages 上线 | Pages workflow 必须成功；GitHub Pages 首次启用需仓库设置操作 |
| 09 | 远程部署误暴露论文隐私 | 强调本地仅回环监听，不把标准库开发服务开放公网 |

## 部署验证和局限

- 自动化：\`python -m unittest discover -s tests -p test_pages_landing.py -v\`；部署前在工作流执行。
- GitHub 首次开通：Settings → Pages → Build and deployment → Source: GitHub Actions。此操作没有被写入代码仓库可以代替。
- GitHub Actions 完成并返回真实部署地址前，URL 只是**预计地址**。请以工作流的成功状态为准。
- 尚需 375px 手机、768px 平板、1440px 桌面真实浏览器目视测试，以及用户的实际隐私和咨询数据验证。
- 页面在 Apple 品牌旗下没有任何官方关系或认证；「苹果风」只是审美方向。
