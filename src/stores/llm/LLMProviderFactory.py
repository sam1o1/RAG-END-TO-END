import re
from .LLMEnums import LLMEnum
from .providers import AzureOpenAIProvider, CohereProvider


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnum.OPENAI.value:
            return AzureOpenAIProvider(
                api_key=self.config.AZURE_OPENAI_API_KEY,
                api_base=self.config.AZURE_OPENAI_ENDPOINT,
                api_version=self.config.AZURE_OPENAI_API_VERSION,
                default_input_max_chars=self.config.INPUT_DEFAULT_MAX_CHARS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )

        elif provider == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_chars=self.config.INPUT_DEFAULT_MAX_CHARS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )

        return None
