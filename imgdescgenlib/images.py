import os
import exiftool
import tempfile
import csv

from imgdescgenlib.exceptions import ImageToolException
from imgdescgenlib.image import Image
from imgdescgenlib.schemas import ImageDescription

class Images:
    """
    Manager for multiple Image instances; container for images
    """

    def __init__(self, imgs_path: list[str]):
        self._common_dir: str = None
        self._exiftool_path: str = None

        # temp dir for storing metadata.csv with/without images
        self._tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self._images: list[Image] = []

        self._load(imgs_path)

    def _load(self, imgs_path: list[str]):
        """
        Loads images from file
        """
        img_dir = None
        different_dirs = False
        for img_path in imgs_path:
            if img_dir == None:
                img_dir = os.path.dirname(img_path)
            elif img_dir != os.path.dirname(img_path) and different_dirs == False:
                different_dirs = True

            self._images.append(Image(img_path))

        if different_dirs == False:
            # set a _common_dir to not to copy all images to temp directory if they are in the same
            self._common_dir = os.path.normpath(os.path.dirname(img_path))

    def _save(self):
        """
        Saves all images to a temporary directory.
        """
        for img in self._images:
            img.save(self._tmpdir.name)

    def set_exiftool_path(self, exiftool_path: str):
        """
        Sets the path to the ExifTool executable.
        If None, pyexiftool will search for it in PATH.
        """
        self._exiftool_path = exiftool_path

    def calculate_size(self) -> int:
        """
        Calculates the size of all images in bytes.
        """
        size = 0
        for img in self._images:
            size += img.size()
        return size

    def reduce_quality(self):
        """
        Reduces the quality of all images.
        """
        for img in self._images:
            #orig_size = img.size()
            img.reduce_quality()
            #reduced_size = img.size()
            #print(f"Reduce quality: size before {orig_size}, after {reduced_size}")

    def encode_base64(self) -> list[str]:
        """
        Encodes images bytes using base64.
        Returns base64 str list.
        """
        return [image.encode_base64() for image in self._images]

    def read_metadata(self) -> dict | None:
        """
        Reads image metadata
        """
        try:
            with exiftool.ExifToolHelper(executable=self._exiftool_path) as et:
                return et.get_tags(
                    [image._img_path for image in self._images],
                    None
                )
        except exiftool.exceptions.ExifToolException:
            raise ImageToolException

    def write_description_metadata(self, img_metadata: list[ImageDescription], output_path: str):
        """
        Writes image description
        Notes:
            - If images are not in the same directory, they will all be saved to the temp directory
        """

        if self._common_dir == None:
            self._save()

        # create directory for processed images if not exists
        os.makedirs(output_path, exist_ok=True)
        
        # create temp csv file with filename and metadata
        with open(f'{self._tmpdir.name}/metadata.csv', 'w', newline='') as csvfile:
            fieldnames = ['SourceFile', 'EXIF:ImageDescription']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(len(self._images)):
                writer.writerow(
                    {
                        'SourceFile': self._images[i]._img_path if self._common_dir else f"{self._tmpdir.name}/{os.path.basename(self._images[i]._img_path)}",
                        'EXIF:ImageDescription': img_metadata[i].description
                    }
                )

        try:
            with exiftool.ExifToolHelper(executable=self._exiftool_path) as et:
                et.execute(
                    f'-csv={self._tmpdir.name}/metadata.csv',
                    '-o', output_path,
                    self._common_dir if self._common_dir else self._tmpdir.name
                )
        except exiftool.exceptions.ExifToolException:
            raise ImageToolException
