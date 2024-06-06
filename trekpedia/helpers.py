"""Helper functions for Trekpedia."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests
from bs4 import BeautifulSoup
from rich import print  # pylint: disable=redefined-builtin

if TYPE_CHECKING:
    from requests import Response


def print_season_header(series: dict[str, str], filename: str) -> None:
    """Display the header for each series as it is processed."""
    print(f'Processing : [bold][underline]{series["name"]}')
    print(f"  -> Using URL : [green]{series['episodes_url']}")
    print(f"  -> Storing episodes to [green]'{filename}'")


def get_overview_rows(summary_table):
    """Return markup for the rows in the series overview table."""
    return summary_table.find("tbody").find_all("tr")[2:]


def save_json(filename: str, data: dict[str, Any]) -> None:
    """Save the specified data as a JSON file to the specified location."""
    with Path(filename).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def clean_string(
    dirty_string: str,
    *,
    underscores: bool = False,
    brackets: bool = False,
    lowercase: bool = False,
) -> str:
    """Take a string and remove underscores, spaces etc as required."""
    if underscores:
        dirty_string = (
            dirty_string.replace(" ", "_").replace(".", "_").replace("__", "_")
        )
    if brackets:
        dirty_string = "".join(re.split(r"[\(\)\[\]]", dirty_string)[::2])
    if lowercase:
        dirty_string = dirty_string.lower()
    return " ".join(dirty_string.split())


def parse_url(url: str) -> BeautifulSoup:
    """Get the specified url and parse with BeautifulSoup."""
    result: Response = requests.get(url, timeout=10)
    return BeautifulSoup(result.text, "lxml")
