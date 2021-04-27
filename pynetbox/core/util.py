from six.moves.urllib.parse import urlsplit

def set_base_url(base, url):
    """ 
    Replace base url (before '/api/') with base_url from 
    pynetbox.api() instantiation.
    """
    b = urlsplit(base)
    base_url = f'{b.scheme}://{b.netloc}{b.path.split("/api/")[0]}'

    u = urlsplit(url)
    path = u.path.split("/api/")[1]
    return f'{base_url}/{path}'


class Hashabledict(dict):
    def __hash__(self):
        return hash(frozenset(self))
