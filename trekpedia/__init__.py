"""Define the package's public interface."""

from trekpedia.helpers import save_json
from trekpedia.trekpedia import Trekpedia

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"
JSON_TEMPLATE = "output/star_trek_series_{}_{}_episodes.json"

__all__ = ["JSON_TEMPLATE", "MAIN_URL", "Trekpedia", "save_json"]
