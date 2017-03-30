import re
from typing import List, Optional
import unicodedata


def match_url(text: str) -> List[str]:
    url_re = re.compile(r'(https?://t.co/[a-zA-Z0-9]+)')
    return url_re.findall(text)


def clean(s: Optional[str]) -> str:
    if not s:
        return "None"

    s = ' '.join(s.split())

    return unicodedata.normalize('NFKD', s) \
        .encode('ASCII', 'ignore') \
        .decode('utf-8')
