#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - 执行版
小批量测试爬取前 20 个产品
"""

import requests
import os
import time
from urllib.parse import urljoin

# 配置
OUTPUT_DIR = "/Users/mac/.openclaw/workspace/oc_local_doc/datasheets/digikey-sbc"
LOG_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/download_log.txt"

# 产品列表（从示例页面提取的前 20 个产品）
PRODUCTS = [
    ("SC1785", "25807415", "https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf"),
    ("SC1432", "21658257", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1791", "25807414", "https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf"),
    ("SC1148", "21658255", "https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf"),
    ("SC1174", "24627137", "https://datasheets.raspberrypi.com/camera/ai-camera-product-brief.pdf"),
    ("SC1431", "21658261", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1113", "25862713", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1223", "17278639", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3-product-brief.pdf"),
    ("SC1153", "21658276", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-power-supply-product-brief.pdf"),
    ("SC1176", "15298147", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-product-brief.pdf"),
]

def download_file(url, save_path):
    """下载文件"""
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
    print("DigiKey SBC 规格书爬虫 - 执行中")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success_count = 0
    not_found_count = 0
    
    for i, (product_name, product_id, pdf_url) in enumerate(PRODUCTS, 1):
        print(f"\n[{i}/{len(PRODUCTS)}] 处理：{product_name} ({product_id})")
        
        filename = f"{product_name}_{product_id}.pdf"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # 检查是否已下载
        if os.path.exists(output_path):
            print(f"  ⚠️  文件已存在，跳过")
            success_count += 1
            continue
        
        # 下载 PDF
        print(f"  下载：{filename}")
        if download_file(pdf_url, output_path):
            print(f"  ✓ 下载成功")
            success_count += 1
            
            # 记录日志
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{product_name}\t{product_id}\t{pdf_url}\t{filename}\tSUCCESS\n")
        else:
            not_found_count += 1
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{product_name}\t{product_id}\t{pdf_url}\t{filename}\tFAILED\n")
        
        time.sleep(0.5)  # 礼貌爬取
    
    # 统计
    print("\n" + "=" * 60)
    print("爬取完成!")
    print("=" * 60)
    print(f"总产品数：{len(PRODUCTS)}")
    print(f"成功下载：{success_count}")
    print(f"失败：{not_found_count}")
    print(f"输出目录：{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
