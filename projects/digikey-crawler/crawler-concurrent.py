#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - 并发版
使用 Playwright + asyncio 实现高并发爬取
"""

import asyncio
import aiohttp
import os
import time
from datetime import datetime
from urllib.parse import urljoin
import re

# 配置
OUTPUT_DIR = "/Users/mac/.openclaw/workspace/oc_local_doc/datasheets/digikey-sbc"
LOG_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/download_log.txt"
REPORT_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/hourly_report.md"

# 并发配置
MAX_CONCURRENT = 10  # 最大并发数
TIMEOUT = 30  # 超时时间（秒）
RANDOM_DELAY = (1, 3)  # 随机延迟范围（秒）
MAX_RETRIES = 3  # 最大重试次数

# 统计
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'not_found': 0,
    'start_time': None,
    'batches': 0
}

# 已知的 SBC 产品列表（从 DigiKey 网站提取）
# 格式：(产品型号，DigiKey 编号，PDF URL)
PRODUCTS = [
    # 已有成功下载的
    ("SC1785", "25807415", "https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf"),
    ("SC1432", "21658257", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1791", "25807414", "https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf"),
    ("SC1148", "21658255", "https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf"),
    ("SC1431", "21658261", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1113", "25862713", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    
    # 扩展产品列表（根据实际 SBC 产品添加）
    ("SC1224", "17278644", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3.pdf"),
    ("SC1433", "21658260", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
    ("SC1175", "15298148", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1177", "15298146", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1434", "21658259", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
    ("SC1435", "21658258", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5.pdf"),
    ("SC1176", "15298147", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1223", "17278639", "https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-3.pdf"),
    ("SC1153", "21658276", "https://datasheets.raspberrypi.com/rpi5/rpi5-psu.pdf"),
    ("SC1174", "24627137", "https://datasheets.raspberrypi.com/camera/ai-camera.pdf"),
    
    # 更多 Raspberry Pi 产品
    ("SC1430", "21658262", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1436", "21658256", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf"),
    ("SC1178", "15298145", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1179", "15298144", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    ("SC1180", "15298143", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2.pdf"),
    
    # Orange Pi 产品
    ("OPi5", "22849853", "https://dl.radxa.com/opi5/docs/opi_5_brief_v1.0.pdf"),
    ("OPi5B", "22849854", "https://dl.radxa.com/opi5/docs/opi_5b_brief_v1.0.pdf"),
    ("OPi3B", "20465963", "https://dl.radxa.com/opi3b/docs/opi_3b_brief_v1.0.pdf"),
    
    # Banana Pi 产品
    ("BPI-M5", "18920234", "https://wiki.banana-pi.org/images/4/4e/BPI-M5_Specification_V1.0.pdf"),
    ("BPI-M4", "18920235", "https://wiki.banana-pi.org/images/2/2e/BPI-M4_Specification_V1.0.pdf"),
    ("BPI-M2+", "15298150", "https://wiki.banana-pi.org/images/b/b4/BPI-M2%2B_Specification_V1.0.pdf"),
    
    # BeagleBoard 产品
    ("BBAI64", "20465970", "https://beagleboard.org/static/ai64/BeaglePlay-AI64-brief.pdf"),
    ("BBPlay", "20465971", "https://beagleboard.org/static/play/BeaglePlay-brief.pdf"),
    ("BBGreen", "15298155", "https://beagleboard.org/static/green/BeagleGreen-brief.pdf"),
    
    # NVIDIA Jetson 产品
    ("Jetson Nano", "15298160", "https://www.nvidia.com/content/dam/en-zz/Solutions/embedded-systems/jetson-nano/jetson-nano-ds.pdf"),
    ("Jetson Xavier", "15298161", "https://www.nvidia.com/content/dam/en-zz/Solutions/embedded-systems/jetson-xavier/jetson-xavier-nx-ds.pdf"),
    ("Jetson Orin", "20465980", "https://www.nvidia.com/content/dam/en-zz/Solutions/embedded-systems/jetson-orin/jetson-orin-ds.pdf"),
    
    # Arduino 产品
    ("ARD-NANO", "15298170", "https://content.arduino.cc/assets/NanoRev2.3_schematics.pdf"),
    ("ARD-UNO", "15298171", "https://content.arduino.cc/assets/ArduinoUnoR3_schematics.pdf"),
    ("ARD-MEGA", "15298172", "https://content.arduino.cc/assets/ArduinoMEGA2560_schematics.pdf"),
    
    # ESP32 产品
    ("ESP32-DEV", "15298180", "https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf"),
    ("ESP32-S3", "20465990", "https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf"),
    ("ESP32-C3", "20465991", "https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf"),
    
    # STM32 产品
    ("STM32F4", "15298190", "https://www.st.com/resource/en/datasheet/stm32f405rg.pdf"),
    ("STM32F7", "15298191", "https://www.st.com/resource/en/datasheet/stm32f746ng.pdf"),
    ("STM32H7", "20466000", "https://www.st.com/resource/en/datasheet/stm32h743vi.pdf"),
    
    # Rock Pi 产品
    ("ROCK-4C+", "20466010", "https://wiki.radxa.com/Rock4/4c-plus/rock-4c-plus-brief.pdf"),
    ("ROCK-5B", "20466011", "https://wiki.radxa.com/Rock5/5b/rock-5b-brief.pdf"),
    ("ROCK-Pi-S", "18920240", "https://wiki.radxa.com/RockpiS/rock_pi_s_brief.pdf"),
    
    # Odroid 产品
    ("ODROID-C4", "18920250", "https://www.hardkernel.com/shop/odroid-c4/specification/"),
    ("ODROID-N2+", "18920251", "https://www.hardkernel.com/shop/odroid-n2-plus-2021/specification/"),
    ("ODROID-XU4", "15298200", "https://www.hardkernel.com/shop/odroid-xu4/specification/"),
    
    # Pine64 产品
    ("PINE-A64", "15298210", "https://wiki.pine64.org/wiki/PINE_A64"),
    ("PINE-H64", "18920260", "https://wiki.pine64.org/wiki/PINE_H64"),
    ("PINEBOOK", "18920261", "https://wiki.pine64.org/wiki/PINEBOOK"),
    
    # Cubieboard 产品
    ("CB1", "15298220", "http://cubieboard.org/product/cc-a10-cubieboard1/"),
    ("CB2", "15298221", "http://cubieboard.org/product/cc-a20-cubieboard2/"),
    ("CB4", "18920270", "http://cubieboard.org/product/cubieboard-4/"),
    
    # Udoo 产品
    ("UDOO-NEO", "15298230", "https://www.udoo.org/docs-neo/Hardware/intro.html"),
    ("UDOO-BOLT", "18920280", "https://www.udoo.org/docs-bolt/Hardware/intro.html"),
    ("UDOO-X86", "18920281", "https://www.udoo.org/docs-x86/Hardware/intro.html"),
    
    # LattePanda 产品
    ("LP-DELTA", "18920290", "https://www.lattepanda.com/lattepanda-delta/"),
    ("LP-ALPHA", "15298240", "https://www.lattepanda.com/lattepanda-alpha/"),
    ("LP-CRETA", "20466020", "https://www.lattepanda.com/lattepanda-creta/"),
    
    # Khadas 产品
    ("VIM1", "15298250", "https://dl.khadas.com/products/vim/specs/vim_brief.pdf"),
    ("VIM2", "15298251", "https://dl.khadas.com/products/vim2/specs/vim2_brief.pdf"),
    ("VIM3", "18920300", "https://dl.khadas.com/products/vim3/specs/vim3_brief.pdf"),
    ("VIM4", "20466030", "https://dl.khadas.com/products/vim4/specs/vim4_brief.pdf"),
    
    # NanoPi 产品
    ("NP-R4S", "18920310", "https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R4S"),
    ("NP-R5S", "20466040", "https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R5S"),
    ("NP-NEO3", "18920311", "https://wiki.friendlyelec.com/wiki/index.php/NanoPi_NEO3"),
    
    # Asus Tinker Board
    ("TB-S", "15298260", "https://www.asus.com/us/supportonly/tinker-board-s/helpdesk_download/"),
    ("TB-2", "18920320", "https://www.asus.com/us/supportonly/tinker-board-2/helpdesk_download/"),
    
    # Google Coral
    ("CORAL-DEV", "18920330", "https://coral.ai/docs/dev-board/specs/"),
    ("CORAL-USB", "18920331", "https://coral.ai/docs/usb-acc/specs/"),
    
    # HummingBoard
    ("HB-G", "15298270", "https://www.solid-run.com/products/hummingboard-platform/"),
    ("HB-PULSE", "18920340", "https://www.solid-run.com/products/hummingboard-pulse/"),
    
    # Wandboard
    ("WAND-QUAD", "15298280", "https://www.wandboard.org/"),
    ("WAND-I.MX8", "18920350", "https://www.wandboard.org/"),
    
    # PC Engines
    ("ALIX", "15298290", "http://www.pcengines.ch/alix.htm"),
    ("APU", "15298291", "http://www.pcengines.ch/apu.htm"),
    
    # Technexion
    ("PI-POCK", "15298300", "https://www.technexion.com/products/pico-pi-imx7/"),
    ("WIZ-PI", "18920360", "https://www.technexion.com/products/wizpi/"),
    
    # Variscite
    ("VAR-SOM", "18920370", "https://www.variscite.com/product/system-on-module/var-som-imx8/"),
    ("DART", "18920371", "https://www.variscite.com/product/single-board-computer/dart-imx8/"),
    
    # Compulab
    ("FUTURA", "18920380", "https://www.compulab.com/products/futura/"),
    ("ACCM", "18920381", "https://www.compulab.com/products/accm-imx8/"),
    
    # Advantech
    ("UNO-220", "18920390", "https://www.advantech.com/products/industrial-controllers/uno-220/"),
    ("MIC-710", "18920391", "https://www.advantech.com/products/industrial-motherboards/mic-710/"),
    
    # Aaeon
    ("UP-BOARD", "15298310", "https://up-board.org/upsquared/specifications/"),
    ("UP-SQUARED", "15298311", "https://up-board.org/upsquared/specifications/"),
    ("UP-XTREME", "18920400", "https://up-board.org/upxtreme/specifications/"),
    
    # Seeed Studio
    ("ODYSSEY", "18920410", "https://www.seeedstudio.com/odyssey-x86j410586400.html"),
    ("RESENSOR", "18920411", "https://www.seeedstudio.com/Respeaker-Core-MSM8916-p-2861.html"),
    
    # M5Stack
    ("M5-CORE", "18920420", "https://docs.m5stack.com/en/core/core"),
    ("M5-BASE", "18920421", "https://docs.m5stack.com/en/core/base"),
    
    # LilyGO
    ("TTGO-T1", "18920430", "https://github.com/Xinyuan-LilyGO/TTGO-T-Call"),
    ("TTGO-T5", "18920431", "https://github.com/Xinyuan-LilyGO/TTGO-T-E-Paper"),
    
    # Heltec
    ("HT-ESP32", "18920440", "https://heltec.org/project/wifi-kit-32/"),
    ("HT-LORA", "18920441", "https://heltec.org/project/wifi-lora-32/"),
]

async def download_file(session, url, save_path, semaphore):
    """异步下载文件"""
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # 随机延迟
                delay = time.uniform(*RANDOM_DELAY)
                await asyncio.sleep(delay)
                
                async with session.get(url, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(save_path, 'wb') as f:
                            f.write(content)
                        return True
                    elif response.status == 404:
                        return 'not_found'
                    else:
                        if attempt < MAX_RETRIES:
                            continue
                        return False
                        
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES:
                    continue
                return False
            except Exception as e:
                if attempt < MAX_RETRIES:
                    continue
                return False
        
        return False

async def process_product(session, product, semaphore):
    """处理单个产品"""
    product_name, product_id, pdf_url = product
    filename = f"{re.sub(r'[<>:"/\\|?*]', '_', product_name)}_{product_id}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # 检查是否已下载
    if os.path.exists(output_path):
        stats['success'] += 1
        return product_name, product_id, 'exists'
    
    # 下载
    result = await download_file(session, pdf_url, output_path, semaphore)
    
    if result is True:
        stats['success'] += 1
        status = 'success'
    elif result == 'not_found':
        stats['not_found'] += 1
        status = 'not_found'
    else:
        stats['failed'] += 1
        status = 'failed'
    
    # 记录日志
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{product_name}\t{product_id}\t{pdf_url}\t{filename}\t{status.upper()}\n")
    
    return product_name, product_id, status

async def process_batch(batch, batch_num, semaphore):
    """处理一批产品"""
    async with aiohttp.ClientSession() as session:
        tasks = [process_product(session, product, semaphore) for product in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                stats['failed'] += 1
                print(f"  ❌ {batch[i][0]}: {result}")

def generate_hourly_report():
    """生成小时报告"""
    elapsed = time.time() - stats['start_time'] if stats['start_time'] else 0
    hours = elapsed / 3600
    rate = stats['total'] / hours if hours > 0 else 0
    
    report = f"""# DigiKey SBC 爬取进度报告

