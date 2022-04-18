# Trekpedia JSON

Star Trek TV/Film episode database scraped from web sources and provided in JSON
format.

Currently really just a geek project for me to get familiar with Python
web-scraping, and provide data for API development.

All copyright to the 'Star Trek' name and data belongs to
[ViacomCBS][viacomcbs].

All data in this project has been mined from the [Wikipedia Star Trek page][wst]
and associated subpages under the [Fair Use][fup] principal.

The license below only applies to the **SOURCE CODE**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Development

First development of the scraper is being carried out using [Jupyter
Notebooks][jupyter] . These can be found in the `notebooks` folder.

### Current progress

For the moment, only scraping the TV series data, leaving film data until later
iterations.

#### `trekpedia-stage-1.ipynb [COMPLETE]`

* Scrape the main Wikipedia Star Trek page and create a JSON file containing
  Series names and metadata (number of seasons, number of episodes etc.) This
  metadata will probably include series summary and other data in future
  iterations (not necessarily from Wikipedia)

#### `trekpedia-stage-2.ipynb [IN PROGRESS]`

* Take the JSON file created in the previous step, and dump the episode names
  for each series to a separate json file, with some Series metadata
  * Discovery and Prodigy need special treatment as their markup seems to follow
    no logic know to man, God or Vulcan.

#### `trekpedia.py [IN PROGRESS]`

* First work towards moving from Jupyter notebooks to a standard Python script

## Produced Files

A work-in-progress version of the derived data is available in the
[output](output) directory.

This contains:

* [star_trek_series_info.json](output/star_trek_series_info.json)
  which lists info and links for each series only, and is used as the basis for
  getting the individual series data.
* One individual JSON file for each Star Trek incarnation (Currently 10 as we
  are skipping Prodigy for now).

A tarball is included in the [releases](releases) folder and attached to each
GitHuB release.

## Installation

To Write as code progresses.

## Deployment

As Above

[viacomcbs]:https://www.viacomcbs.com
[wst]: https://en.wikipedia.org/wiki/Star_Trek
[fup]: https://en.wikipedia.org/wiki/Fair_use#Text_and_data_mining
[jupyter]: https://jupyter.org/
