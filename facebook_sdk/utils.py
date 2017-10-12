import re
import six

try:
    from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
except ImportError:
    from urllib import urlencode
    from urlparse import urlparse, parse_qs, urlunparse


def force_slash_prefix(value):
    return '/' + value if not (value and str(value).startswith('/')) else value


def base_graph_url_endpoint(url_to_trim):
    return re.sub(r'^https://.+\.facebook\.com(/v.+?)?/', '/', url_to_trim)


def remove_params_from_url(url, params_to_remove):
    parsed = urlparse(url)
    qd = parse_qs(parsed.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in qd.items() if k not in params_to_remove)
    newurl = urlunparse([
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(filtered, doseq=True),  # query string
        parsed.fragment
    ])

    return newurl


def get_params_from_url(url):
    parsed = urlparse(url)
    qd = parse_qs(parsed.query, keep_blank_values=True)
    return qd


def convert_params_to_utf8(params):
    return {
        k: v.encode("utf-8") if isinstance(v, six.text_type) else v
        for k, v in params.items()
    }
