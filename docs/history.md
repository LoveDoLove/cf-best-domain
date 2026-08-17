# 历史与已废弃信息

本文件只用于追溯；当前实现以代码 + `AGENTS.md` 为准。以下内容均已 superseded，勿据其操作。

## 时间线

- `Initial commit` → 版本迭代 `1.0.0` … `1.1.1`（2026-06 前，纯版本号提交，无决策价值）。
- **2026-06-06 大重构**：多来源 → wetest-only；脚本/工作流重命名；加 secret 校验与空 `ip.txt` guard；加 squash 提交策略（详见 `docs/decisions.md`）。
- **2026-08-17**：`fetch_wetest_ips.py` 加重试（ConnectTimeout 教训，见 `docs/lessons.md`）；记忆体系重建（AGENTS.md + docs/）。

## Superseded 文件映射

| 旧名（已废弃） | 当前名 |
| --- | --- |
| `collect_ips.py` | `fetch_wetest_ips.py` |
| `bestdomain.py` | `update_cloudflare_dns.py` |
| `.github/workflows/caijiip.yml` | `.github/workflows/collect_ip_list.yml` |
| `.github/workflows/main.yml` | `.github/workflows/update_cloudflare_dns.yml` |
| `MEMORY.md` | 删除（2026-08-17，知识并入 `docs/`） |
| `memory/`（每日日志） | 删除（2026-08-17，内容并入本文档） |

## Superseded 方案

- 多来源抓取：曾加入 `https://api.edgeone.ai/ips`，后移除；被 wetest-only 取代。
- 旧重试策略：`RemoteDisconnected` 时代 `urllib3` retry（total=5, backoff_factor=2）+ 备用请求（长超时、stream=True、Connection: close）；随 `collect_ips.py` 重写废弃，现为 3 次循环重试。
- 环境变量曾支持多个 key 名（`WETEST_CF2DNS_KEY` / `CF2DNS_KEY` / `WETEST_KEY`）→ 现在只认 `WETEST_CF2DNS_KEY`。

## 未完成的历史建议（未实施，保留供参考）

- 添加 `requirements.txt` / `.env.example`（2026-06-06 建议；项目刻意无 requirements.txt，CI 直接 `pip install requests`）。
- 建立 `.agents/skills/` 本地技能包目录（仓库从未存在该目录；技能管理约定见 AGENTS.md）。
- 添加 Cloudflare 优选 IP 来源替代方案（如 hostmonit API）— 未实施，若 wetest 长期不可达可评估。