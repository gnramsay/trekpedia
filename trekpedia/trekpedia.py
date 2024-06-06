"""Define the Trekpedia class."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag
from rich import print

from trekpedia.helpers import (  # pylint: disable=redefined-builtin
    clean_string,
    get_overview_rows,
    parse_url,
    print_season_header,
    save_json,
)

if TYPE_CHECKING:
    from requests import Response


class Trekpedia:
    """Overall class to get and Parse the Wikipedia data."""

    def __init__(self, summary_url: str, json_template: str) -> None:
        """Initialize the class."""
        self.main_url: str = summary_url
        self.json_template: str = json_template
        self.series_markup: BeautifulSoup = BeautifulSoup()
        self.episode_markup: BeautifulSoup = BeautifulSoup()
        self.exceptions: list[str] = [
            "Animated",
            "Short_Treks",
            "Picard",
            "Lower_Decks",
            "Prodigy",
            "Strange_New_Worlds",
        ]
        self.series_data: dict = {}
        self.version: str = "0.0.7"

    def get_summary_data(self) -> None:
        """Get and parse the summary data."""
        self.series_markup = parse_url(self.main_url)

    def get_series_detail_link(self, url: str) -> str:
        """Return the link to the detail page for the specified series."""
        series_page: Response = requests.get(url, timeout=10)
        bss: BeautifulSoup = BeautifulSoup(series_page.text, "lxml")
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

    def get_logo(self, url: str) -> str:
        """Return the logo for the specified series.

        We get this from the individual series page since they have removed it
        from the main page.
        """
        series_data = parse_url(url)
        image_url = series_data.find("td", attrs={"class": "infobox-image"})
        if image_url:
            return f"https:{image_url.find("img")["src"]}"

        return ""

    def get_series_details(self, series) -> dict[str, Any]:
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
        series_dict["logo"] = self.get_logo(series_dict["url"])

        return series_dict

    def get_series_rows(self) -> Tag | None:
        """Return all the summary rows for the current Series."""
        try:
            tv_section = cast(
                Tag | None, self.series_markup.find(id="Television")
            )
            if tv_section and tv_section.parent:
                trek_table = tv_section.parent.findNext("table").find("tbody")  # type: ignore
                rows = trek_table.find_all("tr")  # type: ignore
                return rows[1:]  # type: ignore
        except AttributeError:
            return None

        return None

    def get_series_info(self) -> None:
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
            if links != "":
                series_all[series]["episodes_url"] = links
        self.series_data = series_all

    def get_episode_data(self, episode, headers, last_episode):
        """We may grab more info in the future."""
        episode_data = {}

        # protect the next operation - if the th is not found (ie
        # tas, ds9, voy etc) just skip over this one as it is a
        # summary...
        try:
            episode_data["num_overall"] = clean_string(
                episode.find("th").text, brackets=True
            )
        except AttributeError:
            return None

        cells = episode.find_all("td")
        if len(cells) != len(headers):
            # this area is where we need to fix errors caused by the way they
            # are now handling double-episodes in many Series.
            # This is a hack to fix the issue, and will be cleaned up very soon!
            if len(cells) == 1:
                # we only have no_in_season
                cells.insert(
                    1,
                    BeautifulSoup(f"<td>{last_episode['title']}</td>", "lxml"),
                )
                cells.insert(
                    2,
                    BeautifulSoup(
                        f"<td>{last_episode['director']}</td>", "lxml"
                    ),
                )
                cells.insert(
                    3,
                    BeautifulSoup(
                        f"<td>{last_episode['air_date']}</td>", "lxml"
                    ),
                )

            if len(cells) in [2, 3]:
                # we only have no_in_season and original_release_date
                cells.insert(
                    1,
                    BeautifulSoup(f"<td>{last_episode['title']}</td>", "lxml"),
                )
                cells.insert(
                    2,
                    BeautifulSoup(
                        f"<td>{last_episode['director']}</td>", "lxml"
                    ),
                )
            elif len(cells) == 4:
                # we have everything except the title
                cells.insert(
                    1,
                    BeautifulSoup(f"<td>{last_episode['title']}</td>", "lxml"),
                )

        try:
            episode_data["num_in_season"] = cells[
                headers.index("no_inseason")
            ].text
        except ValueError:
            episode_data["num_in_season"] = episode_data["num_overall"]

        # get the required data using the header indexes, otherwise
        # will mess up on ds9-s4 and later since they add new
        # columns to the table.
        episode_data["title"] = clean_string(
            cells[headers.index("title")].text.replace('"', ""),
            brackets=True,
        )
        try:
            link_url = cells[headers.index("title")].a["href"]
            if "cite_note" in link_url:
                raise TypeError()
            episode_data["link"] = f"https://en.wikipedia.org{link_url}"
        except TypeError:
            if last_episode and episode_data["title"] == last_episode["title"]:
                # for multi-part episodes, the link is only on the first so we
                # need to copy it over to the second.
                episode_data["link"] = last_episode["link"]
            else:
                # set the link url to an empty string...
                episode_data["link"] = ""

        episode_data["director"] = clean_string(
            cells[headers.index("directed_by")].text, brackets=True
        )

        # air date needs fixed as is listed differently in later
        # series...
        airdate_idx = [
            i
            for i, item in enumerate(headers)
            if re.search("^original.*date$", item)
            or re.search("^paramount.*date$", item)
        ][0]
        try:
            episode_data["air_date"] = clean_string(
                cells[airdate_idx].text, brackets=True
            )
        except IndexError:
            episode_data["air_date"] = clean_string(
                cells[-1].text, brackets=True
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
            clean_string(
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
        # we send the previous episode back to it to handle the way some
        # split-episodes are markedup
        for episode in table[1:]:
            episode_data = self.get_episode_data(
                episode, headers, episode_list[-1] if episode_list else []
            )
            if episode_data:
                episode_list.append(episode_data)

        return episode_list

    def parse_series(self, series_dict: tuple[int, dict]) -> None:
        """Take the supplied dictionary and parses the Series."""
        index, series = series_dict

        filename = self.get_json_filename(index, series)

        print_season_header(series, filename)

        season_all = {}

        self.episode_markup = parse_url(series["episodes_url"])

        try:
            overview_table: Tag | None = self.episode_markup.find(
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
                for season in get_overview_rows(overview_table):
                    try:
                        overview_row_header = season.find("th")
                        overview_row_data = season.find_all("td")
                        table_id = overview_row_header.a["href"][1:]
                        table = self.get_episode_table(table_id)

                        season_number = int(
                            "".join(
                                re.split(r"[\[\]]", overview_row_header.text)[
                                    ::2
                                ]
                            )
                        )

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
                "[red]  => AttributeError, need to investigate! "
                f"({err}) at line number: {err.__traceback__.tb_lineno}"
            )
            return
        save_json(filename, {"seasons": season_all})

    def consolidate(
        self, series, season_number: int, episodes, overview_row_data
    ) -> dict[str, Any]:
        """Consolidate the season data into a dict ready for JSON."""
        # some hoop-jumping to get around the Discovery Overview table layout
        try:
            _ = int(overview_row_data[1].text)
            offset = 1
        except ValueError:
            offset = 0

        season_start = clean_string(
            " ".join(overview_row_data[1 + offset].text.split()),
            brackets=True,
        )
        season_end = clean_string(
            " ".join(overview_row_data[2 + offset].text.split()),
            brackets=True,
        )
        # shameless hack to fix the Discovery season END date. Will look at
        # other options to get this right later but it does work and the value
        # will not change.
        if series["name"].lower() == "discovery" and season_number == 1:
            season_end = "February 11, 2018"
        return {
            "total": clean_string(overview_row_data[0].text, brackets=True),
            "season_start": season_start,
            "season_end": season_end,
            "episodes": episodes,
        }

    def get_json_filename(self, index: int, series: dict[str, str]) -> str:
        """Generate and return a JSON filename from the template."""
        return self.json_template.format(
            index, series["name"].replace(" ", "_").lower()
        )


if __name__ == "__main__":
    print(
        "\nThis library is [red]not meant to be run directly[/red], "
        "aborting."
    )
    print("Please run the [cyan]'generate_trek.py'[/cyan] file instead!\n")
