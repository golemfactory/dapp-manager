from pathlib import Path
from typing import Dict, Optional

import colors
import requests
from mako.lookup import TemplateLookup
from mako.template import Template


class Inspect:
    _gaom: Optional[Dict] = None

    def __init__(self, api_address: str):
        self.api_address = api_address

    @staticmethod
    def _get_template(name: str) -> Template:
        lookup = TemplateLookup(directories=[Path(__file__).parent / "templates"])
        return lookup.get_template(name)

    def fetch_gaom(self):
        """Retrieve the current Golem Application Object Model data."""

        data = requests.get(f"{self.api_address}/gaom")
        self._gaom = data.json()

    @property
    def gaom(self):
        """Golem Application Object Model data.

        Will retrieve the data if there's none or provide the cached copy
        if GAOM had already been retrieved.
        """

        if not self._gaom:
            self.fetch_gaom()
        return self._gaom

    def display_app_structure(self):
        template = self._get_template("app_structure.txt")
        return template.render(**self.gaom, **{"colors": colors})
