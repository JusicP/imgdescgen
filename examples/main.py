import os

from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.chatbot.gemini import GeminiClient

if __name__ == "__main__":
    # usage example
    api_key = os.environ.get('GEMINI_API_KEY')

    img_desc_gen = ImgDescGen(GeminiClient(api_key))
    desc = img_desc_gen.generate_image_description("test.jpg")

    print(f"Generated description: {desc}")
    