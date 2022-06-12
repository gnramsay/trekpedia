"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""
import json
import re

import requests
from bs4 import BeautifulSoup

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"
JSON_TEMPLATE = "output/star_trek_series_{}_{}_episodes.json"


# ---------------------------------------------------------------------------- #
#                          Define the TrekPredia Class                         #
# ---------------------------------------------------------------------------- #
class TrekPedia:
    """Overall class to get and Parse the Wikipedia data."""

    def __init__(self):
        """Initialize the class."""
        self.main_url = MAIN_URL
        self.series_markup = BeautifulSoup()
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

    def parse_url(self, url):
        """Get the specified url and parse with BeautifulSoup."""
        result = requests.get(url)
        # self.series_summary_bs = BeautifulSoup(result.text, "lxml")
        return BeautifulSoup(result.text, "lxml")

    def get_summary_data(self):
        """Get and parse the summary data."""
        self.series_markup = self.parse_url(self.main_url)

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
        span = self.series_markup.find(
            "span",
            attrs={"class": "mw-headline"},
            id=re.compile(rf"{series.replace(' ', '_')}_\("),
        )
        logo = span.findNext("img", attrs={"class": "thumbimage"})["src"]
        logo_url = f"https:{logo}"
        return logo_url

    def get_series_info(self):
        """Start the process to get and save the series info."""
        self.get_summary_data()

        # get all rows of the 'TV' table so we can parse it.
        tv_section = self.series_markup.find(id="Television").parent
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

    def parse_series(self, series_dict):
        """Take the supplied dictionary and parses the Series."""
        index, series = series_dict

        # skip series with markup that is too screwed up for now...
        if series["name"].lower() in ["prodigy"]:
            return

        print(f'Processing : {series["name"]}')
        filename = JSON_TEMPLATE.format(
            index, series["name"].replace(" ", "_").lower()
        )
        print(f"  -> Using URL : {series['episodes_url']}")
        print(f"  -> Storing episodes to '{filename}'")

        season_final = {}
        season_all = {}

        episode_markup = self.parse_url(series["episodes_url"])

        try:
            # find the episode summary table, will be the first table with the
            # below classes in the document
            summary_table = episode_markup.find(
                "table", attrs={"class": "wikitable plainrowheaders"}
            )

            if not summary_table:
                print("   x No Summary Table found, skipping this Series ...")
                return

            summary_rows = summary_table.find("tbody").find_all("tr")[2:]

            for season in summary_rows:
                season_data = {}
                link = season.find("th")
                cells = season.find_all("td")

                try:
                    season_number = int(link.text)
                except AttributeError:
                    continue

                # exit the loop if we have processed the actual number of
                # seasons. Usually this is not needed, however it is for the
                # new series that are still in progress.
                if season_number > int(series["season_count"]):
                    break

                print(
                    f"  -> Processing season: {season_number} "
                    f"of {series['season_count']}"
                )
                season_id = link.a["href"][1:]
                season_data["total"] = self.clean_string(
                    cells[0].text, brackets=True
                )
                season_data["season_start"] = self.clean_string(
                    " ".join(cells[1].text.split()), brackets=True
                )
                season_data["season_end"] = self.clean_string(
                    " ".join(cells[2].text.split()), brackets=True
                )
                season_data["episodes"] = []

                # now get the episodes for each season
                section = episode_markup.find("span", id=season_id)
                table = section.findNext("table").find("tbody").find_all("tr")

                # split the headers out into a list, as they change between
                # series and even seasons! at this time we also remove any
                # unicode stuff
                hdr_list = table[0].find_all("th")
                headers = [
                    self.clean_string(
                        x.text, underscores=True, brackets=True, lowercase=True
                    )
                    for x in hdr_list
                ]
                # remove the overall count as this is a TH not a TD and will
                # skew the indexing later...
                headers.remove("no_overall")

                # 'episodes' will consist of one row for each episode, except
                # ds9 and voy who also put summary after each one and confuse
                # things!
                episodes = table[1:]

                episode_list = []

                # loop over each episode. We may grab more info in the future.
                for episode in episodes:
                    episode_data = {}
                    # protect the next operation - if the th is not found (ie
                    # tas, ds9, voy) just skip over this one as it is a
                    # summary...
                    try:
                        episode_data["num_overall"] = self.clean_string(
                            episode.find("th").text, brackets=True
                        )
                    except AttributeError:
                        continue
                    cells = episode.find_all("td")
                    episode_data["num_in_season"] = cells[
                        headers.index("no_inseason")
                    ].text

                    # need to do some tweaking, sometimes the first episode is
                    # in 2 parts need to detect this and split them. Alternative
                    # is to have a hard-coded list, as it happens very rarely.

                    # get the required data using the header indexes, otherwise
                    # will mess up on ds9-s4 and later since they add new
                    # columns to the table.
                    episode_data["title"] = self.clean_string(
                        cells[headers.index("title")].text.replace('"', ""),
                        brackets=True,
                    )
                    try:
                        link_url = cells[headers.index("title")].a["href"]
                        if "cite_note" in link_url:
                            raise TypeError()
                        episode_data[
                            "link"
                        ] = f"https://en.wikipedia.org{link_url}"
                    except TypeError:
                        # set the link url to an empty string...
                        episode_data["link"] = ""

                    episode_data["director"] = self.clean_string(
                        cells[headers.index("directed_by")].text, brackets=True
                    )

                    # air date needs fixed as is listed differently in later
                    # series...
                    airdate_idx = [
                        i
                        for i, item in enumerate(headers)
                        if re.search("^original.*date$", item)
                    ][0]
                    episode_data["air_date"] = self.clean_string(
                        cells[airdate_idx].text, brackets=True
                    )

                    episode_list.append(episode_data)

                # consolidate into a format suitable for writing to JSON
                season_data["episodes"] = episode_list
                season_all[season_number] = season_data
                season_final["seasons"] = season_all
        except AttributeError as err:
            print(
                f"  => ERROR, need to investigate! "
                f"({err}) at line number: {err.__traceback__.tb_lineno}"
            )
            return
        self.save_json(filename, season_final)

    @staticmethod
    def save_json(filename, data):
        """Save the specified data as a JSON file to the specified location."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def clean_string(
        dirty_string, underscores=False, brackets=False, lowercase=False
    ):
        """Take a string and remove underscores, spaces etc as required."""
        if underscores:
            dirty_string = (
                dirty_string.replace(" ", "_")
                .replace(".", "_")
                .replace("__", "_")
            )
        if brackets:
            dirty_string = "".join(re.split(r"\(|\)|\[|\]", dirty_string)[::2])
        if lowercase:
            dirty_string = dirty_string.lower()
        return " ".join(dirty_string.split())


# ---------------------------------------------------------------------------- #
#                                   Main Code                                  #
# ---------------------------------------------------------------------------- #
trekpedia = TrekPedia()

print(
    "Trekpedia : Parse 'Star Trek' data from the Web and save as JSON.\n"
    "(C)2022 Grant Ramsay (grant@gnramsay.com)\n"
    f"Version {trekpedia.version}\n"
)

# -------- get the series info and save to a JSON file for later use. -------- #
print("Getting Series Data...", end="")
trekpedia.get_series_info()
trekpedia.save_json("output/star_trek_series_info.json", trekpedia.series_data)
print(" Done!\n")

# -------------------- loop through each series and parse -------------------- #
for series_data in trekpedia.series_data.items():

    trekpedia.parse_series(series_data)
