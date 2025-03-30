import os
import base64 # for image encoding
import exiftool
import PIL.Image

from io import BytesIO

from imgdescgenlib.exceptions import ImageToolException

class Image:
    """
    Encapsulation of image.
    """
    
    def __init__(self, img_path: str, output_path: str):
        self._load(img_path)
        self._output_path = output_path

        self._quality = "keep"

    def _load(self, img_path: str):
        """
        Loads image from file
        """
        self._internal_image = PIL.Image.open(img_path)
        self._img_path = img_path

    def reduce_quality(self):
        """
        Reduces quality of image
        """
        self._quality = 10

    def save(self, path: str):
        """
        Saves original image to directory
        """
        self._internal_image.save(f"{path}/{os.path.basename(self._img_path)}", format="JPEG", quality="keep")

    def size(self):
        """
        Returns the size of an image in bytes 
        """
        buffer = BytesIO()
        self._internal_image.save(buffer, format="JPEG", quality=self._quality)
        return buffer.getbuffer().nbytes

    def encode_base64(self):
        """
        Encodes image bytes using base64.
        Returns base64 str.
        """
        buffer = BytesIO()
        self._internal_image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def read_metadata(self) -> dict | None:
        """
        Reads image metadata
        """
        try:
            with exiftool.ExifToolHelper() as et:
                return et.get_tags(
                    self._img_path,
                    None
                )
        except exiftool.exceptions.ExifToolException:
            raise ImageToolException
    
    def write_description_metadata(self, img_metadata: dict):
        """
        Writes image description
        """
        # create directory for processed images if not exists
        os.makedirs(self._output_path, exist_ok=True)
        
        # write image with modded metadata
        try:
            with exiftool.ExifToolHelper() as et:
                et.set_tags(
                    self._img_path,
                    {"ImageDescription": img_metadata["description"]},
                    ["-o", f'{self._output_path}/{os.path.basename(self._img_path)}']
                )
        except exiftool.exceptions.ExifToolException:
            raise ImageToolException