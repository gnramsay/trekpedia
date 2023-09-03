"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""
import sys

import colorama
from rich import print  # pylint: disable=redefined-builtin

from lib.trekpedia import Trekpedia

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"
JSON_TEMPLATE = "output/star_trek_series_{}_{}_episodes.json"


# ---------------------------------------------------------------------------- #
#                                   Main Code                                  #
# ---------------------------------------------------------------------------- #
def main(_args):
    """Run the main program, parse and save data from Wikipedia."""
    try:
        trekpedia = Trekpedia(summary_url=MAIN_URL, json_template=JSON_TEMPLATE)

        colorama.init()

        print(
            "Trekpedia : Parse '[cyan]Star Trek[/cyan]' "
            "data from the Web and save as JSON.\n"
        )
        print("\u00a9 2023 Grant Ramsay <grant@gnramsay.com>\n")
        print(f"Version {trekpedia.version}\n")

        # ---- get the series info and save to a JSON file for later use. ---- #
        print("Getting Series Data ... ", end="")
        trekpedia.get_series_info()
        trekpedia.save_json(
            "output/star_trek_series_info.json", trekpedia.series_data
        )
        print("Done!\n")

        # ----------- loop through each series and parse then save ----------- #
        for series_data in trekpedia.series_data.items():
            if series_data[0] not in [11]:
                trekpedia.parse_series(series_data)
    except KeyboardInterrupt:
        print("\r", " " * 80)
        print("[red][bold]Escape Pressed, processing ABORTED.\n")


# ---------------------------------------------------------------------------- #
#              Actually run our code, unless we have been imported             #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main(sys.argv[1:])
