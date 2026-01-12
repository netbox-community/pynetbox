import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="451747f45ebb6f0a7297ddf8ed005e0dd6d9f7de",
    threading=True,
)


# #########################################################
# After this is just sample code using the activate_branch and
# wait_for_branch_status functions
# #########################################################
ots = nb.core.object_types.all()
for ot in ots:
    print(ot)
