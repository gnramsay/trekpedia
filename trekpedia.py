"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""
import json
import re

import requests
from bs4 import BeautifulSoup

# don't truncate Pandas.DataFrame cell contents when displaying.
# pd.set_option("display.max_colwidth", None)

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"


def parse_url(url):
    """Get the url and parse with BeautifulSoup."""
    result = requests.get(url)
    return BeautifulSoup(result.text, "lxml")


def get_logo(name, soup):
    """Return the logo for the specified series.

    We do this from the main page because the logo is not in the episode page,
    or not good quality.
    """
    # short treks has no logo on this page, return empty string for now...
    if name == "Short Treks":
        return ""
    span = soup.find(
        "span",
        attrs={"class": "mw-headline"},
        id=re.compile(f"{name.replace(' ', '_')}_\("),
    )
    logo = span.findNext("img", attrs={"class": "thumbimage"})["src"]
    logo_url = f"https:{logo}"
    return logo_url


def get_season_links(url):
    """Return a list of season links for the specified series."""
    # a list of series that need different handling...
    exceptions = ["Animated", "Short_Treks", "Picard", "Lower_Decks", "Prodigy"]
    series_page = requests.get(url)
    bss = BeautifulSoup(series_page.text, "lxml")
    # get all the Heading rows depending on season. Wikipedia is not
    # consistent...
    if "Enterprise" in url:
        headings = bss.find_all("h3")
    elif any(x in url for x in exceptions):
        # specific cases, they have episode data in the original page so just
        # return that...
        return url
    else:
        headings = bss.find_all("h2")
    for heading in headings:
        headline = heading.find(
            "span", attrs={"class": "mw-headline"}, id=re.compile("pisode")
        )
        if headline is not None:
            try:
                episodes = headline.findNext("div", attrs={"role": "note"}).a[
                    "href"
                ]
            except AttributeError:
                episodes = ""
    return f"https://en.wikipedia.org{episodes}"


# get the parsed page.
bs = parse_url(MAIN_URL)

# get all rows of the 'TV' table so we can parse it.
tv = bs.find(id="Television").parent
trek_table = tv.findNext("table").find("tbody")
series_rows = trek_table.find_all("tr")[1:]

# create a list, containing dictionary for each season.
# also add an ID so we can link it to the series data later.
series_all = {}
for index, series in enumerate(series_rows, 1):
    series_dict = {}
    series_dict["name"] = series.th.a.text
    series_dict["url"] = f'https://en.wikipedia.org{series.th.a["href"]}'
    series_dict["season_count"] = series.find_all("td")[0].text
    series_dict["episode_count"] = series.find_all("td")[1].text
    series_dict["episodes_url"] = ""
    dates = (
        series.find_all("td")[2]
        .text.split("(")[0]
        .strip()
        .replace("\u2013", "-")
    )
    # get the unicode stuff out of the string...
    dates = " ".join(dates.split())
    series_dict["dates"] = dates
    series_dict["logo"] = get_logo(series_dict["name"], bs)

    series_all[index] = series_dict

keys = series_all.keys()
for series in keys:
    links = get_season_links(series_all[series]["url"])
    if not links == "":
        series_all[series]["episodes_url"] = links

# save this list to a JSON file.
with open("output/star_trek_series_info.json", "w", encoding="utf-8") as f:
    json.dump(series_all, f, ensure_ascii=False, indent=4)
print("Done.")
