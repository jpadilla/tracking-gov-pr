from urllib.parse import urlparse

import requests


def check_websites(websites):
    responses = []
    variations = []

    for prop in websites:
        prop_variation = dict(prop)
        prop_variation["variation"] = False
        prop_variation["url"] = urlparse(prop["url"])

        variations.append(prop_variation)

        if prop_variation["url"].scheme == "http":
            prop_variation = dict(prop_variation)
            prop_variation["url"] = prop_variation["url"]._replace(scheme="https")
            prop_variation["variation"] = True
            variations.append(prop_variation)
        elif prop_variation["url"].scheme == "https":
            prop_variation = dict(prop_variation)
            prop_variation["url"] = prop_variation["url"]._replace(scheme="http")
            prop_variation["variation"] = True
            variations.append(prop_variation)

        if prop_variation["url"].netloc.startswith("www."):
            prop_variation = dict(prop_variation)
            nonwww_url = prop_variation["url"].netloc.replace("www.", "")
            prop_variation["url"] = prop_variation["url"]._replace(netloc=nonwww_url)
            prop_variation["variation"] = True
            variations.append(prop_variation)

            if prop_variation["url"].scheme == "http":
                prop_variation = dict(prop_variation)
                prop_variation["url"] = prop_variation["url"]._replace(scheme="https")
                prop_variation["variation"] = True
                variations.append(prop_variation)
            elif prop_variation["url"].scheme == "https":
                prop_variation = dict(prop_variation)
                prop_variation["url"] = prop_variation["url"]._replace(scheme="http")
                prop_variation["variation"] = True
                variations.append(prop_variation)

    for prop in variations:
        prop_url = prop["url"].geturl()

        response = {
            "name": prop["name"],
            "variation": prop["variation"],
            "request_url": prop_url,
        }

        try:
            r = requests.get(prop_url, timeout=(3.05, 7))
            response.update(
                {
                    "response_url": r.url,
                    "response_redirects": len(r.history),
                    "response_status_code": r.status_code,
                    "exception": None,
                }
            )
        except requests.exceptions.RequestException as exc:
            response.update(
                {
                    "response_url": (
                        exc.response.url if exc.response else exc.request.url
                    ),
                    "exception": type(exc).__name__,
                }
            )
        except Exception as exc:
            response.update({"exception": type(exc).__name__})

        print(response)
        responses.append(response)

    return responses
