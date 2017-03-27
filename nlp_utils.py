import re
from typing import List


def match_url(text: str) -> List[str]:
    url_re = re.compile(r'(https?://t.co/[a-zA-Z0-9]+)')
    return url_re.findall(text)

