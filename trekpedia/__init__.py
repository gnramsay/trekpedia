from .trekpedia import Trekpedia

MAIN_URL = "https://en.wikipedia.org/wiki/Star_Trek"
JSON_TEMPLATE = "output/star_trek_series_{}_{}_episodes.json"

__all__ = ["Trekpedia", "MAIN_URL", "JSON_TEMPLATE"]
