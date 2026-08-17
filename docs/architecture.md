# 架构

## 系统概览

```
wetest.vip API ──fetch_wetest_ips.py──> ip.txt ──update_cloudflare_dns.py──> Cloudflare DNS A 记录
```

两个独立脚本，通过仓库根目录的 `ip.txt` 解耦。GitHub Actions 按 `*/30` cron 驱动。

## 模块

### fetch_wetest_ips.py（抓取）

- `SOURCES`：`(name, url, key)` 列表，当前仅 `cloudflare`（`https://www.wetest.vip/api/cf2dns/get_cloudflare_ip`），`cloudfront` 来源已注释保留。
- 请求参数：`key`（来自 `WETEST_CF2DNS_KEY` env）+ `type=v4`；timeout=20s；3 次重试，间隔 5s。
- `walk_values` 递归遍历 JSON 任意层级，`is_ipv4` 过滤，`extract_ips` 去重。
- 输出：`ip.txt`，一行一个 IPv4。
- 无 key 时跳过该来源（打印 `[skip]`），不报错。

### update_cloudflare_dns.py（同步）

- `get_ip_list`：支持本地文件或 http URL（每行一个 IP）。
- `get_cloudflare_zone`：用 `CF_API_TOKEN` 取 token 可见的**第一个** zone。
- `delete_existing_dns_records`：循环删除该子域所有现存 A 记录（防重复）。
- `update_cloudflare_dns`：为每个 IP 创建 A 记录（ttl=1 auto，proxied=false）。
- `subdomain_ip_mapping`：`{子域: IP来源}`，当前仅 `{'api': 'ip.txt'}`。子域为 `@` 时用根域名。
- 异常仅打印 `Error: ...`，不中断其余映射（当前只有一个映射）。

## Workflows（`.github/workflows/`）

| 文件 | 触发 | 作用 |
| --- | --- | --- |
| `collect_ip_list.yml` | cron `*/30` + dispatch | 校验 `WETEST_CF2DNS_KEY` → 跑 fetch → squash 提交 `ip.txt`（若上次提交是 bot 的 "Automatic update" 则 soft reset 后重提交，`--force-with-lease` 推送） |
| `update_cloudflare_dns.yml` | cron `*/30` + dispatch | 校验两个 secret → 跑 fetch → **校验 `ip.txt` 非空**（空则 exit 1，防误删 DNS）→ 跑 update |
| `cleanup-failed-runs.yml` | 手动 | 下载执行 `LoveDoLove/Github-Action-Cleaner` 脚本清理失败运行记录 |
| `cleanup-all-runs.yml` | 手动 | 同上，清理全部运行记录 |

## 扩展点

- 新增 IP 来源：在 `SOURCES` 加一项（需来源 API 支持 key + JSON 返回）。
- 新增子域：在 `subdomain_ip_mapping` 加一项（值可为本地文件或 URL）。

## 安全边界

- 密钥仅经 GitHub Secrets → env；脚本内无硬编码。
- DNS 更新的唯一保护：`update_cloudflare_dns.yml` 的 `ip.txt` 非空 guard。脚本本身无此 guard，本地直接跑 update 脚本需自行注意。

## Runtime 约束

- Python 3.7+；仅 `requests` + stdlib；无 requirements.txt（workflow 内 `pip install requests`）。
- 无测试框架，CI 即验证。