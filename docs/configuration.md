# 配置与部署指南

本指南详细说明 `cf-best-domain` 的凭据配置、子域名映射扩展及 GitHub Actions 定时自动化部署步骤。

---

## 1. 凭据获取与权限配置

自动化运行需要两个核心密钥，均通过环境变量或 GitHub Actions Secrets 注入，**严禁硬编码进源码或提交到仓库**。

### 1.1 Cloudflare API Token (`CF_API_TOKEN`)
脚本通过 Cloudflare REST API v4 管理目标域名的 A 记录。

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)。
2. 进入右上角 **“我的个人资料” (My Profile) → “API 令牌” (API Tokens)**。
3. 点击 **“创建令牌” (Create Token)**，选择底部的 **“创建自定义令牌” (Create Custom Token)**。
4. 按以下规范配置权限（遵循最小权限原则）：
   - **令牌名称 (Token name)**：例如 `cf-best-domain-dns-sync`
   - **权限 (Permissions)**：
     - `区域 (Zone)` - `DNS` - `编辑 (Edit)`
   - **区域资源 (Zone Resources)**：
     - `包含 (Include)` - `特定区域 (Specific zone)` - 选择你的目标域名（如 `example.com`）
   - **客户端 IP 地址筛选 (Client IP Filtering)**：留空（GitHub Actions Runner IP 随机变动）
   - **TTL (有效期)**：根据个人安全策略设定，或保持默认
5. 点击 **“继续以显示摘要”** 并点击 **“创建令牌”**。
6. **复制并妥善保存生成的 Token**（该 Token 仅显示一次）。

> ⚠️ **安全警告**：切勿使用全局 API 密钥（Global API Key）。自定义令牌具有严格的权限和作用域隔离，更加安全。

### 1.2 wetest 优选接口密钥 (`WETEST_CF2DNS_KEY`)
1. 访问 [wetest.vip](https://www.wetest.vip/) 注册账号。
2. 在个人中心或 API 接口服务页获取你的专属 `key`。
3. 该密钥用于调用 Cloudflare 优选 IP 接口：`https://www.wetest.vip/api/cf2dns/get_cloudflare_ip?key={KEY}&type=v4`。

---

## 2. GitHub Actions 自动化部署

### 2.1 配置仓库 Secrets
1. 在你的 GitHub Fork 仓库中，进入 **Settings** 选项卡。
2. 在左侧菜单中展开 **Secrets and variables**，点击 **Actions**。
3. 点击 **New repository secret** 分别添加以下两条密钥：
   - `CF_API_TOKEN`：填入上述创建的 Cloudflare API Token。
   - `WETEST_CF2DNS_KEY`：填入上述获取的 wetest API Key。

### 2.2 启用与触发工作流
1. 切换至仓库的 **Actions** 选项卡。
2. 若提示工作流处于禁用状态，点击 **"I understand my workflows, go ahead and enable them"**。
3. 在左侧列表中选中 **"Update Cloudflare DNS"**。
4. 点击右侧 **"Run workflow"** 下拉框，选择当前分支并点击绿色按钮手动触发，测试端到端解析更新流程。

---

## 3. 子域名映射自定义 (`subdomain_ip_mapping`)

在 `update_cloudflare_dns.py` 文件中，`subdomain_ip_mapping` 字典控制哪些子域名应该同步哪些 IP 列表：

```python
subdomain_ip_mapping = {
    # 示例 1: 将 api.yourdomain.com 解析为本地抓取的 ip.txt
    'api': 'ip.txt',

    # 示例 2: 将根域名 yourdomain.com 解析为 ip.txt (使用 '@' 代表根域名)
    # '@': 'ip.txt',

    # 示例 3: 为特定业务子域名指定自定义来源 (支持远程 HTTP URL 或本地文件)
    # 'cdn': 'ip.txt',
    # 'bestcf': 'https://example.com/other_ips.txt',
}
```

- **多记录轮询**：若 `ip.txt` 中包含多条 IPv4 地址，脚本会为该子域名批量添加多个 A 记录，DNS 解析器将根据权重或客户端就近进行轮询分配。
- **TTL 设置**：默认创建的 A 记录 `TTL` 设为 `1`（即 Cloudflare 的“自动”TTL），保证节点切换后全网快速生效。
- **代理状态 (Proxied)**：默认创建为仅 DNS 模式（`proxied=False`），直接将流量解析到优选节点，避免走 CDN 二次代理重新产生绕路。

---

## 4. 定时策略调整

工作流默认每 30 分钟定时执行一次：
- `.github/workflows/collect_ip_list.yml`
- `.github/workflows/update_cloudflare_dns.yml`

如需调整频率，修改 workflow 顶部的 cron 表达式即可：

```yaml
on:
  schedule:
    - cron: "*/30 * * * *"  # 每 30 分钟一次 (UTC)
    # - cron: "0 * * * *"   # 每小时整点执行一次
    # - cron: "0 */2 * * *" # 每 2 小时执行一次
```

---

## 5. 故障排查 (Troubleshooting)

| 错误表现 | 常见原因 | 解决方案 |
| --- | --- | --- |
| `Missing secret: WETEST_CF2DNS_KEY` | 仓库 Secrets 遗漏或拼写错误 | 检查 GitHub Actions Secrets 名称是否准确无误 |
| `Error: No zones found` | `CF_API_TOKEN` 权限不足或作用域错误 | 检查 Token 是否勾选了对应域名的 Zone 权限 |
| `ip.txt is empty; aborting...` | wetest 接口返回空数据或 key 过期 | 检查 wetest 账号状态与网络，熔断机制已成功阻止错误清空 DNS |
| `[retry] cloudflare: attempt 1 failed` | CI 节点跨国网络瞬态超时 | 正常现象，内置 3 次重试机制会自动吸收偶发超时 |
