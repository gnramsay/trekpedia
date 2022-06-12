"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""
import json
import re

import requests
from bs4 import BeautifulSoup

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"


class TrekPedia:
    """Overall class to get and Parse the Wikipedia data."""

    def __init__(self):
        """Initialize the class."""
        self.main_url = MAIN_URL
        self.series_summary_bs = BeautifulSoup()
        self.exceptions = [
            "Animated",
            "Short_Treks",
            "Picard",
            "Lower_Decks",
            "Prodigy",
            "Strange_New_Worlds",
        ]
        self.series_data = {}
        self.version = "0.0.1"

    def parse_url(self):
        """Get the url and parse with BeautifulSoup."""
        result = requests.get(self.main_url)
        self.series_summary_bs = BeautifulSoup(result.text, "lxml")

    def get_season_links(self, url):
        """Return a list of season links for the specified series."""
        series_page = requests.get(url)
        bss = BeautifulSoup(series_page.text, "lxml")
        # get all the Heading rows depending on season. Wikipedia is not
        # consistent...
        if "Enterprise" in url:
            headings = bss.find_all("h3")
        elif any(x in url for x in self.exceptions):
            # specific cases, they have episode data in the original page so
            # just return that...
            return url
        else:
            headings = bss.find_all("h2")
        for heading in headings:
            headline = heading.find(
                "span", attrs={"class": "mw-headline"}, id=re.compile("pisode")
            )
            if headline is not None:
                try:
                    episodes = headline.findNext(
                        "div", attrs={"role": "note"}
                    ).a["href"]
                except AttributeError:
                    episodes = ""
        return f"https://en.wikipedia.org{episodes}"

    def get_logo(self, series):
        """Return the logo for the specified series.

        We do this from the main page because the logo is not in the episode
        page, or not good quality.
        """
        # short treks has no logo on this page, return empty string for now...
        if series == "Short Treks":
            return ""
        span = self.series_summary_bs.find(
            "span",
            attrs={"class": "mw-headline"},
            id=re.compile(rf"{series.replace(' ', '_')}_\("),
        )
        logo = span.findNext("img", attrs={"class": "thumbimage"})["src"]
        logo_url = f"https:{logo}"
        return logo_url

    def save_json(self, filename, data):
        """Save the specified data as a JSON file to the specified location."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_series_info(self):
        """Start the process to get and save the series info."""
        self.parse_url()

        # get all rows of the 'TV' table so we can parse it.
        tv_section = self.series_summary_bs.find(id="Television").parent
        trek_table = tv_section.findNext("table").find("tbody")
        series_rows = trek_table.find_all("tr")[1:]

        series_all = {}
        for index, series in enumerate(series_rows, 1):
            series_dict = {}
            series_dict["name"] = series.th.a.text
            series_dict[
                "url"
            ] = f'https://en.wikipedia.org{series.th.a["href"]}'
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
            series_dict["logo"] = self.get_logo(series_dict["name"])

            series_all[index] = series_dict

        keys = series_all.keys()
        for series in keys:
            links = self.get_season_links(series_all[series]["url"])
            if not links == "":
                series_all[series]["episodes_url"] = links
        self.series_data = series_all


# --------------------------------- Main Code -------------------------------- #
trekpedia = TrekPedia()

print(
    "Trekpedia : Parse 'Star Trek' data from the Web and save as JSON.\n"
    "(c)2022 Grant Ramsay (grant@gnramsay.com)\n"
    f"Version {trekpedia.version}\n"
)

print("Getting Series Data...", end="")
# get the series info and save to a JSON file for later use.
trekpedia.get_series_info()
trekpedia.save_json("output/star_trek_series_info.json", trekpedia.series_data)
print("Done!\n")
