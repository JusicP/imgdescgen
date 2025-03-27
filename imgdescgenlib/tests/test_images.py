import os
import tempfile
import PIL.Image

from imgdescgenlib.images import Images
from imgdescgenlib.image import Image

def create_temp_image(index: int, directory: str) -> str:

    img_filename = f"temp_image_{index}.jpg"
    img = PIL.Image.new('RGB',
                      size=(228, 1337),
                      color=(0, 0, 255))

    temp_img_path = os.path.join(directory, img_filename)
    img.save(temp_img_path)

    return temp_img_path

def test_write_description_metadata():
    # create 2 images
    img_count = 2

    with tempfile.TemporaryDirectory() as tempdir:
        img_paths = []
        new_imgs_path = []
        metadata = []
        for i in range(img_count):
            img_paths.append(create_temp_image(i, tempdir))
            new_imgs_path.append(os.path.join(tempdir, Image.PROCESSED_IMAGES_DIR, os.path.basename(img_paths[i])))

            metadata.append(
                { "description": f"test_{i}" }
            )

        imgs = Images(img_paths, os.path.join(tempdir, Image.PROCESSED_IMAGES_DIR))
        imgs.write_description_metadata(metadata)

        new_imgs = Images(new_imgs_path)
        tags = new_imgs.read_metadata()

        for i in range(img_count):
            assert tags[i]["EXIF:ImageDescription"] == metadata[i]["description"]