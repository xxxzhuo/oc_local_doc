#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫
爬取單板電腦 (SBC) 目录下所有产品的规格书 PDF
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re

# 配置
BASE_URL = "https://www.digikey.com"
SBC_CATEGORY_URL = "https://www.digikey.com/en/products/filter/development-boards-kits-programmers/single-board-computers-sbc/2040"
OUTPUT_DIR = "./digikey_sbc_datasheets"

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_product_urls(category_url):
    """获取 SBC 分类下所有产品页面的 URL"""
    product_urls = []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    page = 1
    while True:
        # 构建分页 URL
        if page == 1:
            url = category_url
        else:
            url = f"{category_url}?page={page}"
        
        print(f"正在爬取第 {page} 页...")
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有产品链接
        products = soup.find_all('a', href=re.compile(r'/en/products/detail/'))
        
        if not products:
            print(f"第 {page} 页没有找到产品，可能已到达最后一页")
            break
        
        for product in products:
            href = product.get('href')
            if href and href not in product_urls:
                full_url = urljoin(BASE_URL, href)
                product_urls.append(full_url)
        
        # 检查是否有下一页
        next_button = soup.find('a', string=re.compile(r'Next|下一頁', re.I))
        if not next_button:
            print("没有更多页面了")
            break
        
        page += 1
        time.sleep(1)  # 礼貌爬取，避免请求过快
    
    return product_urls

def get_datasheet_url(product_url):
    """从产品页面提取规格书 PDF 链接"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(product_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找规格书链接
        datasheet_links = soup.find_all('a', string=re.compile(r'Datasheet|規格書', re.I))
        
        for link in datasheet_links:
            href = link.get('href')
            if href and href.endswith('.pdf'):
                return urljoin(BASE_URL, href)
        
        # 尝试其他可能的选择器
        datasheet_section = soup.find(string=re.compile(r'Datasheet|規格書|Documents', re.I))
        if datasheet_section:
            parent = datasheet_section.find_parent()
            if parent:
                link = parent.find('a', href=re.compile(r'\.pdf$', re.I))
                if link:
                    return urljoin(BASE_URL, link.get('href'))
        
        return None
        
    except Exception as e:
        print(f"  错误：{e}")
        return None

def download_pdf(pdf_url, output_path):
    """下载 PDF 文件"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(pdf_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
        
    except Exception as e:
        print(f"  下载失败：{e}")
        return False

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def main():
    print("=" * 60)
    print("DigiKey SBC 规格书爬虫")
    print("=" * 60)
    
    # 步骤 1: 获取所有产品 URL
    print("\n步骤 1: 获取 SBC 分类下所有产品...")
    product_urls = get_product_urls(SBC_CATEGORY_URL)
    print(f"找到 {len(product_urls)} 个产品")
    
    # 保存产品列表
    with open(f"{OUTPUT_DIR}/product_list.txt", 'w', encoding='utf-8') as f:
        for url in product_urls:
            f.write(url + '\n')
    
    # 步骤 2: 爬取每个产品的规格书
    print(f"\n步骤 2: 爬取规格书 PDF...")
    success_count = 0
    not_found_count = 0
    
    for i, product_url in enumerate(product_urls, 1):
        print(f"\n[{i}/{len(product_urls)}] 处理：{product_url}")
        
        # 提取规格书 URL
        datasheet_url = get_datasheet_url(product_url)
        
        if not datasheet_url:
            print("  ⚠️  未找到规格书")
            not_found_count += 1
            continue
        
        print(f"  ✓ 找到规格书：{datasheet_url}")
        
        # 生成文件名
        # 从 URL 提取产品名称
        product_name = product_url.split('/')[-3]
        product_id = product_url.split('/')[-2]
        filename = f"{sanitize_filename(product_name)}_{product_id}.pdf"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # 检查是否已下载
        if os.path.exists(output_path):
            print(f"  ⚠️  文件已存在，跳过")
            success_count += 1
            continue
        
        # 下载 PDF
        print(f"  下载到：{filename}")
        if download_pdf(datasheet_url, output_path):
            print(f"  ✓ 下载成功")
            success_count += 1
        else:
            print(f"  ✗ 下载失败")
        
        # 保存下载记录
        with open(f"{OUTPUT_DIR}/download_log.txt", 'a', encoding='utf-8') as f:
            f.write(f"{product_name}\t{product_id}\t{datasheet_url}\t{filename}\n")
        
        # 礼貌爬取
        time.sleep(0.5)
    
    # 统计结果
    print("\n" + "=" * 60)
    print("爬取完成!")
    print("=" * 60)
    print(f"总产品数：{len(product_urls)}")
    print(f"成功下载：{success_count}")
    print(f"未找到规格书：{not_found_count}")
    print(f"输出目录：{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
