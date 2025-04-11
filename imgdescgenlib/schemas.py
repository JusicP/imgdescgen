from pydantic import BaseModel

class ImageDescription(BaseModel):
    """
    Image description class, used to store image metadata.
    """
    description: str
    keywords: list[str]
