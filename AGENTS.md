# AGENTS.md

本文件是 AI Agent 的快速入口。详细知识按需 follow 下方链接，不要全量读取。

## 项目身份

`cf-best-domain`：自动抓取 Cloudflare 优选 IP 并同步到 Cloudflare DNS A 记录的小型 Python 工具。两个脚本 + GitHub Actions 定时任务，无框架、无测试、无 requirements.txt（唯一依赖 `requests`，CI 内直接 `pip install requests`）。

## 关键规则

- **以代码为准**：文档与实现冲突时，以当前 source code / workflow 为准，并修正文档。
- **保持简单**：任何自动化改动优先考虑稳定、安全、易懂；禁止重新引入复杂抓取逻辑（多来源、爬虫、代理、反爬）。
- **安全**：密钥只经环境变量 / GitHub Secrets（`WETEST_CF2DNS_KEY`、`CF_API_TOKEN`），绝不写入仓库；`ip.txt` 为空时禁止执行 DNS 更新（防误删记录）。

## 当前架构（极简摘要）

```
wetest.vip API ──fetch_wetest_ips.py──> ip.txt ──update_cloudflare_dns.py──> Cloudflare DNS A 记录
```

- `fetch_wetest_ips.py`：从 wetest.vip API 抓优选 IPv4 → 去重 → 写 `ip.txt`。来源在 `SOURCES`（当前仅 cloudflare，cloudfront 已注释），key 用 `WETEST_CF2DNS_KEY`。带 3 次重试（5s 间隔）。
- `update_cloudflare_dns.py`：读 `ip.txt` → 取 token 第一个 zone → 删除并重建 `subdomain_ip_mapping` 中各子域的 A 记录（当前仅 `api`）。key 用 `CF_API_TOKEN`。
- `ip.txt`：中间产物，提交在仓库根目录。
- Workflows（全部 `*/30` cron）：
  - `collect_ip_list.yml`：抓取 + 提交（squash 自动更新提交）
  - `update_cloudflare_dns.yml`：抓取 + 校验 `ip.txt` 非空 + 更新 DNS
  - `cleanup-failed-runs.yml` / `cleanup-all-runs.yml`：手动触发，清理 Actions 运行记录（下载外部脚本执行）

## 约束

- Python 3.7+（workflow 用 3.9 / 3.x）；仅依赖 `requests` + stdlib。
- 无本地测试；CI 即验证。改动脚本后至少 `python -m py_compile` 或本地跑一次。
- wetest API 从 GitHub Actions runner 偶发连接超时（已加重试吸收；若持续失败，可能是 wetest 封数据中心 IP）。

## 验证要求

1. 改动脚本 → 语法/运行验证（本地或 CI）。
2. 改动 workflow → 核对 secret 校验、`ip.txt` 非空 guard、提交策略不被破坏。
3. 改动文档 → 与实现交叉核对，避免漂移。

## 详细知识

| 主题 | 位置 |
| --- | --- |
| 架构 / 数据流 / 扩展点 | `docs/architecture.md` |
| 工程决策与 rationale | `docs/decisions.md` |
| Lessons learned | `docs/lessons.md` |
| 历史 / 已废弃信息 | `docs/history.md` |

## 变更记录

- 2026-08-17：重建为入口文档；详细内容移入 `docs/`；移除已删除的 `MEMORY.md` 引用。