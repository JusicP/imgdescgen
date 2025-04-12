from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class GeminiModelName(BaseModel):
    """
    Gemini model name class, used to store model name and display name.
    """
    name: str # string in format "models/{baseModelId}-{version}"
    displayName: str | None = None

class GeminiModel(GeminiModelName):
    """
    Gemini model class, used to store model metadata.
    """
    inputTokenLimit: int | None = None
    outputTokenLimit: int | None = None
    supportedGenerationMethods: list[str] | None = None

class GeminiModelListResponse(BaseModel):
    models: list[GeminiModel]

    def get_model_by_name(self, name: str) -> GeminiModel | None:
        """
        Returns model by name. Check GeminiModelName.name comment for naming.
        """
        return next((model for model in self.models if model.name == name), None)

    def get_supported_models(self):
        """
        Returns list of models that support generation methods: generateContent and countTokens.
        """
        return self.filter_by_generation_methods(["generateContent", "countTokens"])

    def filter_by_generation_methods(self, generation_methods: list[str]):
        """
        Filters models by generation methods.
        """
        filtered_models = [model for model in self.models if any(method in model.supportedGenerationMethods for method in generation_methods)]
        return GeminiModelListResponse(models=filtered_models)

class GeminiUsageMetadata(BaseModel):
    """
    Gemini usage metadata class, used to store usage metadata from generateContent API.
    """
    promptTokenCount: int
    candidatesTokenCount: int
    
class GeminiCanditate(BaseModel):
    """
    Gemini candidate class, used to store candidate from generateContent API.
    """
    content: dict
    finishReason: str # https://ai.google.dev/api/generate-content#FinishReason

#https://ai.google.dev/api/generate-content    
class GeminiGenerateContentResponse(BaseModel):
    """
    Gemini generate content response class, used to store response from generateContent API.
    """
    candidates: list[GeminiCanditate]
    usageMetadata: GeminiUsageMetadata

class GeminiConfig(BaseSettings):
    """
    Gemini config class, used to store API key and other settings.
    """
    model_config = SettingsConfigDict(env_prefix='GEMINI_')

    api_key: str = ""
    model_name: GeminiModelName | None = None
    # TODO: write image schema from GeminiImageDescription
    image_description_prompt: str = 'Write a detailed description and key words of the each image, ' \
                'with this JSON schema: Image = {"description": str, "keywords": list[str]} Return: list[Image]}.'
