import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="1b97f3263501a4eab29db007033e30ea6f7c4ef5",
    threading=True,
)

print(nb.version)
