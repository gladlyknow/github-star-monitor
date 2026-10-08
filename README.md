# GitHub Star Monitor — 中文 SaaS 热点情报

每日 01:15 UTC（北京时间 09:15）通过 GitHub Actions 收集 GitHub 仓库 Star 快照，生成 `reports/YYYY-MM-DD.md` 中文 SaaS 商业机会日报，可选通过 SMTP 发送邮件。

## 运行
- Actions → Daily GitHub Star Monitor → Run workflow。
- 首日没有 24 小时对比基线，显示“无可比历史”，不伪造增长。
- 日报中文介绍通过可选 `OPENAI_API_KEY` 翻译；未配置时保留英文原文并标注“尚未翻译”。
- SaaS 方向、客户、定价和评分均为启发式探索，不代表经过验证的商业机会。

## 邮件配置：Gmail
在仓库 **Settings → Secrets and variables → Actions → New repository secret** 添加：

| Secret | Value |
| --- | --- |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | 发送邮件的 Gmail 地址 |
| `SMTP_PASSWORD` | Gmail 两步验证后生成的应用专用密码（不是账号登录密码） |
| `REPORT_EMAIL_TO` | `gladlyknow@gmail.com` |
| `OPENAI_API_KEY` | 可选，启用中文 AI 翻译 |

**不要把密钥写入代码、提交记录或聊天。** 如果未配置 SMTP 相关 Secret，邮件步骤会跳过并提示，不影响日报生成。邮件仅在 SMTP 服务接受消息后才视为已提交发送，收件箱最终投递取决于邮件服务。

## 限制
- 候选仓库来源是最近 7 天创建的高 Star 仓库，并非完整 GitHub Trending；可能漏掉老项目突然爆红的情况。
- 增长量为间隔 20–28 小时的两次快照差值，不是精确滚动 24h。
- 当日重复触发不会覆盖快照，但会重新生成日报，并可能重复发送邮件。
- 不建议在未验证客户需求前直接以初筛评分作为投资或开发决策。
