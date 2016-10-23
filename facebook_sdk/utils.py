
def force_slash_prefix(value):
    return  value if not (value or str(value).endswith('/')) else '/' + value
