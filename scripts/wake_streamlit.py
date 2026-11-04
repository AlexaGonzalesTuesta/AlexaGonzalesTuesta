"""Opens each Streamlit demo in a real browser and clicks the wake button if the app is asleep.

Streamlit Community Cloud only wakes an app when a person clicks
"Yes, get this app back up!", so a plain HTTP ping is not enough.
Exits with code 1 if any app is still asleep, so GitHub emails you.
"""
import sys
from playwright.sync_api import sync_playwright

APPS = [
    "https://aero-repair-tat-analytics-eb8r3ndycesifmfduzgrsj.streamlit.app/",
    "https://equipment-parts-integration-app-hrkhgumc6pa6hzh4jxulvq.streamlit.app/",
]
WAKE_TEXT = "get this app back up"


def wake(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(8_000)
    button = page.get_by_role("button", name=WAKE_TEXT, exact=False)
    if button.count() == 0:
        print(f"AWAKE   {url}")
        return True
    print(f"ASLEEP  {url} -> clicking wake button")
    button.first.click()
    # Booting a sleeping app can take a couple of minutes.
    for _ in range(24):
        page.wait_for_timeout(10_000)
        if page.get_by_role("button", name=WAKE_TEXT, exact=False).count() == 0:
            print(f"WOKE UP {url}")
            return True
    print(f"FAILED  {url} is still asleep")
    return False


def main(urls):
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for url in urls:
            try:
                ok = wake(page, url) and ok
            except Exception as exc:  # keep checking the other apps
                print(f"ERROR   {url}: {exc}")
                ok = False
        browser.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or APPS))
