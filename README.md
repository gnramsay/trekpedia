# Trekpedia JSON <!-- omit in toc -->

- [Compatibility](#compatibility)
- [Development](#development)
  - [Current progress](#current-progress)
- [Produced Files](#produced-files)
- [Operation](#operation)
  - [Install Dependencies](#install-dependencies)
  - [Run the program](#run-the-program)
- [Current known BUGS](#current-known-bugs)
- [Further Enhancements planned](#further-enhancements-planned)

Star Trek TV episode database scraped from web sources and provided in JSON
format. Films will be added at a later date.

This geek project is just for me to get familiar with Python web-scraping and
provide data for API development.

All copyright to the 'Star Trek' name and data belongs to
[ViacomCBS][viacomcbs].

All data in this project is mined live from the [Wikipedia Star Trek page][wst]
and associated subpages under the [Fair Use][fup] principal.

The license below only applies to the **SOURCE CODE**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Compatibility

This data is mined from Wikipedia and is therefore only as accurate as the
source. It is also only as up-to-date as the last time I ran the scraper.

Note also that the site formatting changes (annoyingly) frequently and
inconsistently, so the script may fail to run properly if the site has changed
since the last update. I aim to keep the script up-to-date with any changes, but
I can't guarantee doing this immediately. There are a few 'hacks' in the code to
get around some of the formatting issues and I will be refactoring these shortly
into better code.

## Development

Initially, I carried out the development of the scraper using [Jupyter
Notebooks][jupyter]. These are deprecated and archived in the `notebooks`
folder.

I have migrated this base work into pure Python, where all further development
will remain.

### Current progress

I am only scraping the TV series data, leaving film data until later iterations.

There are currently two stages of operation:

- Scrape the main Wikipedia Star Trek page and create a JSON file containing
  Series names and metadata (number of seasons, number of episodes, etc.). This
  metadata will probably include a series summary and other data in future
  iterations (not necessarily from Wikipedia)

- Take the JSON file created in the previous step, and dump the episode names
  for each series to a separate JSON file, with some Series metadata

## Produced Files

A current version of the derived data is available in the [output](output)
directory, valid as of 3rd September 2023.

This directory contains the following GENERATED files:

- The file [star_trek_series_info.json](output/star_trek_series_info.json) lists
  info and links for each series. This file was previously required as input to
  the Stage 2 notebook but not needed for the current scripts. However,
  it does contain Series metadata that is useful when generating an API, for
  example.
- A Separate JSON file for each Star Trek series, 12 to date.

A tarball is included in the [releases](releases) folder and attached to each
GitHub release.

## Operation

Clone or download the repository, install dependencies, then run the main script
from the root of the created folder.

### Install Dependencies

The project has been set up using [Poetry](https://python-poetry.org/) to
organize and install dependencies. If you have Poetry installed, simply run the
following to install all that is needed.

```console
poetry install
```

If you do not (or cannot) have Poetry installed, I have provided an
auto-generated `requirements.txt` in the project root which you can use as
normal:

```console
pip install -r requirements.txt
```

I definately recommend using Poetry if you can though, it makes dealing with
updates and conflicts very easy.

If using poetry you now need to activate the VirtualEnv:

```console
poetry shell
```

### Run the program

```console
python generate_trek.py
```

The updated files will be created in the output folder, overwriting existing
ones.

## Current known BUGS

- `Star Trek: Prodigy` data is quite different and crashes again so has temporarily
  been disabled and will not be generated until I fix that.

## Further Enhancements planned

- A list of Star Trek characters [here][st-char] can also be parsed and linked
to the relevant series/season/episode data.
- Add a brief series and episode summary.

[viacomcbs]:https://www.viacomcbs.com
[wst]: https://en.wikipedia.org/wiki/Star_Trek
[st-char]: https://en.wikipedia.org/wiki/List_of_Star_Trek_characters
[fup]: https://en.wikipedia.org/wiki/Fair_use#Text_and_data_mining
[jupyter]: https://jupyter.org/
