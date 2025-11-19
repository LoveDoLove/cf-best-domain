import requests
from bs4 import BeautifulSoup
import re
import ipaddress
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    # 'https://cf.090227.xyz',
    'https://api.uouin.com/cloudflare.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://stock.hostmonit.com/CloudFlareYes'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 收集所有IP用于去重和验证(保留发现顺序)
found_ips = []
found_ips_set = set()

def _normalize_ip(ip_str: str) -> str:
    """清除提取到的IP地址字符串两端常见的标点和空白字符。"""
    if not ip_str:
        return ip_str
    return ip_str.strip().strip(',;()[]')

def _add_ip(ip_str: str, source: str) -> bool:
    """验证IP并添加到有序唯一列表中。

    返回值: 如果IP被成功添加(即未重复且为IPv4)返回True，否则返回False。
    """
    ip_str = _normalize_ip(ip_str)
    try:
        # 使用ipaddress验证IP是否合法(IPv4/IPv6)，但我们只接受IPv4
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.version != 4:
            # 忽略IPv6地址
            return
    except Exception:
        return

    if ip_str not in found_ips_set:
        found_ips.append(ip_str)
        found_ips_set.add(ip_str)
        print(f"[{source}] Found IP: {ip_str}")
        return True
    return False

for url in urls:
        print(f"Processing {url} ...")
        try:
            # 发送HTTP请求获取网页内容
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 根据网站的不同结构找到包含IP地址的元素
            if url == 'https://ip.164746.xyz/ipTop10.html':
                # 该页面直接返回逗号分隔的IP字符串，无需解析HTML
                ip_candidates = [ip.strip() for ip in response.text.split(',')]
                local_found = []
                for ip in ip_candidates:
                    if re.match(ip_pattern, ip):
                        if _add_ip(ip, url):
                            local_found.append(ip)
                if local_found:
                    print(f"[{url}] All found IPs: {', '.join(local_found)}")
                continue
            elif url == 'https://api.uouin.com/cloudflare.html':
                # 该页面的IP以文本表格形式出现，直接用正则提取所有IPv4
                ip_matches = re.findall(ip_pattern, response.text)
                local_found = []
                for ip in ip_matches:
                    if _add_ip(ip, url):
                        local_found.append(ip)
                if local_found:
                    print(f"[{url}] All found IPs: {', '.join(local_found)}")
                else:
                    print(f"[{url}] No valid IPs found in response text.")
                continue
            elif url == 'https://www.wetest.vip/page/cloudflare/address_v4.html':
                # 优化：直接查找所有 <td data-label="优选地址">，更快
                tds = soup.find_all('td', attrs={'data-label': '优选地址'})
                for td in tds:
                    ip_text = td.get_text(strip=True)
                    ip_candidates = [ip.strip() for ip in ip_text.split(',')]
                    for ip in ip_candidates:
                        if re.match(ip_pattern, ip):
                            _add_ip(ip, url)
                continue
            elif url == 'https://stock.hostmonit.com/CloudFlareYes':
                # 直接查找表格并提取<tr>的第二列<div class='cell'>内容
                table = soup.find('table')
                if table:
                    tbody = table.find('tbody')
                    if tbody:
                        first_row = tbody.find('tr')
                        if first_row:
                            tds = first_row.find_all('td')
                            if len(tds) >= 2:
                                cell_div = tds[1].find('div', class_='cell')
                                if cell_div:
                                    ip_text = cell_div.get_text(strip=True)
                                    ip_candidates = [ip.strip() for ip in ip_text.split(',')]
                                    for ip in ip_candidates:
                                        if re.match(ip_pattern, ip):
                                            _add_ip(ip, url)
                continue
            else:
                elements = soup.find_all('li')

            # 遍历所有元素,查找IP地址
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)

                # 如果找到IP地址,则写入文件
                for ip in ip_matches:
                    _add_ip(ip, url)

        except Exception as e:
            print(f"处理 {url} 时出错：{e}")

# 将去重后的IP写入文件
with open('ip.txt', 'w', encoding='utf-8') as file:
    for ip in found_ips:
        file.write(ip + '\n')

print(f"共发现 {len(found_ips)} 个唯一IPv4地址，已保存到 ip.txt 文件中。")