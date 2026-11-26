# 工程决策记录 (Architecture Decision Records)

每条记录包含决策、理由、备选方案及当前状态。

## 1. 收敛为 wetest 单一来源（2026-06-06）

- **决策**：IP 采集来源从多来源（包括 `api.edgeone.ai/ips` 等）收敛为仅通过 wetest.vip API 获取 Cloudflare 节点。
- **理由**：保证数据源的高稳定性与高可用性；多来源爬虫带来极高的反爬破解与维护成本。
- **备选**：edgeone / 公开文本列表 — 已废弃。
- **状态**：current。**约束**：禁止重新引入复杂的多源网页爬虫逻辑。

## 2. 文件命名与职责统一（2026-06-06）

- **决策**：统一重命名：
  - `collect_ips.py` → `fetch_wetest_ips.py`
  - `bestdomain.py` → `update_cloudflare_dns.py`
  - `caijiip.yml` → `collect_ip_list.yml`
  - `main.yml` → `update_cloudflare_dns.yml`
- **理由**：文件名直观反映业务职责，消除歧义。
- **状态**：current。旧文件记录见 `docs/history.md`。

## 3. Workflow 安全守卫与非空熔断（2026-06-06）

- **决策**：密钥缺失直接让 workflow 报错退出；`update_cloudflare_dns.yml` 在 `ip.txt` 大小为 0 时强制 abort (`exit 1`)。
- **理由**：Cloudflare DNS 删除操作不可逆，空 IP 执行清空将造成线上解析瘫痪。
- **备选**：仅在 Python 脚本内阻断 — 拒绝，在 Workflow 入口阻断更具确定性与可见性。
- **状态**：current，不可移除。

## 4. 自动更新提交压缩策略（2026-06-06）

- **决策**：在 `collect_ip_list.yml` 中，若上一提交为 bot 的 "Automatic update"，则通过 `git reset --soft HEAD~1` 撤销并重新提交，搭配 `--force-with-lease` 推送。
- **理由**：每 30 分钟一次的 cron 会产生巨量提交历史；软重置压缩保证 Git 提交历史整洁且不丢失可追溯性。
- **备选**：每次生成全新提交 — 否决，历史日志污染严重。
- **状态**：current。

## 5. 跨国网络瞬态抖动与线性重试（2026-08-17）

- **决策**：`fetch_wetest_ips.py` 对 `requests.RequestException` 执行 3 次重试，每次间隔 5s。
- **理由**：GitHub Actions 云端 Runner 对国内边缘接口偶发出现 ConnectTimeout（通常为单次偶发）。
- **备选**：urllib3 HTTPAdapter — 否决，代码显式循环更简单直观。
- **状态**：current。

## 6. 记忆体系与文档模块化重构（2026-08-17）

- **决策**：废除散乱的 `MEMORY.md`，知识归拢为 `AGENTS.md`（入口指引）+ `docs/`（主题独立文档）。
- **理由**：杜绝文档内容滞后与漂移，让不同受众拥有独立专用的文档。
- **状态**：current。

## 7. Actions Runner 兼容性与 Python 3.x 策略收敛（2026-11-26）

- **决策**：将所有 GitHub Actions 工作流中的 `actions/setup-python` 版本从硬编码 `"3.9"` 统一收敛为 `"3.x"`，同时将 `actions/checkout` 升级为 `v4`。
- **理由**：GitHub Actions `ubuntu-latest` 升级至 Ubuntu 26.04 环境后，Python 3.9 等 EOL 版本不再预装且缺少预构建包，导致 CI 失败；配置 `"3.x"` 可直接挂载 Runner 预装缓存（如 CPython 3.15.2），零秒启动且免疫操作系统大版本升级破坏。
- **备选**：硬编码 `"3.12"` — 否决，随未来 Runner 升级仍有失效风险，`"3.x"` 对标准库脚本最稳定。
- **状态**：current。
