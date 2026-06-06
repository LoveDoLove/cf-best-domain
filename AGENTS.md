# AGENTS.md

本文件定义 AI Agent（助手）的身份、行为规范与对话启动流程，供每次 Copilot/Assistant 会话开始时读取并恢复状态。

## 身份与行为要点
- 恪守仓库约定与用户偏好，优先查阅 `MEMORY.md` 恢复长期记忆。
- 优先复用本地技能包目录 `.agents/skills/` 中的已安装技能。
- 这个仓库当前的主流程很简单：`fetch_wetest_ips.py` 抓取优选 IP，`update_cloudflare_dns.py` 更新 Cloudflare DNS，GitHub Actions 负责定时自动化。
- 任何自动化改动都要优先考虑稳定、安全、易懂，避免重新引入复杂的抓取逻辑。

## 技能包管理（Skill）
- 技能包存放位置：`.agents/skills/<skill-name>/`。
- 每个技能包须包含主入口 `SKILL.md`，描述能力、用法与来源。
- 强制要求：所有技能包必须是 clone/下载自 GitHub 或其他公开开源仓库，不得仅由本仓库人工编写后声称为“开源技能”。

技能安装建议流程：
1. 在本地目录 `.agents/skills/` 搜索是否已有匹配技能。
2. 若没有，优先在 GitHub 上检索关键词（例如："copilot skill", "agent skill", "AI skill"），选择有明确 LICENSE 的开源仓库。
3. 将该仓库或其子目录 clone 到 `.agents/skills/<skill-name>/`，并保留原始仓库链接与 commit 信息写入 `SKILL.md` 或 `METADATA` 文件中以便审计。

## 会话启动模板
在新开的对话或会话恢复时，请对 Assistant 发送：

```
请读取 AGENTS.md 和 MEMORY.md，恢复你的身份和工作状态，然后继续我们的工作。
```

## 审计与安全
- Skills 必须保留来源信息（仓库 URL、作者、License）。
- 不允许安装或执行未授权的第三方二进制或闭源代码。

## 当前仓库约定
- `WETEST_CF2DNS_KEY` 用于抓取 wetest 的优选 IP。
- `CF_API_TOKEN` 用于更新 Cloudflare DNS。
- `ip.txt` 是两步自动化之间的中间产物，workflow 会先生成它，再更新 DNS。

## 变更记录
- 2026-06-06: 初始版本（由用户请求生成）。
