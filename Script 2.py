from playwright.sync_api import sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import os

def download_padel_grids(sites):
    target_folder = "peak_padel_research"
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Created new folder: {target_folder}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for url in sites:
            context = browser.new_context(viewport={'width': 1400, 'height': 900})
            page = context.new_page()
            
            club_name = url.split('/clubs/')[1].split('?')[0]
            print(f"\n--- Processing: {club_name} ---")

            try:
                page.goto(url, wait_until="commit")

                grid_selector = "div.rounded-lg.bg-white.shadow-md.order-2.md\\:order-1"

                page.wait_for_selector(grid_selector, timeout=20000)
                time.sleep(2) 

                # --- FIX FOR STRIPED BOXES ---
                # Simulate clicking Next Day (>) then Previous Day (<) to force solid grey boxes to render
                try:
                    # Target the 'Next' and 'Previous' date buttons by looking for chevron SVG icons
                    next_btn = page.locator("button:has(svg[class*='right']), button:has(svg[data-icon*='right'])").first
                    prev_btn = page.locator("button:has(svg[class*='left']), button:has(svg[data-icon*='left'])").first

                    # Fallback if specific SVG classes aren't found: grab the first two SVG buttons (usually the date arrows)
                    if not next_btn.is_visible(timeout=1000):
                        next_btn = page.locator("button:has(svg)").nth(1)
                        prev_btn = page.locator("button:has(svg)").nth(0)

                    next_btn.click()
                    time.sleep(2)  # Wait for the next day to load
                    prev_btn.click()
                    time.sleep(3)  # Wait for the original day to reload and paint properly
                except Exception as e:
                    print(f"Date toggle workaround failed for {club_name}: {e}")

                # Clear cookie banner
                try:
                    cookie_btn = page.get_by_role("button", name="Accept").or_(page.get_by_role("button", name="Reject"))
                    if cookie_btn.is_visible(timeout=3000):
                        cookie_btn.click()
                except:
                    pass

                # --- SAVING TO THE FOLDER ---
                date_str = url.split('date=')[-1]
                file_name = f"grid_{club_name}_{date_str}.png"
                
                full_save_path = os.path.join(target_folder, file_name)
                
                grid_element = page.locator(grid_selector).first
                grid_element.screenshot(path=full_save_path)
                
                print(f"SUCCESS: Saved to {full_save_path}")

            except Exception as e:
                print(f"FAILED for {club_name}: {e}")
            
            context.close()

        browser.close()

today_str = datetime.now(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d")

base_sites = [
    "https://playtomic.com/clubs/tribe-padel-wellness-sydney",
    "https://playtomic.com/clubs/indoor-padel-australia-alexandria",
    "https://playtomic.com/clubs/indoor-padel-australia-northern-beaches",
    "https://playtomic.com/clubs/sydney-racquet-club",
    "https://playtomic.com/clubs/padel-club-australia",
    "https://playtomic.com/clubs/padel-point-bankstown",
    "https://playtomic.com/clubs/sol-padel-albury",
    "https://playtomic.com/clubs/game4padel-docklands",
    "https://playtomic.com/clubs/game4padel-richmond",
    "https://playtomic.com/clubs/ipadel-melbourne",
    "https://playtomic.com/clubs/canberra-racquet-club"
]

padel_sites = [f"{site}?date={today_str}" for site in base_sites]

if __name__ == "__main__":
    download_padel_grids(padel_sites)
