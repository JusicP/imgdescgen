import os
import tempfile
import PIL.Image

from imgdescgenlib.image import Image

def create_temp_image(directory: str) -> str:
    img_filename = "temp_image.jpg"
    img = PIL.Image.new('RGB',
                      size=(228, 1337),
                      color=(0, 0, 255))

    temp_img_path = os.path.join(directory, img_filename)
    img.save(temp_img_path)
    return temp_img_path

def test_image_metadata_rw():
    with tempfile.TemporaryDirectory() as tempdir:
        metadata = {
            "description": "test description",
            "keywords": [
                "word 1",
                "word 2"
            ]
        }

        img_path = create_temp_image(tempdir)
        new_img_path = os.path.join(tempdir, Image.PROCESSED_IMAGES_DIR, os.path.basename(img_path))

        img = Image(img_path, os.path.join(tempdir, Image.PROCESSED_IMAGES_DIR))
        img.write_description_metadata(metadata)

        new_img = Image(new_img_path)
        tags = new_img.read_metadata()

        assert tags[0]["EXIF:ImageDescription"] == metadata["description"]