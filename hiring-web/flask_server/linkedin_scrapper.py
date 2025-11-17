from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import logging
import time


class LinkedinScrapper:
    def __init__(self):
        logging.basicConfig(filename="linkedin-scraping.log", level=logging.INFO)

    @staticmethod
    def clean_jobs(jobs: list) -> list:
        cleaned_jobs = []
        for job in jobs:
            check = True
            for value in job.values():
                if value is None:
                    check = False
            if check:
                cleaned_jobs.append(job)
        return cleaned_jobs

    @staticmethod
    def scrape_linkedin_jobs(
        job_title: str,
        location: str,
        pages: int = 1,
        max_jobs: int = 5
    ) -> list:

        logging.info(f"Scraping '{job_title}' in '{location}' with pages={pages}, max_jobs={max_jobs}")

        pages = pages or 1
        jobs = []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
            page.goto(url, timeout=60000)

            last_count = 0

            for block in range(pages):
                logging.info(f"Scrolling block {block + 1}/{pages}...")

                for _ in range(15):  # multiple small scrolls instead of one big one
                    page.mouse.wheel(0, 800)
                    time.sleep(0.3)

                    # check if new jobs loaded
                    count_now = page.locator(".base-card__full-link").count()
                    if count_now > last_count:
                        last_count = count_now

                # Try clicking "load more"
                try:
                    load_btn = page.locator("button.infinite-scroller__show-more-button")
                    if load_btn.is_visible():
                        logging.info("Clicking 'Load more jobs' button...")
                        load_btn.click()
                        time.sleep(0.3)
                except:
                    pass

            # Parse all loaded jobs
            soup = BeautifulSoup(page.content(), "html.parser")
            job_cards = soup.select("div.base-search-card")

            logging.info(f"Found {len(job_cards)} job cards after scrolling.")

            for card in job_cards:
                if len(jobs) >= max_jobs:
                    break

                try:
                    title = card.find("h3", class_="base-search-card__title").text.strip()
                    company = card.find("h4", class_="base-search-card__subtitle").text.strip()
                    job_loc = card.find("span", class_="job-search-card__location").text.strip()
                    link = card.find("a", class_="base-card__full-link")["href"]
                    job_id = link[link.find("?")-10:link.find("?")]
                    posted_date = card.find("time", class_="job-search-card__listdate")["datetime"]

                except:
                    logging.warning("Skipped a malformed job card.")
                    continue

                # Navigate to job page for description
                try:
                    page.goto(link, timeout=15000)
                    time.sleep(0.5)

                    detail_soup = BeautifulSoup(page.content(), "html.parser")
                    desc_element = detail_soup.find(
                        "div", class_="description__text description__text--rich"
                    )

                    if desc_element:
                        desc = desc_element.get_text(" ", strip=True)
                    else:
                        desc = None

                    # Clean description
                    if desc:
                        emoji_pattern = re.compile(
                            "[" 
                            "\U0001F600-\U0001F64F"
                            "\U0001F300-\U0001F5FF"
                            "\U0001F680-\U0001F6FF"
                            "\U0001F700-\U0001F77F"
                            "\U0001F780-\U0001F7FF"
                            "\U0001F800-\U0001F8FF"
                            "\U0001F900-\U0001F9FF"
                            "\U0001FA00-\U0001FA6F"
                            "\U0001FA70-\U0001FAFF"
                            "\u2600-\u26FF"
                            "\u2700-\u27BF"
                            "]"
                        )
                        desc = emoji_pattern.sub("", desc)
                        desc = re.sub(r"\s+", " ", desc)
                        salary = detail_soup.find("div", class_="salary compensation__salary").text.strip()

                except Exception as e:
                    logging.warning(f"Failed to extract description: {str(e)}")
                    desc = None

                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "city": job_loc,
                    "description": desc,
                    "salary": salary,
                    "posted_date": posted_date
                })

                logging.info(f"Scraped: {title} @ {company}")

        # Return exact max_jobs
        return jobs[:max_jobs]