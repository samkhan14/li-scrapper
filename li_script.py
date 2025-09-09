from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

# =======================
# CONFIG
# =======================

LI_AT_COOKIE = "AQEDAV6LZcoDancZAAABmTDKU6sAAAGZVNbXq00AwEO02lhRwX3H3me9pgyIGVdPYUECiDL-qo883M9rt-dOj-yDSOwdBms810SfMcNV6R2HL5jdfS3M60g1vIysGiwbraRFQCPsz4sN8_jfYC4I0wJC"
SEARCH_URL = "https://www.linkedin.com/search/results/content/?datePosted=past-24h&keywords=laravel,karachi"

OUTPUT_FILE = f"linkedin_posts_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"


def scrape_posts():
    with sync_playwright() as p:
        # Launch browser in headless mode (background)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Add LinkedIn login cookie
        context.add_cookies([{
            "name": "li_at",
            "value": LI_AT_COOKIE,
            "domain": ".linkedin.com",
            "path": "/"
        }])

        page = context.new_page()

        # Go to LinkedIn search URL
        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load more posts
        for _ in range(3):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)

        # Extract posts
        posts = page.query_selector_all(".update-components-text")

        data = []
        for post in posts:
            text = post.inner_text().strip()
            if text:
                data.append({
                    "PostText": text,
                    "ScrapedAt": datetime.now().isoformat()
                })

        # Save to Excel
        df = pd.DataFrame(data)
        df.to_excel(OUTPUT_FILE, index=False)

        print(f"✅ Scraped {len(data)} posts and saved to {OUTPUT_FILE}")

        browser.close()


if __name__ == "__main__":
    scrape_posts()
