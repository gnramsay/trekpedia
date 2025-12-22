"""Trekpedia JSON.

Produce JSON dumps of Star Trek data suitable for adding to an API.
"""

from rich import print as rprint

from trekpedia import JSON_TEMPLATE, MAIN_URL, Trekpedia, save_json


# ---------------------------------------------------------------------------- #
#                                   Main Code                                  #
# ---------------------------------------------------------------------------- #
def main() -> None:
    """Run the main program, parse and save data from Wikipedia."""
    try:
        trekpedia = Trekpedia(summary_url=MAIN_URL, json_template=JSON_TEMPLATE)

        rprint(
            "Trekpedia : Parse '[cyan]Star Trek[/cyan]' "
            "data from the Web and save as JSON.\n"
        )
        rprint("\u00a9 2023 Grant Ramsay <grant@gnramsay.com>\n")
        rprint(f"Version {trekpedia.version}\n")

        # ---- get the series info and save to a JSON file for later use. ---- #
        rprint("Getting Series Data ... ", end="")
        trekpedia.get_series_info()
        save_json("output/star_trek_series_info.json", trekpedia.series_data)
        rprint("Done!\n")

        # ----------- loop through each series and parse then save ----------- #
        for series_data in trekpedia.series_data.items():
            # for now we ignore 'Prodigy' until I re-visit the code.
            if series_data[0] not in [11]:
                trekpedia.parse_series(series_data)
    except KeyboardInterrupt:
        rprint("\r", " " * 80)
        rprint("[red][bold]Escape Pressed, processing ABORTED.\n")


# ---------------------------------------------------------------------------- #
#              Actually run our code, unless we have been imported             #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
