from imgdescgenlib.chatbot.base import ChatbotBase
from imgdescgenlib.image import Image

class ImgDescGen():
    """
    Class that provides simple interface for retrieving AI-generated description of image and writing it to the image metadata.
    """
    def __init__(self, chatbot: ChatbotBase):
        self._chatbot = chatbot

    def generate_image_description(self, img_path: str, save_to_disk = True):
        """
        Loads image from file and sends request to the chatbot.
        Then writes metadata to image and dumps it to disk.
        """
        img = Image(img_path)

        img_metadata = self._chatbot.generate_image_description(img.encode_base64())

        if save_to_disk == True:
            img.write_description_metadata(img_metadata)

        return img_metadata