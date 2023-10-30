import asyncio
from pyppeteer import launch

async def main():
    browser = await launch()
    page = await browser.newPage()

    await page.goto('https://www.tiendaenlinea.7-eleven.com.mx/') 
    
    await page.waitFor('button[data-id="mega-menu-trigger-button"]')  
    
    await page.click('button[data-id="mega-menu-trigger-button"]')
    await asyncio.sleep(2)
    await page.waitForSelector('.vtex-mega-menu-2-x-menuContainer list ma0 pa0 pb3 br b--muted-4', {'visible': True})

    html_content = await page.content()
    print(html_content)
    await browser.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
