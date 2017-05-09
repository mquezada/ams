import re
from typing import List, Optional
import unicodedata
from urllib import parse


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


def clean_url(url: str) -> str:
    u = parse.urldefrag(url).url
    u = parse.urlparse(u)
    query = parse.parse_qs(u.query)
    allowed = ('v', 'id', 'fbid', 'contentguid', 'set', 'type', 'l')
    query = {k: v for (k, v) in query.items() if k in allowed}
    u = u._replace(query=parse.urlencode(query, True))
    return parse.urlunparse(u)
