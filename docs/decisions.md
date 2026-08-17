# 工程决策

每条记录：决策、理由、备选、状态。

## 1. 收敛为 wetest 单一来源（2026-06-06）

- **决策**：`collect_ips.py` 从多来源（含 `api.edgeone.ai/ips` 等）收敛为仅 wetest.vip 两个 API（cloudflare / cloudfront），后进一步仅启用 cloudflare。
- **理由**：稳定、安全、易懂；多来源带来维护与失败面。
- **备选**：edgeone / 公共 IP 列表 — 已删除（曾短暂加入后移除）。
- **状态**：current。**约束**：禁止重新引入复杂抓取逻辑（AGENTS.md 关键规则）。

## 2. 文件命名统一（2026-06-06）

- **决策**：`collect_ips.py → fetch_wetest_ips.py`、`bestdomain.py → update_cloudflare_dns.py`、`caijiip.yml → collect_ip_list.yml`、`main.yml → update_cloudflare_dns.yml`。
- **理由**：名字反映职责。
- **状态**：current。旧名字仅存在于历史（见 `docs/history.md`）。

## 3. Workflow 安全 guard（2026-06-06）

- **决策**：secret 缺失 → workflow 直接失败；`update_cloudflare_dns.yml` 在 `ip.txt` 为空时 abort。
- **理由**：DNS 删除操作不可逆；空 IP 列表执行 delete 会清空子域 A 记录。
- **备选**：脚本内 guard — 未做，guard 只在 workflow 层。
- **状态**：current，不可轻易移除。

## 4. 自动更新提交 squash 策略（2026-06-06）

- **决策**：`collect_ip_list.yml` 中，若上次提交是 bot 的 "Automatic update"，则 `git reset --soft HEAD~1` 重提交，再 `--force-with-lease` 推送。
- **理由**：避免每次 cron 累积一个提交，保持历史干净；force-with-lease 防止覆盖他人改动。
- **备选**：每次新建提交 — 被否，历史噪音大。
- **状态**：current。

## 5. 抓取重试（2026-08-17）

- **决策**：`fetch_wetest_ips.py` 对 `requests.RequestException` 重试 3 次，间隔 5s。
- **理由**：wetest API 对 GitHub Actions runner 偶发 ConnectTimeout（实测：单次失败，前后运行均成功）。
- **备选**：urllib3 `HTTPAdapter` retry — 未采用，循环更直观。
- **状态**：current。若重试后仍持续失败 → 可能是 wetest 封数据中心 IP，需换来源或换执行环境。

## 6. 记忆体系迁移（2026-08-17）

- **决策**：删除 `MEMORY.md` 与 `old-memory/`，知识重组为 `AGENTS.md`（入口）+ `docs/`（按主题）。
- **理由**：MEMORY.md 已被实现取代且引用失效；旧日志含大量已 superseded 信息，污染 current knowledge。
- **状态**：current。

## Superseded 决策（勿重新实施）

- 多来源抓取（edgeone 等）→ 被决策 1 取代。
- `RemoteDisconnected` 时代的重试策略（total=5, backoff_factor=2, stream=True 备用请求）→ 随 `collect_ips.py` 重写而废弃；现为简单 3 次循环重试。