from .scrape import scrape_directory


def scrape_towns():
    return scrape_directory(
        "https://pr.gov/Directorios/Pages/DirectoriodeMunicipios.aspx"
    )
