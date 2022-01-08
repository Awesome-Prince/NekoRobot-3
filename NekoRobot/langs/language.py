"""
MIT License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022 Hodacka
Copyright (c) 2022, Yūki • Black Knights Union, <https://github.com/Hodacka/NekoRobot-3>
This file is part of @NekoXRobot (Telegram Bot)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the Software), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import yaml
import os
from typing import Dict


class Language:
    def __init__(self) -> None:
        self.languages: Dict = {}
        self.reload_strings()

    def get_string(self, lang: str, string: str) -> str:
        try:
            return self.languages[lang][string]
        except KeyError:
            # a keyerror happened, the english file must have it
            en_string = self.languages["en"].get(string)
            if en_string is None:
                raise StringNotFound(f"String: ({string}) not found.")
            return en_string

    def reload_strings(self) -> None:
        for filename in os.listdir(r"./NekoRobot/langs"):
            if filename.endswith(".yaml"):
                language_name = filename[:-5]
                self.languages[language_name] = yaml.safe_load(
                    open(r"./NekoRobot/langs/" + filename, encoding="utf8")
                )

    def get_languages(self) -> Dict:
        to_return: Dict = {}
        for language in self.languages:
            to_return[language] = self.languages[language]["language"]
        return to_return

    def get_language(self, language: str) -> str:
        return self.languages[language]["language"]


class StringNotFound(Exception):
    """
    Raised when language string not found for the
    given key inside english locale.
    """


langs = Language()
