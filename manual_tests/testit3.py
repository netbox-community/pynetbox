import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="92e3ccc349e861c32bcf74af5cde435a5cea0d81",
    threading=True,
)


# #########################################################
# After this is just sample code using the activate_branch and
# wait_for_branch_status functions
# #########################################################
sites = nb.dcim.sites.all()
for site in sites:
    print(site)
