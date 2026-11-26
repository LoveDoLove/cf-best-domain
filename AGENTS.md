# AGENTS.md

本文件是面向 AI Coding Agent 的第一入口与工程操作指引。保持高信息密度，不要把详细文档直接内嵌于此；详细知识按需查阅 `docs/` 目录下的独立文件。

## 1. 项目定位与核心原则

- **项目身份**：`cf-best-domain` — 自动化抓取 Cloudflare 优选 IP 并同步至 Cloudflare DNS A 记录的极简 Python 自动化工具。
- **以代码为准**：文档与源码出现分歧时，**以当前源码（`*.py`）与工作流（`*.yml`）的实现为绝对事实源**，并同步纠正文档。
- **极简主义约束**：保持简单与稳定。**严禁重新引入复杂的多源网页爬虫、代理池、第三方重型数据库或依赖框架**。
- **安全红线**：密钥（`CF_API_TOKEN`、`WETEST_CF2DNS_KEY`）仅通过环境变量与 GitHub Secrets 传递，**绝不硬编码入代码、日志或提交中**。
- **熔断完整性**：`update_cloudflare_dns.yml` 中的 `[ -s ip.txt ]` 非空门禁是防止线上 DNS 记录被意外清空的核心防线，**严禁弱化或移除**。

## 2. 架构拓扑速查

```
wetest.vip API ──fetch_wetest_ips.py──> ip.txt ──update_cloudflare_dns.py──> Cloudflare DNS A 记录
```

- `fetch_wetest_ips.py`：从 wetest.vip 获取 Cloudflare 优选 IPv4 → 递归提取与校验 → 排重 → 写入 `ip.txt`。
- `update_cloudflare_dns.py`：从 `ip.txt` 读取 IP → 基于 Token 发现 Zone → 循环清理旧 A 记录 → 批量写入新 A 记录（`TTL=1`，`proxied=False`）。
- `ip.txt`：中间状态解耦载体，由 Git 跟踪版本。

## 3. Runtime 规范与运行约束

- **Python 运行时**：Python 3.7+（GitHub Actions 统一配置 `python-version: "3.x"`）。
- **依赖管理**：仅依赖 Python 标准库及 `requests`，无 `requirements.txt`（CI 中执行 `pip install requests`）。
- **测试与验证**：无本地单元测试框架。改动脚本后执行 `python -m py_compile <file.py>` 验证语法，业务行为以 GitHub Actions CI 真实运行结果为准。

## 4. 详细知识索引地图

在执行深度任务时，请根据以下主题索引精准查阅 `docs/` 目录下的专门文档：

| 关注主题 | 文档路径 | 核心内容 |
| --- | --- | --- |
| **技术白皮书 (EN)** | [`docs/whitepaper.md`](docs/whitepaper.md) | 英文架构白皮书、Anycast 路由优化理论、系统拓扑、安全模型与演进规划 |
| **技术白皮书 (中文)** | [`docs/whitepaper_zh.md`](docs/whitepaper_zh.md) | 完整双语技术白皮书：路由机理、系统拓扑、安全模型与演进规划 |
| **系统架构与数据流** | [`docs/architecture.md`](docs/architecture.md) | 模块切分、详细请求参数、异常重试逻辑、工作流触发机制 |
| **工程决策记录 (ADR)** | [`docs/decisions.md`](docs/decisions.md) | 架构演进决策（单一数据源、Squash 提交、Runner 兼容策略等） |
| **经验教训与避坑** | [`docs/lessons.md`](docs/lessons.md) | 跨国网络超时、Runner 镜像升级与 EOL Python、文档漂移防范 |
| **配置与部署指南** | [`docs/configuration.md`](docs/configuration.md) | Cloudflare Token 权限配置、wetest 密钥获取、子域名映射扩展配置 |
| **历史与已废弃信息** | [`docs/history.md`](docs/history.md) | 旧文件名映射表、已淘汰方案列表（避免重复走弯路） |

## 5. 变更与提交规范

1. **改动脚本**：必须通过 `python -m py_compile` 验证语法，严禁引入未经批准的第三方重型依赖。
2. **改动工作流**：核对密钥名称、非空熔断守卫、提交 squash 逻辑是否完整。
3. **改动文档**：必须中英文（`README.md` & `README_zh.md`、`whitepaper.md` & `whitepaper_zh.md`）对照检查，防止信息不对称。
