"""Define the Trekpedia class."""
import json
import re

import requests
from blessings import Terminal
from bs4 import BeautifulSoup

t = Terminal()  # pylint: disable=invalid-name


class Trekpedia:
    """Overall class to get and Parse the Wikipedia data."""

    def __init__(self, summary_url, json_template):
        """Initialize the class."""
        self.main_url = summary_url
        self.json_template = json_template
        self.series_markup = BeautifulSoup()
        self.episode_markup = BeautifulSoup()
        self.exceptions = [
            "Animated",
            "Short_Treks",
            "Picard",
            "Lower_Decks",
            "Prodigy",
            "Strange_New_Worlds",
        ]
        self.series_data = {}
        self.version = "0.0.3"

    def get_summary_data(self):
        """Get and parse the summary data."""
        self.series_markup = self.parse_url(self.main_url)

    def get_series_detail_link(self, url):
        """Return the link to the detail page for the specified series."""
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

    def get_series_details(self, series):
        """Get explicit details for each series."""
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
        series_dict["logo"] = self.get_logo(series_dict["name"])

        return series_dict

    def get_series_rows(self):
        """Return all the summary rows for the current Series."""
        tv_section = self.series_markup.find(id="Television").parent
        trek_table = tv_section.findNext("table").find("tbody")
        series_rows = trek_table.find_all("tr")[1:]
        return series_rows

    def get_series_info(self):
        """Stage 1: process main page to get and save the series info."""
        self.get_summary_data()

        # get all rows of the 'TV' table so we can parse it.
        series_rows = self.get_series_rows()

        series_all = {}
        for index, series in enumerate(series_rows, 1):
            series_all[index] = self.get_series_details(series)

        keys = series_all.keys()
        for series in keys:
            links = self.get_series_detail_link(series_all[series]["url"])
            if not links == "":
                series_all[series]["episodes_url"] = links
        self.series_data = series_all

    def get_episode_data(self, episode, headers):
        """We may grab more info in the future."""
        episode_data = {}

        # protect the next operation - if the th is not found (ie
        # tas, ds9, voy etc) just skip over this one as it is a
        # summary...
        try:
            episode_data["num_overall"] = self.clean_string(
                episode.find("th").text, brackets=True
            )
        except AttributeError:
            return None

        cells = episode.find_all("td")
        if len(cells) != len(headers):
            cells = episode.find_all(["th", "td"])

        try:
            episode_data["num_in_season"] = cells[
                headers.index("no_inseason")
            ].text
        except ValueError:
            episode_data["num_in_season"] = "n/a"

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
            episode_data["link"] = f"https://en.wikipedia.org{link_url}"
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

        return episode_data

    def get_episode_table(self, table_id):
        """Return the HTML of the episode table."""
        section = self.episode_markup.find("span", id=table_id)
        return section.findNext("table").find("tbody").find_all("tr")

    def parse_episodes(self, series, season_number, table):
        """Parse the episodes for this Season."""
        print(
            f"  -> Processing season: {season_number} "
            f"of {series['season_count']}"
        )

        # split the headers out into a list, as they change between
        # series and even seasons! at this time we also remove any
        # unicode stuff
        headers = [
            self.clean_string(
                x.text, underscores=True, brackets=True, lowercase=True
            )
            for x in table[0].find_all("th")
        ]
        # remove the overall count if it exists as this is a TH not a TD and
        # will skew the indexing later...
        try:
            headers.remove("no_overall")
        except ValueError:
            pass

        episode_list = []

        # loop over each episode. We may grab more info in the future.
        for episode in table[1:]:
            episode_data = self.get_episode_data(episode, headers)
            if episode_data:
                episode_list.append(episode_data)

        return episode_list

    def parse_series(self, series_dict):
        """Take the supplied dictionary and parses the Series."""
        index, series = series_dict

        filename = self.get_json_filename(index, series)

        self.print_season_header(series, filename)

        season_all = {}

        self.episode_markup = self.parse_url(series["episodes_url"])

        try:
            overview_table = self.episode_markup.find(
                "table", attrs={"class": "wikitable plainrowheaders"}
            )

            if not overview_table:
                # if no overview table, its a single-season for now
                table = self.get_episode_table("Episodes")
                episodes = self.parse_episodes(series, 1, table)
                # we can get the required metadata from the series_data.
                this_series = self.series_data[index]
                # now create the season object
                season_all[1] = {
                    "total": this_series["episode_count"],
                    "season_start": this_series["dates"].split("-")[0].strip(),
                    "season_end": this_series["dates"].split("-")[1].strip(),
                    "episodes": episodes,
                }
            else:
                # its a standard Series with multiple seasons.
                for season in self.get_overview_rows(overview_table):
                    try:
                        overview_row_header = season.find("th")
                        overview_row_data = season.find_all("td")
                        table_id = overview_row_header.a["href"][1:]
                        table = self.get_episode_table(table_id)

                        season_number = int(overview_row_header.text)
                    except AttributeError:
                        # fixes crash on Discovery season 2
                        continue

                    # exit the loop if we have processed the actual number of
                    # seasons. Usually this is not needed, however it is for the
                    # new series that are still in progress.
                    if season_number > int(series["season_count"]):
                        break

                    # get the episodes
                    episodes = self.parse_episodes(series, season_number, table)

                    # Get the results into a dictionary ready for JSON
                    season_all[season_number] = self.consolidate(
                        series, season_number, episodes, overview_row_data
                    )
        except AttributeError as err:
            print(
                f"{t.red}  => AttributeError, need to investigate! "
                f"({err}) at line number: "
                f"{err.__traceback__.tb_lineno}{t.normal}"
            )
            return
        self.save_json(filename, {"seasons": season_all})

    def consolidate(self, series, season_number, episodes, overview_row_data):
        """Consolidate the season data into a dict ready for JSON."""
        # some hoop-jumping to get around the Discovery Overview table layout
        try:
            _ = int(overview_row_data[1].text)
            offset = 1
        except ValueError:
            offset = 0

        season_start = self.clean_string(
            " ".join(overview_row_data[1 + offset].text.split()),
            brackets=True,
        )
        season_end = self.clean_string(
            " ".join(overview_row_data[2 + offset].text.split()),
            brackets=True,
        )
        # shameless hack to fix the Discovery season END date. Will look at
        # other options to get this right later but it does work and the value
        # will not change.
        if series["name"].lower() == "discovery" and season_number == 1:
            season_end = "February 11, 2018"
        return {
            "total": self.clean_string(
                overview_row_data[0].text, brackets=True
            ),
            "season_start": season_start,
            "season_end": season_end,
            "episodes": episodes,
        }

    def get_json_filename(self, index, series):
        """Generate and return a JSON filename from the template."""
        filename = self.json_template.format(
            index, series["name"].replace(" ", "_").lower()
        )

        return filename

    @staticmethod
    def print_season_header(series, filename):
        """Display the header for each series as it is processed."""
        print(f'Processing : {t.cyan}{t.underline}{series["name"]}{t.normal}')
        print(f"  -> Using URL : {t.green}{series['episodes_url']}{t.normal}")
        print(f"  -> Storing episodes to {t.green}'{filename}'{t.normal}")

    @staticmethod
    def get_overview_rows(summary_table):
        """Return markup for the rows in the series overview table."""
        summary_rows = summary_table.find("tbody").find_all("tr")[2:]
        return summary_rows

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

    @staticmethod
    def parse_url(url):
        """Get the specified url and parse with BeautifulSoup."""
        result = requests.get(url)
        return BeautifulSoup(result.text, "lxml")


if __name__ == "__main__":
    print(
        f"\nThis library is {t.red}not meant to be run directly{t.normal}, "
        "aborting."
    )
    print(
        f"Please run the {t.cyan}'generate_trek.py'{t.normal} file instead!\n"
    )
