import requests
from bs4 import BeautifulSoup
import re
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

# 创建一个文件来存储IP地址
with open('ip.txt', 'w') as file:
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
                found_ips = []
                for ip in ip_candidates:
                    if re.match(ip_pattern, ip):
                        file.write(ip + '\n')
                        found_ips.append(ip)
                        print(f"[{url}] Found IP: {ip}")
                if found_ips:
                    print(f"[{url}] All found IPs: {', '.join(found_ips)}")
                continue
            elif url == 'https://api.uouin.com/cloudflare.html':
                # 遍历表格所有行，提取每行第三列的IP（优选IP）
                table = soup.find('table')
                if table:
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        found_ips = []
                        for row in rows:
                            tds = row.find_all('td')
                            if len(tds) >= 3:
                                ip = tds[2].get_text(strip=True)
                                if re.match(ip_pattern, ip):
                                    file.write(ip + '\n')
                                    found_ips.append(ip)
                                    print(f"[{url}] Found IP: {ip}")
                        if found_ips:
                            print(f"[{url}] All found IPs: {', '.join(found_ips)}")
                continue
            elif url == 'https://www.wetest.vip/page/cloudflare/address_v4.html':
                # 优化：直接查找所有 <td data-label="优选地址">，更快
                tds = soup.find_all('td', attrs={'data-label': '优选地址'})
                for td in tds:
                    ip_text = td.get_text(strip=True)
                    ip_candidates = [ip.strip() for ip in ip_text.split(',')]
                    for ip in ip_candidates:
                        if re.match(ip_pattern, ip):
                            file.write(ip + '\n')
                            print(f"[{url}] Found IP: {ip}")
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
                                            file.write(ip + '\n')
                                            print(f"[{url}] Found IP: {ip}")
                continue
            else:
                elements = soup.find_all('li')

            # 遍历所有元素,查找IP地址
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)

                # 如果找到IP地址,则写入文件
                for ip in ip_matches:
                    file.write(ip + '\n')
                    print(f"[{url}] Found IP: {ip}")

        except Exception as e:
            print(f"处理 {url} 时出错：{e}")

print('IP地址已保存到 ip.txt 文件中。')