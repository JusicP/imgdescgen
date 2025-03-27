import os
import exiftool
import tempfile
import csv

from imgdescgenlib.image import Image

class Images:
    """
    Manager for multiple Image instances; container for images
    """

    def __init__(self, imgs_path: list[str], processed_img_path = Image.PROCESSED_IMAGES_DIR):
        self._img_basedir = None
        self._processed_img_path = processed_img_path
        self._load(imgs_path)

    def _load(self, imgs_path: list[str]):
        """
        Loads images from file
        """
        self._images = []
        for img_path in imgs_path:
            # set base dir for images
            if self._img_basedir == None:
                self._img_basedir = os.path.normpath(os.path.dirname(img_path))

            self._images.append(Image(img_path, self._processed_img_path))

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
        with exiftool.ExifToolHelper() as et:
            return et.get_tags(
                [image._img_path for image in self._images],
                None
            )

    def write_description_metadata(self, img_metadata: list[dict]):
        """
        Writes image description
        Note: images must be in the same directory
        TODO: copy images to one directory if they are in different
        """

        # create directory for processed images if not exists
        os.makedirs(self._processed_img_path, exist_ok=True)
        
        # create temp csv file with filename and metadata
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(f'{tmp_dir}/metadata.csv', 'w', newline='') as csvfile:
                fieldnames = ['SourceFile', 'EXIF:ImageDescription']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i in range(len(self._images)):
                    writer.writerow(
                        {
                            'SourceFile': self._images[i]._img_path,
                            'EXIF:ImageDescription': img_metadata[i]['description']
                        }
                    )

            with exiftool.ExifToolHelper() as et:
                et.execute(f'-csv={f'{tmp_dir}/metadata.csv'}', '-o', self._processed_img_path, self._img_basedir)
