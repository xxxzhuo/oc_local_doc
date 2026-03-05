#!/usr/bin/env python3
"""
DigiKey SBC 规格书爬虫 - Playwright 并发版
使用 Playwright 浏览器自动化获取真实 PDF 链接并下载
"""

import asyncio
from playwright.async_api import async_playwright, Page
import os
import time
from datetime import datetime
import re

# 配置
OUTPUT_DIR = "/Users/mac/.openclaw/workspace/oc_local_doc/datasheets/digikey-sbc"
LOG_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/download_log.txt"
REPORT_FILE = "/Users/mac/.openclaw/workspace/oc_local_doc/projects/digikey-crawler/hourly_report.md"

# 并发配置
MAX_CONCURRENT = 5  # 最大并发浏览器实例数
TIMEOUT = 60000  # 超时时间（毫秒）
RANDOM_DELAY = (2, 5)  # 随机延迟范围（秒）

# 统计
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'not_found': 0,
    'start_time': None,
    'batches': 0,
    'products_processed': 0
}

# SBC 分类页面 URL
SBC_CATEGORY_URL = "https://www.digikey.com/en/products/filter/development-boards-kits-programmers/single-board-computers-sbc/2040"

async def get_product_urls(page: Page) -> list:
    """从分类页面获取所有产品链接"""
    print(f"访问分类页面：{SBC_CATEGORY_URL}")
    
    try:
        await page.goto(SBC_CATEGORY_URL, wait_until='networkidle', timeout=TIMEOUT)
        await page.wait_for_timeout(3000)  # 等待页面完全加载
        
        # 提取所有产品链接
        product_links = await page.query_selector_all('a[href*="/en/products/detail/"]')
        
        product_urls = []
        seen_urls = set()
        
        for link in product_links:
            href = await link.get_attribute('href')
            if href and href not in seen_urls:
                full_url = f"https://www.digikey.com{href}"
                product_urls.append(full_url)
                seen_urls.add(full_url)
        
        print(f"找到 {len(product_urls)} 个产品")
        return product_urls
        
    except Exception as e:
        print(f"❌ 获取产品列表失败：{e}")
        return []

async def get_datasheet_url(page: Page, product_url: str) -> str:
    """从产品页面提取规格书 PDF 链接"""
    try:
        await page.goto(product_url, wait_until='networkidle', timeout=TIMEOUT)
        await page.wait_for_timeout(2000)  # 等待页面稳定
        
        # 查找规格书链接
        datasheet_link = await page.query_selector('a[href*=".pdf"]')
        
        if datasheet_link:
            href = await datasheet_link.get_attribute('href')
            if href:
                if href.startswith('http'):
                    return href
                else:
                    return f"https://www.digikey.com{href}"
        
        # 尝试其他选择器
        datasheet_links = await page.query_selector_all('text=Datasheet')
        if datasheet_links:
            for link in datasheet_links:
                href = await link.get_attribute('href')
                if href and '.pdf' in href:
                    return href if href.startswith('http') else f"https://www.digikey.com{href}"
        
        return None
        
    except Exception as e:
        print(f"    ❌ 提取失败：{e}")
        return None

async def download_pdf(session, url: str, save_path: str) -> bool:
    """下载 PDF 文件"""
    try:
        response = await session.get(url, timeout=30)
        if response.status == 200:
            content = await response.read()
            with open(save_path, 'wb') as f:
                f.write(content)
            return True
        elif response.status == 404:
            return 'not_found'
        else:
            return False
    except Exception as e:
        print(f"    ❌ 下载失败：{e}")
        return False

async def process_product(page: Page, product_url: str, semaphore: asyncio.Semaphore, aiohttp_session):
    """处理单个产品"""
    async with semaphore:
        # 随机延迟
        delay = time.uniform(*RANDOM_DELAY)
        await asyncio.sleep(delay)
        
        try:
            # 提取产品信息
            parts = product_url.rstrip('/').split('/')
            product_name = parts[-3] if len(parts) >= 3 else "unknown"
            product_id = parts[-2] if len(parts) >= 2 else "unknown"
            
            print(f"\n处理：{product_name} ({product_id})")
            
            # 获取规格书 URL
            datasheet_url = await get_datasheet_url(page, product_url)
            
            if not datasheet_url:
                print(f"  ⚠️  未找到规格书")
                stats['not_found'] += 1
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{product_name}\t{product_id}\t-\t-\tNOT_FOUND\n")
                return
            
            print(f"  ✓ 找到：{datasheet_url}")
            
            # 生成文件名
            filename = f"{re.sub(r'[<>:"/\\|?*]', '_', product_name)}_{product_id}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            # 检查是否已下载
            if os.path.exists(output_path):
                print(f"  ⚠️  文件已存在，跳过")
                stats['success'] += 1
                return
            
            # 下载 PDF
            print(f"  下载：{filename}")
            result = await download_pdf(aiohttp_session, datasheet_url, output_path)
            
            if result is True:
                print(f"  ✓ 下载成功")
                stats['success'] += 1
                status = 'SUCCESS'
            elif result == 'not_found':
                print(f"  ✗ PDF 不存在")
                stats['not_found'] += 1
                status = 'NOT_FOUND'
            else:
                print(f"  ✗ 下载失败")
                stats['failed'] += 1
                status = 'FAILED'
            
            # 记录日志
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{product_name}\t{product_id}\t{datasheet_url}\t{filename}\t{status}\n")
            
            stats['products_processed'] += 1
            
        except Exception as e:
            print(f"  ❌ 错误：{e}")
            stats['failed'] += 1
            stats['products_processed'] += 1

