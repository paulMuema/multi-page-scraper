import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("🚀 Launching Chromium browser...")
        # Keep headless=False so you can visually watch it do its work!
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Globally enforce a safety buffer for loading items
        page.set_default_timeout(10000)
        
        print("🌐 Connecting to target website...")
        await page.goto("https://quotes.toscrape.com/")
        
        scraped_data = []
        page_number = 1
        
        while True:
            print(f"⏳ Processing Page {page_number}...")
            
            # Step 1: Explicitly wait for the list items to stabilize on screen
            await page.wait_for_selector(".quote")
            
            # Step 2: Grab the parent block containers directly
            quotes_blocks = await page.locator(".quote").all()
            
            # Step 3: Loop inside the current layout elements
            for block in quotes_blocks:
                text_element = await block.locator(".text").inner_text()
                author_element = await block.locator(".author").inner_text()
                
                scraped_data.append({
                    "Quote": text_element,
                    "Author": author_element,
                    "Page": page_number
                })
            
            # Locate the "Next" link container
            next_button = page.locator(".next a")
            
            # If the button exists and is visible on screen, click it
            if await next_button.count() > 0:
                print("🖱️ Clicking 'Next' button...")
                page_number += 1
                
                # Click and explicitly pause to allow client-side hydration to settle
                await next_button.click()
                await asyncio.sleep(1)  
            else:
                print("🏁 No 'Next' button remaining. Extraction complete!")
                break
        
        print("📊 Saving all pages into an Excel spreadsheet...")
        df = pd.DataFrame(scraped_data)
        df.to_excel("all_scraped_quotes.xlsx", index=False)
        
        print("✅ SUCCESS! Check your directory for 'all_scraped_quotes.xlsx'")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