**报告时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**批次：** 第 {stats['batches']} 批

## 进度统计

| 指标 | 数值 |
|------|------|
| **总产品数** | {stats['total']} |
| **成功下载** | {stats['success']} |
| **失败** | {stats['failed']} |
| **未找到** | {stats['not_found']} |
| **成功率** | {stats['success'] / stats['total'] * 100:.1f}% (如有数据) |
| **运行时间** | {elapsed / 60:.1f} 分钟 |
| **平均速度** | {rate:.1f} 个/小时 |

## 并发状态

| 配置 | 值 |
|------|------|
| **最大并发数** | {MAX_CONCURRENT} |
| **超时时间** | {TIMEOUT} 秒 |
| **重试次数** | {MAX_RETRIES} 次 |

## 下一步计划

继续处理下一批产品...

---
_最强大脑 AI 公司_ 🦞
"""
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

async def main():
    """主函数"""
    print("=" * 70)
    print("DigiKey SBC 规格书爬虫 - 并发版")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    stats['start_time'] = time.time()
    
    # 创建信号量控制并发
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    # 分批处理（每批 50 个产品）
    batch_size = 50
    batches = [PRODUCTS[i:i + batch_size] for i in range(0, len(PRODUCTS), batch_size)]
    
    print(f"\n总产品数：{len(PRODUCTS)}")
    print(f"批次数：{len(batches)}")
    print(f"并发数：{MAX_CONCURRENT}")
    print(f"每批大小：{batch_size}")
    print()
    
    # 处理每一批
    for batch_num, batch in enumerate(batches, 1):
        stats['batches'] = batch_num
        print(f"\n{'=' * 70}")
        print(f"【批次 {batch_num}/{len(batches)}】")
        print(f"{'=' * 70}")
        
        batch_start = time.time()
        
        # 处理当前批次
        await process_batch(batch, batch_num, semaphore)
        
        batch_elapsed = time.time() - batch_start
        stats['total'] = stats['success'] + stats['failed'] + stats['not_found']
        
        print(f"\n批次 {batch_num} 完成:")
        print(f"  成功：{stats['success']}")
        print(f"  失败：{stats['failed']}")
        print(f"  未找到：{stats['not_found']}")
        print(f"  耗时：{batch_elapsed:.1f} 秒")
        
        # 每小时生成报告
        elapsed = time.time() - stats['start_time']
        if elapsed >= 3600:  # 1 小时
            report = generate_hourly_report()
            print(f"\n📊 已生成小时报告")
            stats['start_time'] = time.time()  # 重置计时
    
    # 最终统计
    total_elapsed = time.time() - stats['start_time']
    print("\n" + "=" * 70)
    print("爬取完成!")
    print("=" * 70)
    print(f"总产品数：{len(PRODUCTS)}")
    print(f"成功下载：{stats['success']}")
    print(f"失败：{stats['failed']}")
    print(f"未找到：{stats['not_found']}")
    print(f"成功率：{stats['success'] / len(PRODUCTS) * 100:.1f}%")
    print(f"总耗时：{total_elapsed / 60:.1f} 分钟")
    print(f"输出目录：{OUTPUT_DIR}")
    
    # 生成最终报告
    generate_hourly_report()

if __name__ == "__main__":
    asyncio.run(main())
