import pynetbox

nb = pynetbox.api(
    "http://localhost:8000", token="10f30c9ad366dbcd334ee93ae8f7c0bb2405ec8f"
)

# Attach an image to a device
with open("/Users/ahanson/Downloads/IMG_0696.jpg", "rb") as f:
    attachment = nb.extras.image_attachments.create(
        object_type="dcim.device", object_id=27, image=f, name="rack-photo.jpg"
    )
