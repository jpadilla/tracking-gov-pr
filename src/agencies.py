from .scrape import scrape_directory


def scrape_agencies():
    return scrape_directory(
        "https://pr.gov/Directorios/Pages/DirectoriodeAgencias.aspx"
    )
