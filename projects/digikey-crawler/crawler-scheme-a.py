#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - 方案 A（HTTP 请求 + BeautifulSoup）
优化版：添加重试机制、异常处理、User-Agent
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import re

# 配置
BASE_URL = "https://www.digikey.com"
SBC_CATEGORY_URL = "https://www.digikey.com/en/products/filter/development-boards-kits-programmers/single-board-computers-sbc/2040"
OUTPUT_DIR = "/Users/mac/.openclaw/workspace/oc_local_doc/datasheets/digikey-sbc"
LOG_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/download_log.txt"

# 重试配置
MAX_RETRIES = 3
TIMEOUT = 30
DELAY = 1.5  # 秒

# Session 配置
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
})

def download_file_with_retry(url, save_path, max_retries=MAX_RETRIES):
    """带重试的文件下载"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"    尝试 {attempt}/{max_retries}...")
            response = session.get(url, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except requests.exceptions.SSLError as e:
            print(f"    ⚠️  SSL 错误：{e}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  网络错误：{e}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return False
            
        except Exception as e:
            print(f"    ⚠️  未知错误：{e}")
            return False
    
    return False

def get_product_urls_from_category():
    """从分类页面获取产品 URL"""
    product_urls = []
    
    try:
        print(f"访问分类页面：{SBC_CATEGORY_URL}")
        response = session.get(SBC_CATEGORY_URL, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有产品链接
        product_links = soup.find_all('a', href=re.compile(r'/en/products/detail/'))
        
        for link in product_links:
            href = link.get('href')
            if href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in product_urls:
                    product_urls.append(full_url)
        
        print(f"找到 {len(product_urls)} 个产品")
        return product_urls
        
    except Exception as e:
        print(f"❌ 获取产品列表失败：{e}")
        return []

def get_datasheet_url_from_product(product_url):
    """从产品页面提取规格书 URL"""
    try:
        response = session.get(product_url, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找规格书链接
        datasheet_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        
        for link in datasheet_links:
            href = link.get('href')
            if href:
                # 检查是否是规格书
                parent_text = link.parent.get_text().lower() if link.parent else ''
                if 'datasheet' in parent_text or '规格书' in parent_text or 'document' in parent_text:
                    return urljoin(BASE_URL, href)
        
        # 如果没找到，返回第一个 PDF 链接
        if datasheet_links:
            return urljoin(BASE_URL, datasheet_links[0].get('href'))
        
        return None
        
    except Exception as e:
        print(f"    ❌ 提取失败：{e}")
        return None

def sanitize_filename(name):
    """清理文件名"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def main():
    print("=" * 70)
    print("DigiKey SBC 规格书爬虫 - 方案 A（优化版）")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 步骤 1: 获取产品列表
    print("\n【步骤 1】获取产品列表...")
    product_urls = get_product_urls_from_category()
    
    if not product_urls:
        print("❌ 未找到产品，使用备用产品列表")
        # 备用产品列表（从之前执行中提取）
        product_urls = [
            f"https://www.digikey.com/en/products/detail/raspberry-pi/SC{i}/{id}"
            for i, id in [
                ("1785", "25807415"), ("1432", "21658257"), ("1791", "25807414"),
                ("1148", "21658255"), ("1174", "24627137"), ("1431", "21658261"),
                ("1113", "25862713"), ("1223", "17278639"), ("1153", "21658276"),
                ("1176", "15298147"), ("1224", "17278644"), ("1433", "21658260"),
            ]
        ]
    
    # 步骤 2: 爬取规格书
    print(f"\n【步骤 2】爬取规格书...（共 {len(product_urls)} 个产品）")
    
    success_count = 0
    not_found_count = 0
    failed_count = 0
    
    for i, product_url in enumerate(product_urls[:50], 1):  # 最多爬取 50 个
        print(f"\n[{i}/{min(50, len(product_urls))}] 处理：{product_url}")
        
        try:
            # 提取产品信息
            parts = product_url.rstrip('/').split('/')
            product_name = parts[-3] if len(parts) >= 3 else "unknown"
            product_id = parts[-2] if len(parts) >= 2 else "unknown"
            
            # 获取规格书 URL
            print(f"  提取规格书链接...")
            datasheet_url = get_datasheet_url_from_product(product_url)
            
            if not datasheet_url:
                print(f"  ⚠️  未找到规格书")
                not_found_count += 1
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{product_name}\t{product_id}\t-\t-\tNOT_FOUND\n")
                continue
            
            print(f"  ✓ 找到：{datasheet_url}")
            
            # 生成文件名
            filename = f"{sanitize_filename(product_name)}_{product_id}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            # 检查是否已下载
            if os.path.exists(output_path):
                print(f"  ⚠️  文件已存在，跳过")
                success_count += 1
                continue
            
            # 下载 PDF
            print(f"  下载：{filename}")
            if download_file_with_retry(datasheet_url, output_path):
                print(f"  ✓ 下载成功")
                success_count += 1
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{product_name}\t{product_id}\t{datasheet_url}\t{filename}\tSUCCESS\n")
            else:
                print(f"  ✗ 下载失败")
                failed_count += 1
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{product_name}\t{product_id}\t{datasheet_url}\t{filename}\tFAILED\n")
            
        except Exception as e:
            print(f"  ❌ 错误：{e}")
            failed_count += 1
        
        # 礼貌爬取
        time.sleep(DELAY)
    
    # 统计
    print("\n" + "=" * 70)
    print("爬取完成!")
    print("=" * 70)
    print(f"总产品数：{len(product_urls[:50])}")
    print(f"成功下载：{success_count}")
    print(f"未找到规格书：{not_found_count}")
    print(f"下载失败：{failed_count}")
    print(f"成功率：{success_count / len(product_urls[:50]) * 100:.1f}%")
    print(f"输出目录：{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
