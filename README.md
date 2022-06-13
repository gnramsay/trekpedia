# Trekpedia JSON

Star Trek TV/Film episode database scraped from web sources and provided in JSON
format.

Currently really just a geek project for me to get familiar with Python
web-scraping, and provide data for API development.

for an API specifically written to use this data, see [trekpedia-api-rails][rails-api]

All copyright to the 'Star Trek' name and data belongs to
[ViacomCBS][viacomcbs].

All data in this project has been mined from the [Wikipedia Star Trek page][wst]
and associated subpages under the [Fair Use][fup] principal.

The license below only applies to the **SOURCE CODE**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Development

Original development of the scraper was carried out using [Jupyter
Notebooks][jupyter] . These can be found in the `notebooks` folder.

However, I have migrated this base work into the pure Python in the
[trekpedia.py](trekpedia.py) file, and all further work will be carried out
there.

### Current progress

For the moment, I am only scraping the TV series data, leaving film data until
later iterations.

#### `generate_trek.py [WORKING]`

* First work towards moving from Jupyter notebooks to a standard Python script.
  This now has exaclty the same functionality as the original Jupyter notebooks,
  so they have been retired. The are kept in the [notebooks](notebooks/) folder
  for posterity.

There are currently 2 stages of operation:

* Scrape the main Wikipedia Star Trek page and create a JSON file containing
  Series names and metadata (number of seasons, number of episodes etc.) This
  metadata will probably include series summary and other data in future
  iterations (not necessarily from Wikipedia)

* Take the JSON file created in the previous step, and dump the episode names
  for each series to a separate json file, with some Series metadata
  * Discovery and Prodigy need special treatment as their markup seems to follow
    no logic know to man, God or Vulcan.

## Produced Files

A current version of the derived data is available in the [output](output)
directory, valid as of June 2022.

This contains:

* [star_trek_series_info.json](output/star_trek_series_info.json)
  which lists info and links for each series only, and is used as the basis for
  getting the individual series data.
* One individual JSON file for each Star Trek incarnation (Currently 10 as we
  are skipping `Prodigy` and `Strange New Worlds` for now).

A tarball is included in the [releases](releases) folder and attached to each
GitHub release.

## Operation

Clone or download the repository, then run the main script from the root of the
created folder.

```python
python generate_trek.py
```

The updated files will be created in the output folder, overwriting any existing
ones.

[viacomcbs]:https://www.viacomcbs.com
[wst]: https://en.wikipedia.org/wiki/Star_Trek
[fup]: https://en.wikipedia.org/wiki/Fair_use#Text_and_data_mining
[jupyter]: https://jupyter.org/
[rails-api]: https://github.com/gnramsay/trekpedia-api-rails
