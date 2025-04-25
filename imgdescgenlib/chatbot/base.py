from imgdescgenlib.images import Images
from imgdescgenlib.schemas import ImageDescription

class ChatbotBase():
    """
    Chatbot base class
    """
    def generate_image_description(self, images: Images) -> list[ImageDescription]:
        raise NotImplementedError