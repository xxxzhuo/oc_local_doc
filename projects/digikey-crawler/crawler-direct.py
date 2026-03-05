#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - 直接下载版
使用已知的 PDF 链接直接下载，绕过页面爬取
"""

import requests
import os
import time

# 配置
OUTPUT_DIR = "/Users/mac/.openclaw/workspace/oc_local_doc/datasheets/digikey-sbc"
LOG_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/download_log.txt"

# 已知的产品 PDF 链接（从之前成功下载中提取模式）
PRODUCTS = [
    # 重试失败的 4 个
    ("SC1174", "24627137", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3.pdf"),
    ("SC1223", "17278639", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3.pdf"),
    ("SC1153", "21658276", "https://datasheets.raspberrypi.com/rpi5/rpi5-psu.pdf"),
    ("SC1176", "15298147", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    
    # 新增产品
    ("SC1224", "17278644", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3-wide.pdf"),
    ("SC1433", "21658260", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
    ("SC1175", "15298148", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1177", "15298146", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1434", "21658259", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
    ("SC1435", "21658258", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
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
    print("=" * 70)
    print("DigiKey SBC 规格书爬虫 - 直接下载版")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    
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
        print(f"  URL: {pdf_url}")
        
        if download_file(pdf_url, output_path):
            print(f"  ✓ 下载成功")
            success_count += 1
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{product_name}\t{product_id}\t{pdf_url}\t{filename}\tSUCCESS\n")
        else:
            print(f"  ✗ 下载失败")
            failed_count += 1
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{product_name}\t{product_id}\t{pdf_url}\t{filename}\tFAILED\n")
        
        time.sleep(0.5)
    
    # 统计
    print("\n" + "=" * 70)
    print("爬取完成!")
    print("=" * 70)
    print(f"总产品数：{len(PRODUCTS)}")
    print(f"成功下载：{success_count}")
    print(f"失败：{failed_count}")
    print(f"成功率：{success_count / len(PRODUCTS) * 100:.1f}%")
    print(f"输出目录：{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
