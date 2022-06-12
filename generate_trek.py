"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""
import sys

import colorama
from blessings import Terminal

from trekpedia import Trekpedia

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"
JSON_TEMPLATE = "output/star_trek_series_{}_{}_episodes.json"


# ---------------------------------------------------------------------------- #
#                                   Main Code                                  #
# ---------------------------------------------------------------------------- #
def main(_args):
    """Run the main program, parse and save data from Wikipedia."""
    trekpedia = Trekpedia(MAIN_URL, JSON_TEMPLATE)

    colorama.init()
    t = Terminal()  # pylint: disable=invalid-name

    print(
        f"Trekpedia : Parse '{t.cyan}Star Trek{t.normal}' "
        "data from the Web and save as JSON.\n"
    )
    print("(C)2022 Grant Ramsay (grant@gnramsay.com)\n")
    print(f"Version {trekpedia.version}\n")

    # ------ get the series info and save to a JSON file for later use. ------ #
    print("Getting Series Data...", end="")
    trekpedia.get_series_info()
    trekpedia.save_json(
        "output/star_trek_series_info.json", trekpedia.series_data
    )
    print(" Done!\n")

    # ------------- loop through each series and parse then save ------------- #
    for series_data in trekpedia.series_data.items():
        trekpedia.parse_series(series_data)


# ---------------------------------------------------------------------------- #
#                         Wrapper to run the main code                         #
# ---------------------------------------------------------------------------- #
def run():
    """Call :func:`main` passing any CLI arguments."""
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------------------- #
#              Actually run our code, unless we have been imported             #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    run()
