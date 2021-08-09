# Trekpedia

Star Trek TV/Film episode database scraped from web sources, with a Django-based
Backend API and a React Frontend. This is a work in progress which will follow
the path `Scraper` -> `Backend` -> `Frontend`.

All copyright to the 'Star Trek' name belongs to [ViacomCBS][viacomcbs]. All
data in this project has been mined from the [Wikipedia Star Trek page][wst] and
associated subpages under the [Fair Use][fup] principal.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Development

First development of the scraper is being carried out using Jupyter Notebooks.
These can be found in the `notebooks` folder under the `backend` folder.

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

## Installation

To Write as code progresses.

## Deployment

As Above

[viacomcbs]:https://www.viacomcbs.com
[wst]: https://en.wikipedia.org/wiki/Star_Trek
[fup]: https://en.wikipedia.org/wiki/Fair_use#Text_and_data_mining
