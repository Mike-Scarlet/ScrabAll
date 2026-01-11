
from playwright.async_api import Page

async def WaitForBaidupanSharedLinkStable(page: Page, timeout: int = 10000):
  # print("in WaitForBaidupanSharedLinkStable")
  await page.wait_for_selector('.cazEfA, .wPQwLCb', state='visible', timeout=timeout)
  # print("out WaitForBaidupanSharedLinkStable")
  