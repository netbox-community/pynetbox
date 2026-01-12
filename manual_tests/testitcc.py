import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="adbf699007aa3b231261347cc9b8afde282c1809",
    threading=True,
)

sites = nb.dcim.sites.all()
for site in sites:
    print(site)
