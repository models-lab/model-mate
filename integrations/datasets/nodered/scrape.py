import json
import time
import traceback
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def exists_flow(flow_link, existing_flows):
    for existing_flow in existing_flows:
        if existing_flow['url'] == flow_link:
            return True
    return False

def scrape_nodered_flows(init=1, end=191):
    options = Options()
    #options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Load nodered_flows.json
    with open("nodered_flows.json", "r", encoding="utf-8") as f:
        existing_flows = json.loads(f.read())


    base_url = "https://flows.nodered.org/search?type=flow"
    all_flows = []
    all_flows.extend(existing_flows)

    try:
        for page in range(init, end):
            print("Scraping page", page)
            url = f"{base_url}&page={page}"
            driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load

            # Find all flow entries
            flow_elements = driver.find_elements(By.CSS_SELECTOR, ".gistbox-flow a")

            for flow_element in flow_elements:
                flow_name = flow_element.text
                flow_link = flow_element.get_attribute("href")

                if exists_flow(flow_link, existing_flows):
                    print("Ignoring existing flow: " + flow_link)
                    continue

                # Visit flow detail page
                driver.get(flow_link)
                time.sleep(random.randrange(2, 5))

                # Extract the flow JSON
                try:
                    flow_json_element = driver.find_element(By.CSS_SELECTOR, "pre#flow span")
                    gist_element = driver.find_element(By.XPATH,
                                                       "//div[@class='flowmeta']//a[contains(@href, 'gist.github.com')]")
                    gist_url = gist_element.get_attribute("href")

                    flow_json = flow_json_element.text
                except:
                    traceback.print_exc()
                    flow_json = None  # Some flows may not have JSON

                if flow_json:
                    all_flows.append({
                        "name": flow_name,
                        "url": flow_link,
                        "gist": gist_url,
                        "flow": json.loads(flow_json)
                    })

                # Go back to the list page
                driver.back()
                time.sleep(random.randrange(2, 5))

            # Save results to a JSON file after each complete page
            with open("nodered_flows.json", "w", encoding="utf-8") as f:
                json.dump(all_flows, f, indent=4)


    finally:
        driver.quit()

    print(f"✅ Scraped {len(all_flows)} flows and saved to 'nodered_flows.json'.")

if __name__ == "__main__":
    scrape_nodered_flows(init=1, end=191)
