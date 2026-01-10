
import asyncio, os

from python_general_lib.environment_setup.logging_setup import *
logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s] %(message)s",
    # datefmt="[%X]",
)

from scrab_browser.playwright_browser_retrieve import GetWrapPlaywrightBrowserContext
from scrab_browser.websites.baidu_pan.login import BaiduPanLogin
from scrab_browser.websites.baidu_pan.get_shared_link import BaiduPanSharedLink
# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

async def main():
  async with async_playwright() as p:
    context = await GetWrapPlaywrightBrowserContext(p)

    # await BaiduPanLogin.GuaranteeBaiduPanLogin(context)

    baidu_share_url = "https://pan.baidu.com/s/1flqi_JjQRHhCvtN-JJHUJA"
    shared_link_page = await BaiduPanSharedLink.GetSharedLink(
        context, baidu_share_url, "yezi")

    # await page.goto("https://example.com")

    # title = await page.title()
    # print(f"页面标题: {title}")

    input()

    await context.close()

asyncio.run(main())