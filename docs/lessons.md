# 经验教训 (Lessons Learned)

记录所有经过实战验证、对未来开发决策产生深远影响的工程教训。

## 1. wetest.vip 对 GitHub Actions runner 偶发超时

- **现象**：`requests.exceptions.ConnectTimeout: (connect timeout=20)`，CI 失败退出；但前后相邻时段的 cron 均成功，属于偶发瞬态抖动。
- **根因**：云厂商数据中心出口到国内部分 API 链路存在跨境偶发丢包或并发限流。
- **对策**：内置 3 次重试（5s 间隔退避）已充分吸收抖动。**若连续多次彻底失败**，则应排查是否为接口服务商拉黑数据中心 IP 段，切勿盲目加大重试次数。

## 2. 避免在 CI 工作流中硬编码 EOL 的 Python 次版本号

- **现象**：GitHub Actions 定时任务突然失败，报错 `##[error]The version '3.9' with architecture 'x64' was not found for Ubuntu 26.04`。
- **根因**：GitHub 官方将 `ubuntu-latest` 底层系统升级为 Ubuntu 26.04，移除了已过生命周期（EOL）的旧 Python 预编译包。
- **对策**：通用自动化脚本在不需要特定 C-ABI 扩展的前提下，应使用 `python-version: "3.x"`，允许 Actions 直接复用 Runner 镜像预编译并内置缓存的现代 Python 运行时，实现秒级初始化的同时消除 Runner 环境迁移风险。

## 3. 文档漂移是持续性工程风险

- **历史教训**：旧版 README 曾声称支持多来源，但代码中其实早已注释；旧版 AGENTS.md 曾引用已被删除的历史文件。
- **对策**：以当前代码（Source Code）及工作流（Workflow）为唯一事实源（Single Source of Truth）；修改文档时必须逐行与代码交叉核对；废弃概念应明确归档至 `docs/history.md`。

## 4. 重命名必须全局同步所有上下文引用

- **教训**：早期在重命名脚本和 workflow 后，未能及时清理对话知识与历史日志中的陈旧文件名，导致后续 AI Agent 沿用废弃的文件名发起操作而报错。
- **对策**：在 `docs/history.md` 中明确维护废弃与现行文件的全量映射表，主干文档与指引文件一律只使用当前标准命名。

## 5. DNS 变更操作具备破坏性，Guard 必须前置在 Workflow 层

- **教训**：`update_cloudflare_dns.py` 执行时会先清空对应子域名下的所有 A 记录再逐条插入；若 `ip.txt` 因故变为空文件，直接执行将彻底删空解析。
- **对策**：在 CI 流程中硬编码 `[ -s ip.txt ]` 校验，空文件时直接熔断退出。该安全防线不可在重构中被任何形式的修改绕过。
