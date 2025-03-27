import os
import base64 # for image encoding
import exiftool

class Image:
    """
    Encapsulation of image.
    """
    PROCESSED_IMAGES_DIR = 'processed_images'

    def __init__(self, img_path, processed_img_path = PROCESSED_IMAGES_DIR):
        self._load(img_path)

        self._processed_img_path = processed_img_path

    def _load(self, img_path):
        """
        Loads image from file
        """
        with open(img_path, "rb") as f:
            self._img_path = img_path

            self._img_bytes = f.read()
            self._img_size = len(self._img_bytes)

    def encode_base64(self):
        """
        Encodes image bytes using base64.
        Returns base64 str.
        """
        return base64.b64encode(self._img_bytes).decode('utf-8')

    def read_metadata(self) -> dict | None:
        """
        Reads image metadata
        """
        with exiftool.ExifToolHelper() as et:
            return et.get_tags(
                self._img_path,
                None
            )

    def write_description_metadata(self, img_metadata: dict):
        """
        Writes image description
        """
        # create directory for processed images if not exists
        os.makedirs(self._processed_img_path, exist_ok=True)
        
        # write image with modded metadata
        with exiftool.ExifToolHelper() as et:
            et.set_tags(
                self._img_path,
                {"ImageDescription": img_metadata["description"]},
                ["-o", f'{self._processed_img_path}/{os.path.basename(self._img_path)}']
            )