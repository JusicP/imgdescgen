from imgdescgenlib.chatbot.base import ChatbotBase
from imgdescgenlib.images import Images

class ImgDescGen():
    """
    Class that provides simple interface for retrieving AI-generated description of image and writing it to the image metadata.
    """
    def __init__(self, chatbot: ChatbotBase):
        self._chatbot = chatbot

    def generate_image_description(self, img_paths: list[str], output_dir: str = None, reduce_quality: bool = True):
        """
        Loads image from file and sends request to the chatbot.
        Then writes metadata to image and dumps it to disk.

        Args:
            img_paths (list[str]): List of images path.
            output_dir (str): Output directory for updated images.
            reduce_quality (bool): Reduce quality of all images.

        Returns:
            dict: Dictionary containing metadata for each image.
        """
        imgs = Images(img_paths)

        if reduce_quality:
            imgs.reduce_quality()

        img_metadata = self._chatbot.generate_image_description(imgs.encode_base64())

        if output_dir:
            imgs.write_description_metadata(img_metadata, output_dir)

        return img_metadata