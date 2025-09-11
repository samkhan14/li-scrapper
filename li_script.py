from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

LI_AT_COOKIE = os.getenv("LI_AT_COOKIE")

# URLs
POSTS_URL = "https://www.linkedin.com/search/results/content/?datePosted=past-24h&keywords=laravel,karachi"
JOBS_URL = "https://www.linkedin.com/jobs/search/?keywords=laravel&location=Karachi&f_TPR=r86400"

OUTPUT_FILE = f"linkedin_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

def scrape_posts(page):
    print("➡️ Scraping recruiter posts...")
    page.goto(POSTS_URL, timeout=60000)
    page.wait_for_timeout(5000)

    for _ in range(3):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(3000)

    posts = page.query_selector_all(".reusable-search__result-container")

    data = []
    for post in posts:
        text = post.query_selector(".update-components-text span")
        link = post.query_selector("a.app-aware-link")
        time = post.query_selector("time")

        data.append({
            "Source": "Post",
            "Text": text.inner_text().strip() if text else "",
            "URL": link.get_attribute("href") if link else "",
            "DateTime": time.get_attribute("datetime") if time else datetime.now().isoformat()
        })
    return data

def scrape_jobs(page):
    print("➡️ Scraping direct jobs...")
    page.goto(JOBS_URL, timeout=60000)
    page.wait_for_timeout(5000)

    for _ in range(3):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(3000)

    jobs = page.query_selector_all(".base-card")

    data = []
    for job in jobs:
        title = job.query_selector(".base-search-card__title")
        company = job.query_selector(".base-search-card__subtitle")
        location = job.query_selector(".job-search-card__location")
        link = job.query_selector("a.base-card__full-link")
        time = job.query_selector("time")

        data.append({
            "Source": "Job",
            "Title": title.inner_text().strip() if title else "",
            "Company": company.inner_text().strip() if company else "",
            "Location": location.inner_text().strip() if location else "",
            "URL": link.get_attribute("href") if link else "",
            "DateTime": time.get_attribute("datetime") if time else datetime.now().isoformat()
        })
    return data

def scrape_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Cookie injection
        context.add_cookies([{
            "name": "li_at",
            "value": LI_AT_COOKIE,
            "domain": ".linkedin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }])

        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/")
        page.wait_for_timeout(5000)

        posts_data = scrape_posts(page)
        jobs_data = scrape_jobs(page)

        all_data = posts_data + jobs_data

        
        df = pd.DataFrame(all_data)
        df.to_excel(OUTPUT_FILE, index=False)
        
        print(f"✅ Saved {len(all_data)} records to {OUTPUT_FILE}")

        browser.close()

if __name__ == "__main__":
    if not LI_AT_COOKIE:
        print("❌ Error: LI_AT_COOKIE not set. Add it as environment variable or GitHub secret.")
    else:
        scrape_all()


