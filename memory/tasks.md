# Tasks (跨会话任务追踪)

以下为由 AI 扫描仓库后建议的长期/待办事项，Agent 与用户可跨对话更新状态：

- [ ] 设置 Cloudflare API Token 环境变量（`CF_API_TOKEN`），并在 README 与 CI 中记录获取与权限要求。（优先级：高）
- [ ] 添加 `requirements.txt`（requests, beautifulsoup4）或 `pyproject.toml`，以便明确依赖。（优先级：中）
- [ ] 创建 `memory/YYYY-MM-DD.md` 每日日志模板（已自动生成本次日志）。
- [ ] 不要将敏感信息写入 `memory/` 或 `MEMORY.md`；改为使用 CI/环境变量或加密 Secret。（优先级：高）
- [ ] 如果需要长期保存已安装技能包索引，按 `MEMORY.md` 指南在其中添加 `.agents/skills/` 列表与来源信息。（优先级：低）
- [ ] 可选：添加 `.env.example`（仅占位，不包含真实凭证）并在 README 中说明用法。（优先级：中）

- [x] 将 `https://api.edgeone.ai/ips` 添加为优选来源并在 `collect_ips.py` 中实现对 JSON 返回的支持（2026-06-06）。

变更历史：
- 2026-06-06: 由 AI 扫描仓库并创建初始任务列表。
