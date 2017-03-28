import re
from typing import List
import unicodedata


def match_url(text: str) -> List[str]:
    url_re = re.compile(r'(https?://t.co/[a-zA-Z0-9]+)')
    return url_re.findall(text)

def remove_accents(s: str) -> str:
    return unicodedata.normalize('NFKD', s) \
        .encode('ASCII', 'ignore') \
        .decode('utf-8')