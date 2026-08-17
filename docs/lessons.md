# Lessons Learned

只有对未来工程决策有影响的教训。

## 1. wetest.vip 对 GitHub Actions runner 偶发超时

- **现象**：`requests.exceptions.ConnectTimeout`（connect timeout=20），job 失败 exit 1；前后 cron 运行均成功 → transient。
- **根因**：wetest.vip 从 GH Actions 数据中心 IP 不稳定（可能限流/防火墙）。
- **对策**：3 次重试 + 5s 间隔已吸收。**若持续失败**，大概率是 wetest 封数据中心 IP → 不要盲目加重试，考虑换来源或换执行环境。
- **验证方法**：查 Actions run 历史判断是一次性还是持续性，再决定修复方向。

## 2. 验证依赖 CI，本地不可靠

- 本机（Windows）未安装 Python → 无法 `py_compile` / 本地跑脚本；语法验证需靠 CI 或远程环境。
- **对策**：改动脚本后至少 `python -m py_compile`；无本地 Python 时明确告知用户验证靠 CI。

## 3. 文档漂移是持续风险

- 历史证据：README 曾声称"两个 wetest API"，代码实际只启用 cloudflare；AGENTS.md 曾引用已删除的 MEMORY.md；旧日志描述已重命名的文件。
- **对策**：以 source code / workflow 为唯一事实源；改文档必须与实现交叉核对；过时信息移入 `docs/history.md` 而不是删除时不留痕。

## 4. 重命名/重构要同步所有引用

- 2026-06-06 重命名脚本与 workflow 后，旧日志/记忆长期保留旧文件名，误导后续 Agent。
- **对策**：历史文件记录 superseded 映射（见 `docs/history.md`），current 文档永远用当前名字。

## 5. DNS 操作不可逆，guard 必须在 workflow 层

- `update_cloudflare_dns.py` 本身无空列表 guard；安全全靠 `update_cloudflare_dns.yml` 的 `ip.txt` 非空检查。
- **对策**：改 workflow 时不要破坏该 guard；本地跑 update 脚本需自行注意（AGENTS.md 已警告）。