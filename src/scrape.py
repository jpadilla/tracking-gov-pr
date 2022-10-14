import datetime

import requests
from parsel import Selector


def get_directory_detail(url):
    r = requests.get(url)
    selector = Selector(text=r.text)
    agency_url = selector.css(".wrapper > .row a::attr(href)").get()

    if not agency_url:
        raise Exception(f"no external url found at {url}")

    revised_at_text = (
        selector.css(".wrapper .alert::text")
        .get()
        .strip()
        .replace("revisado por última vez: ", "")
    )
    revised_at = datetime.datetime.strptime(revised_at_text, "%Y-%m-%dT%H:%M:%SZ")
    normalized_url = agency_url.strip().lower().rstrip(".")
    return {"url": normalized_url, "revised_at": revised_at}


def scrape_directory(base_url):
    results = []
    r = requests.get(base_url)
    selector = Selector(text=r.text)
    for item in selector.css(".dfwp-list > li"):
        item = item.css(".item-title")
        name = item.css("::text").get()
        href = item.attrib["href"]
        url = f"https://pr.gov{href}"

        try:
            detail = get_directory_detail(url)
            results.append(
                {
                    "name": name,
                    "directory_url": url,
                    "url": detail["url"],
                    "revised_at": detail["revised_at"],
                }
            )
        except Exception as exc:
            print(exc)

    return results
