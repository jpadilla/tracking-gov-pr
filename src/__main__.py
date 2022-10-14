import datetime
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from sqlite_utils import Database

from .agencies import scrape_agencies
from .checks import check_websites
from .towns import scrape_towns

DATA_BASE_PATH = Path("./data")
DATASETTE_BASE_PATH = Path("./datasette")
AGENCIES_DATA_FILE = DATA_BASE_PATH / "agencies.json"
TOWNS_DATA_FILE = DATA_BASE_PATH / "towns.json"
AMASS_ENUM_DATA_FILE = DATA_BASE_PATH / "amass-enum.jsonl"
CHECKS_DATA_PATH = DATA_BASE_PATH / "checks"


# Date format used for data files
DATE_FORMAT_STR = "%Y%m%d%H"


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


def recreate_database():
    db = Database(DATASETTE_BASE_PATH / "data.db", recreate=True)

    with open(AGENCIES_DATA_FILE) as f:
        data = json.load(f)
        db.table("agencies").insert_all([{**result} for result in data])

    with open(TOWNS_DATA_FILE) as f:
        data = json.load(f)
        db.table("towns").insert_all([{**result} for result in data])

    with open(AMASS_ENUM_DATA_FILE) as f:
        for line in f:
            data = json.loads(line)
            db.table("discoveries").insert(data)

    for entry in os.scandir(CHECKS_DATA_PATH):
        if not entry.is_file():
            continue

        with open(entry.path) as file:
            data = json.load(file)
            created_at = datetime.datetime.strptime(
                entry.name.split(".json")[0], DATE_FORMAT_STR
            )
            db.table("website_checks").insert_all(
                [{**result, **{"created_at": created_at}} for result in data]
            )


def main():
    args = sys.argv[1:]
    usage = "Usage: tracking-gov-pr [scrape|check-websites|recreate-db|root-domains]"

    if len(args) < 1:
        print(usage)
        exit(1)

    action = args[0]

    if action == "scrape":
        agencies = scrape_agencies()
        with open(AGENCIES_DATA_FILE, "w") as f:
            json.dump(agencies, f, cls=JSONEncoder, indent=2)

        towns = scrape_towns()
        with open(TOWNS_DATA_FILE, "w") as f:
            json.dump(towns, f, cls=JSONEncoder, indent=2)

    elif action == "check-websites":
        with open(AGENCIES_DATA_FILE) as f:
            agencies = json.load(f)

        with open(TOWNS_DATA_FILE) as f:
            towns = json.load(f)

        agencies_results = check_websites(agencies)
        towns_results = check_websites(towns)
        results = agencies_results + towns_results
        now = datetime.datetime.utcnow()
        filename = now.strftime(DATE_FORMAT_STR) + ".json"
        with open(CHECKS_DATA_PATH / filename, "w") as f:
            json.dump(results, f, cls=JSONEncoder, indent=2)

    elif action == "recreate-db":
        recreate_database()

    elif action == "root-domains":
        root_domains = {"pr.gov", "gobierno.pr"}
        urls = set()

        with open(AGENCIES_DATA_FILE) as f:
            agencies = json.load(f)
            urls = urls | {prop["url"] for prop in agencies}

        with open(TOWNS_DATA_FILE) as f:
            towns = json.load(f)
            urls = urls | {prop["url"] for prop in towns}

        for url in urls:
            hostname = urlparse(url).hostname
            if hostname.startswith("www."):
                root_domains.add(hostname.replace("www.", ""))
            else:
                root_domains.add(hostname)

        for root_domain in sorted(root_domains):
            print(root_domain)

    else:
        print(usage)
        exit(1)


if __name__ == "__main__":
    main()
