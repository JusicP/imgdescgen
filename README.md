# Image description generator

This is a Python library for generating description and keywords for images and writing them to the original image metadata.

Description generation relies on chatbots.
At the moment, the choice of chatbot is limited to Gemini.
But it is not difficult to add support for another chatbot or tool.

## Installing
After repo cloning, run this from source:
```
python -m pip install .
```

Writing image metadata relies on [exiftool](https://exiftool.org/) (minimum 12.15 version), the path to which should be in the PATH environment variable or passed as an argument in `ImgDescGen.generate_image_description()` method.

## How to use
[Example](examples/main.py)

[Example of project where library is used](https://github.com/JusicP/imgdescgengui)
