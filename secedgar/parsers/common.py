from __future__ import annotations

import re
from typing import Optional, Any, Dict
from dataclasses import dataclass
from lxml import etree
from bs4 import BeautifulSoup


from bs4.builder import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

class FilingValuesParser:
    @staticmethod
    def parse_by_re_line(re_pattern, input_text) -> Optional[str]:
        line_value = None
        re_search = re.search(re_pattern, input_text)
        if re_search:
            line_value = re_search.group(1)
        return line_value
    
class FilingXMLParser:

    @staticmethod
    def get_xml_text(input_text:str, root_tag:str) -> str:
        soup = BeautifulSoup(input_text, "lxml")
        root_soup = soup.find(root_tag.lower())
        return str(root_soup)

    @staticmethod
    def get_tag_value(xml_string:str, tag_str:str) -> Optional[str]:
        document_root = etree.fromstring(xml_string)
        found_text = document_root.find(f'.//{tag_str.lower()}')
        if found_text is not None:
            return found_text.text
        else:
            return None

@dataclass
class FilingValues:
    form_type: str
    sec_act: Optional[str]
    sec_file_number: Optional[str]
    film_number: Optional[str]

    @staticmethod
    def from_text(input_text:str) -> FilingValues:
        parser = FilingValuesParser()
        return FilingValues(
            form_type=parser.parse_by_re_line(r"FORM TYPE:\s+(.*)", input_text),
            sec_act=parser.parse_by_re_line(r"SEC ACT:\s+(.*)", input_text),
            sec_file_number=parser.parse_by_re_line(r"SEC FILE NUMBER:\s+(.*)", input_text),
            film_number=parser.parse_by_re_line(r"FILM NUMBER:\s+(.*)", input_text),
        )