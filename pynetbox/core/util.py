from six.moves.urllib.parse import urlsplit

def set_base_url(base, url):
    """ 
    Replace base url (before '/api/') with base_url from 
    pynetbox.api() instantiation.
    """
    b = urlsplit(base)
    base_path = b.path if b.path.endswith('/') else f'{b.path}/'
    split_base_path = base_path.split("/api/")[0]
    base_url = f'{b.scheme}://{b.netloc}{split_base_path}'

    u = urlsplit(url)
    url_path = u.path.split("/api/")[1]

    return f'{base_url}/api/{url_path}?{u.query}'



class Hashabledict(dict):
    def __hash__(self):
        return hash(frozenset(self))
