from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import os

def download_padel_grids(sites):
    # --- SETUP THE TARGET FOLDER ---
    # Changed from a hardcoded Desktop path to a relative path
    target_folder = "peak_padel_research"
    
    # Create the folder if it doesn't exist yet
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Created new folder: {target_folder}")

    with sync_playwright() as p:
        # Changed headless=False to True so it doesn't crash on GitHub's monitor-less servers
        browser = p.chromium.launch(headless=True)
        
        for url in sites:
            # New context for stability
            context = browser.new_context(viewport={'width': 1400, 'height': 900})
            page = context.new_page()
            
            # Extracting the club name from the URL
            club_name = url.split('/clubs/')[1].split('?')[0]
            print(f"\n--- Processing: {club_name} ---")

            try:
                page.goto(url, wait_until="commit")

                # The selector for the grid
                grid_selector = "div.rounded-lg.bg-white.shadow-md.order-2.md\\:order-1"

                page.wait_for_selector(grid_selector, timeout=20000)
                time.sleep(4) # Wait for grey boxes to paint

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
                
                # Combine the folder path with the filename
                full_save_path = os.path.join(target_folder, file_name)
                
                grid_element = page.locator(grid_selector).first
                grid_element.screenshot(path=full_save_path)
                
                print(f"SUCCESS: Saved to {full_save_path}")

            except Exception as e:
                print(f"FAILED for {club_name}: {e}")
            
            context.close()

        browser.close()

# 1. Get today's date in the exact format Playtomic expects (YYYY-MM-DD)
today_str = datetime.now().strftime("%Y-%m-%d")

# 2. List your base URLs without the date attached
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

# 3. Dynamically create the final list by combining the base URL and today's date
padel_sites = [f"{site}?date={today_str}" for site in base_sites]

if __name__ == "__main__":
    download_padel_grids(padel_sites)