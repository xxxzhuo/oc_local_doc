#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - Playwright 版本
使用浏览器自动化爬取，更可靠
"""

from playwright.sync_api import sync_playwright
import os
import time
import re
from urllib.parse import urljoin
import requests

# 配置
OUTPUT_DIR = "./digikey_sbc_datasheets"
SBC_CATEGORY_URL = "https://www.digikey.tw/zh/products/filter/開發板-套件-編程器/單板電腦-sbc/2040"

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_file(url, save_path):
    """使用 requests 下载文件"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"    ✗ 下载失败：{e}")
        return False

def main():
    print("=" * 60)
    print("DigiKey SBC 规格书爬虫 (Playwright 版本)")
    print("=" * 60)
    
    product_urls = []
    datasheets_downloaded = []
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # 设置超时
        page.set_default_timeout(60000)
        
        print(f"\n访问 SBC 分类页面...")
        try:
            page.goto(SBC_CATEGORY_URL, wait_until='networkidle')
            time.sleep(3)  # 等待页面完全加载
        except Exception as e:
            print(f"页面加载失败：{e}")
            browser.close()
            return
        
        # 提取所有产品链接
        print("提取产品链接...")
        product_links = page.query_selector_all('a[href*="/zh/products/detail/"]')
        
        for link in product_links:
            href = link.get_attribute('href')
            if href and href not in product_urls:
                full_url = urljoin("https://www.digikey.tw", href)
                if full_url not in product_urls:
                    product_urls.append(full_url)
        
        print(f"找到 {len(product_urls)} 个产品")
        
        # 保存产品列表
        with open(f"{OUTPUT_DIR}/product_list.txt", 'w', encoding='utf-8') as f:
            for url in product_urls:
                f.write(url + '\n')
        
        # 访问每个产品页面，提取规格书
        print(f"\n开始爬取规格书...")
        success_count = 0
        not_found_count = 0
        
        for i, product_url in enumerate(product_urls[:10], 1):  # 先测试前 10 个
            print(f"\n[{i}/{min(10, len(product_urls))}] 处理：{product_url}")
            
            try:
                # 访问产品页面
                page.goto(product_url, wait_until='networkidle')
                time.sleep(2)
                
                # 查找规格书链接
                datasheet_link = page.query_selector('a[href*=".pdf"]')
                
                if not datasheet_link:
                    # 尝试其他选择器
                    datasheet_link = page.query_selector('text=规格书') or page.query_selector('text=Datasheet')
                
                if datasheet_link:
                    href = datasheet_link.get_attribute('href')
                    if href and '.pdf' in href:
                        pdf_url = urljoin("https://www.digikey.tw", href)
                        print(f"  ✓ 找到规格书：{pdf_url}")
                        
                        # 提取产品名称
                        product_name = product_url.split('/')[-3]
                        product_id = product_url.split('/')[-2]
                        filename = f"{re.sub(r'[<>:"/\\|?*]', '_', product_name)}_{product_id}.pdf"
                        output_path = os.path.join(OUTPUT_DIR, filename)
                        
                        # 检查是否已下载
                        if os.path.exists(output_path):
                            print(f"  ⚠️  文件已存在，跳过")
                            success_count += 1
                            continue
                        
                        # 下载 PDF
                        print(f"  下载到：{filename}")
                        if download_file(pdf_url, output_path):
                            print(f"  ✓ 下载成功")
                            success_count += 1
                            datasheets_downloaded.append({
                                'product': product_name,
                                'id': product_id,
                                'url': pdf_url,
                                'file': filename
                            })
                        else:
                            not_found_count += 1
                    else:
                        print("  ⚠️  未找到 PDF 链接")
                        not_found_count += 1
                else:
                    print("  ⚠️  未找到规格书")
                    not_found_count += 1
                
            except Exception as e:
                print(f"  ✗ 错误：{e}")
                not_found_count += 1
            
            # 保存下载记录
            with open(f"{OUTPUT_DIR}/download_log.txt", 'a', encoding='utf-8') as f:
                for item in datasheets_downloaded:
                    f.write(f"{item['product']}\t{item['id']}\t{item['url']}\t{item['file']}\n")
            
            time.sleep(1)  # 礼貌爬取
        
        browser.close()
    
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
