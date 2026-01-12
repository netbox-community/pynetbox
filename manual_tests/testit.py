import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="nbt_jmEaR2a9bQGn.c9ikyDRw46SMH8JeUrBURGKDuNw8imW15nGkFxoE",
    threading=True,
)


sites = nb.dcim.sites.all()
for site in sites:
    print(site)
