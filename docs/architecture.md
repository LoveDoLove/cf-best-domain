# 架构设计

## 系统概览

```
wetest.vip API ──fetch_wetest_ips.py──> ip.txt ──update_cloudflare_dns.py──> Cloudflare DNS A 记录
```

两个独立 Python 脚本，通过仓库根目录的 `ip.txt` 进行数据解耦与状态隔离。GitHub Actions 按 `*/30 * * * *` cron 驱动定时自动化流转。

## 核心模块职责

### 1. fetch_wetest_ips.py（IP 采集引擎）

- **数据源定义 (`SOURCES`)**：
  - 格式：`(name, url, key)` 元组列表；
  - 当前启用：`cloudflare` (`https://www.wetest.vip/api/cf2dns/get_cloudflare_ip`)；
  - 保留备用：`cloudfront` 来源已在代码中注释保留。
- **请求配置**：
  - 参数：`key`（从 `WETEST_CF2DNS_KEY` 环境变量获取）+ `type=v4`；
  - 网络策略：`timeout=20s`；内建 3 次循环重试，间隔 5s 退避；
  - 请求头：`User-Agent: cf-best-domain/1.0`。
- **解析与校验**：
  - `walk_values` 递归生成器遍历返回 JSON 的任意深层嵌套结构；
  - `is_ipv4` 基于 Python 标准库 `ipaddress` 过滤合法 IPv4；
  - `extract_ips` 与 `main` 执行集合排重。
- **输出规格**：
  - `ip.txt`，UTF-8 编码，每行一个独立 IPv4 地址；
  - 无密钥时控制台输出 `[skip]` 并优雅跳过，不抛出异常。

### 2. update_cloudflare_dns.py（DNS 智能同步引擎）

- **IP 读取 (`get_ip_list`)**：支持本地相对路径文件或远程 HTTP/HTTPS URL（按行切分与去空白）。
- **Zone 动态探测 (`get_cloudflare_zone`)**：调用 `GET https://api.cloudflare.com/client/v4/zones`，基于 Bearer Token 解析第一个有效区域的 `id` 与 `name`。
- **历史记录清理 (`delete_existing_dns_records`)**：循环拉取目标记录名下现存的所有 A 记录并逐条发送 DELETE 请求，避免旧记录堆积。
- **批量同步写入 (`update_cloudflare_dns`)**：遍历 IP 列表，通过 POST 请求创建新 A 记录（固定 `ttl=1` 自动极速刷新，`proxied=False` 仅 DNS 解析直连）。
- **子域名映射配置 (`subdomain_ip_mapping`)**：字典格式 `{子域名: IP来源}`，当前默认为 `{'api': 'ip.txt'}`。子域名为 `@` 时直接代表根域名。

## Workflows 编排体系 (`.github/workflows/`)

| 工作流文件 | 触发条件 | 执行阶段与职责 |
| --- | --- | --- |
| `collect_ip_list.yml` | cron `*/30 * * * *` + `workflow_dispatch` | 检出完整 Git 历史 (`fetch-depth: 0`) → 环境挂载 (`python-version: "3.x"`) → 校验 `WETEST_CF2DNS_KEY` → 执行 `fetch_wetest_ips.py` → **智能 Commit 压缩**（若上一提交为 bot 自动更新则 soft reset 合并后 `--force-with-lease` 推送，否则正常提交） |
| `update_cloudflare_dns.yml` | cron `*/30 * * * *` + `workflow_dispatch` | 检出代码 → 环境挂载 (`python-version: "3.x"`) → 校验双密钥完整性 → 重新采集 IP → **非空熔断校验** (`[ -s ip.txt ]`，为空立即终止) → 执行 `update_cloudflare_dns.py` 更新 DNS |
| `cleanup-failed-runs.yml` | 手动触发 | 下载并执行 `LoveDoLove/Github-Action-Cleaner` 脚本，批量清理 Actions 失败日志 |
| `cleanup-all-runs.yml` | 手动触发 | 批量清理 Actions 全量历史运行记录 |

## 扩展机制

- **扩展 IP 来源**：在 `fetch_wetest_ips.py` 的 `SOURCES` 列表中追加元组项（需支持 JSON 返回及 key 鉴权）。
- **扩展子域名**：在 `update_cloudflare_dns.py` 的 `subdomain_ip_mapping` 字典中添加键值对。

## 安全与防护边界

- **凭据零落地**：密钥只经 GitHub Secrets 注入环境变量，脚本内无明文。
- **DNS 防误删熔断保护**：在 `update_cloudflare_dns.yml` 中设立 `ip.txt` 非空门禁。脚本自身无空判定，本地运行需由操作者确认。

## Runtime 约束

- **解释器**：Python 3.7+（GitHub Actions workflow 使用 `3.x` 策略自动匹配 Runner 预装缓存）。
- **依赖库**：仅标准库 + `requests`；无 `requirements.txt`。
- **验证原则**：无本地测试框架，以 GitHub Actions 真实环境作为权威验证端。
