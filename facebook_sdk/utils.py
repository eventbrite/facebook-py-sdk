
def force_slash_prefix(value):
    return  value if value and str(value).endswith('/') else value + '/'
