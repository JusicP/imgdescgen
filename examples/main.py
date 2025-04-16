import json

from imgdescgenlib.exceptions import ImageToolException, ImgDescGenBaseException
from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.chatbot.gemini.gemini import GeminiClient, GeminiConfig
from imgdescgenlib.chatbot.exceptions import ChatbotFailed, ChatbotHttpRequestFailed, ChatbotPayloadTooLarge

def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        ...

if __name__ == "__main__":
    # not required to have config.json, you can set environment variables instead
    config_data = load_json("config.json")
    if config_data:
        config = GeminiConfig.model_validate(config_data)

    client = GeminiClient(config)

    # choose gemini-1.5-flash model if not set in config
    config = client.get_config()
    if not config.model_name:
        models = client.get_available_models()
        config.model_name = models.get_model_by_name("models/gemini-1.5-flash")

    img_desc_gen = ImgDescGen(client)

    try:
        desc = img_desc_gen.generate_image_description(["=test.jpg", "test2.jpg"], "processed_images")
        print(f"Generated description: {desc}")
    except ChatbotPayloadTooLarge:
        print("Error: payload too large, try image with smaller size")
    except ChatbotHttpRequestFailed as e:
        print(f"Error: {e}")
    except ChatbotFailed as e:
        print(f"Error: chatbot failed: {e}")
    except ImageToolException as e:
        print(f"Error: image tool failed: {e}")
    except ImgDescGenBaseException as e:
        print(f"Error: image description generation failed: {e}")
    