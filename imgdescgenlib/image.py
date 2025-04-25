import os
import base64 # for image encoding
import exiftool
import PIL.Image

from io import BytesIO

from imgdescgenlib.exceptions import ImageToolException
from imgdescgenlib.schemas import ImageDescription

class Image:
    """
    Encapsulation of image.
    """
    
    def __init__(self, img_path: str):
        self._exiftool_path = None
        self._load(img_path)

        self._quality = "keep"

    def _load(self, img_path: str):
        """
        Loads image from file
        """
        self._internal_image = PIL.Image.open(img_path)
        self._img_path = img_path

    def get_filename(self) -> str:
        """
        Returns image filename
        """
        return os.path.basename(self._img_path)

    def set_exiftool_path(self, exiftool_path: str):
        """
        Sets the path to the ExifTool executable.
        If None, pyexiftool will search for it in PATH.
        """
        self._exiftool_path = exiftool_path

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

    def save_to_buffer(self) -> BytesIO:
        """
        Saves image to buffer
        """
        buffer = BytesIO()
        self._internal_image.save(buffer, format="JPEG", quality=self._quality)
        return buffer
    
    def size(self) -> int:
        """
        Returns the size of an image in bytes 
        """
        return self.save_to_buffer().getbuffer().nbytes

    def encode_base64(self) -> str:
        """
        Encodes image bytes using base64.
        Returns base64 str.
        """
        buffer = self.save_to_buffer()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def read_metadata(self) -> list:
        """
        Reads image metadata
        """
        try:
            with exiftool.ExifToolHelper(executable=self._exiftool_path) as et:
                return et.get_tags(
                    self._img_path,
                    None
                )
        except FileNotFoundError as e:
            raise ImageToolException(f"ExifTool not found: {e}")
        except exiftool.exceptions.ExifToolExecuteException as e:
            raise ImageToolException(f"ExifTool execution error: {e}")
        except exiftool.exceptions.ExifToolException as e:
            raise ImageToolException(f"ExifTool error: {e}")
    
    def write_description_metadata(self, img_metadata: ImageDescription, output_path: str):
        """
        Writes image description
        """

        # create directory for processed images if not exists
        os.makedirs(output_path, exist_ok=True)
        
        # write image with modded metadata
        try:
            with exiftool.ExifToolHelper(executable=self._exiftool_path) as et:
                et.set_tags(
                    self._img_path,
                    {"ImageDescription": img_metadata.description},
                    ["-o", f'{output_path}/{os.path.basename(self._img_path)}']
                )
        except FileNotFoundError as e:
            raise ImageToolException(f"ExifTool not found: {e}")
        except exiftool.exceptions.ExifToolExecuteException as e:
            raise ImageToolException(f"ExifTool execution error: {e}")
        except exiftool.exceptions.ExifToolException as e:
            raise ImageToolException(f"ExifTool error: {e}")
