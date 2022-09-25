"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
from typing import Dict

import yaml


class Language:
    def __init__(self) -> None:
        self.languages: Dict = {}
        self.reload_strings()

    def get_string(self, lang: str, string: str) -> str:
        try:
            return self.languages[lang][string]
        except (KeyError, IndexError):
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
                    open(f"./NekoRobot/langs/{filename}", encoding="utf8")
                )

    def get_languages(self) -> Dict:
        return {
            language: self.languages[language]["language"]
            for language in self.languages
        }

    def get_language(self, language: str) -> str:
        return self.languages[language]["language"]


class StringNotFound(Exception):
    """
    Raised when language string not found for the
    given key inside english locale.
    """


langs = Language()