def generate_hourly_report():
    """生成小时报告"""
    elapsed = time.time() - stats['start_time'] if stats['start_time'] else 0
    hours = elapsed / 3600
    rate = stats['products_processed'] / hours if hours > 0 else 0
    
    total = stats['success'] + stats['failed'] + stats['not_found']
    success_rate = (stats['success'] / total * 100) if total > 0 else 0
    
    report = f"""# DigiKey SBC 爬取进度报告 (Playwright 并发版)

**报告时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**批次：** 第 {stats['batches']} 批

## 进度统计

| 指标 | 数值 |
|------|------|
| **已处理产品数** | {stats['products_processed']} |
| **成功下载** | {stats['success']} |
| **失败** | {stats['failed']} |
| **未找到** | {stats['not_found']} |
| **成功率** | {success_rate:.1f}% |
| **运行时间** | {elapsed / 60:.1f} 分钟 |
| **平均速度** | {rate:.1f} 个/小时 |

## 并发状态

| 配置 | 值 |
|------|------|
| **最大并发数** | {MAX_CONCURRENT} |
| **超时时间** | {TIMEOUT / 1000} 秒 |

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
    print("DigiKey SBC 规格书爬虫 - Playwright 并发版")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    stats['start_time'] = time.time()
    
    async with async_playwright() as p:
        # 启动多个浏览器实例
        browsers = []
        pages = []
        
        for i in range(MAX_CONCURRENT):
            browser = await p.chromium.launch(headless=True)
            browsers.append(browser)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            pages.append(page)
        
        print(f"已启动 {MAX_CONCURRENT} 个浏览器实例")
        
        # 导入 aiohttp 用于下载
        import aiohttp
        async with aiohttp.ClientSession() as aiohttp_session:
            # 获取所有产品链接
            product_urls = await get_product_urls(pages[0])
            
            if not product_urls:
                print("❌ 未找到产品")
                return
            
            # 创建信号量控制并发
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            
            # 分批处理
            batch_size = 50
            batches = [product_urls[i:i + batch_size] for i in range(0, len(product_urls), batch_size)]
            
            print(f"\n总产品数：{len(product_urls)}")
            print(f"批次数：{len(batches)}")
            print(f"并发数：{MAX_CONCURRENT}")
            print(f"每批大小：{batch_size}")
            
            # 处理每一批
            for batch_num, batch in enumerate(batches, 1):
                stats['batches'] = batch_num
                print(f"\n{'=' * 70}")
                print(f"【批次 {batch_num}/{len(batches)}】")
                print(f"{'=' * 70}")
                
                batch_start = time.time()
                
                # 分配任务到多个浏览器
                tasks = []
                for i, product_url in enumerate(batch):
                    page = pages[i % len(pages)]
                    task = process_product(page, product_url, semaphore, aiohttp_session)
                    tasks.append(task)
                
                # 并发执行
                await asyncio.gather(*tasks, return_exceptions=True)
                
                batch_elapsed = time.time() - batch_start
                total = stats['success'] + stats['failed'] + stats['not_found']
                
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
            total = stats['success'] + stats['failed'] + stats['not_found']
            success_rate = (stats['success'] / total * 100) if total > 0 else 0
            
            print("\n" + "=" * 70)
            print("爬取完成!")
            print("=" * 70)
            print(f"总产品数：{len(product_urls)}")
            print(f"成功下载：{stats['success']}")
            print(f"失败：{stats['failed']}")
            print(f"未找到：{stats['not_found']}")
            print(f"成功率：{success_rate:.1f}%")
            print(f"总耗时：{total_elapsed / 60:.1f} 分钟")
            print(f"输出目录：{OUTPUT_DIR}")
            
            # 生成最终报告
            generate_hourly_report()
            
            # 关闭浏览器
            for browser in browsers:
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
