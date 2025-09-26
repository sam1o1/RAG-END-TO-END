import re
from tkinter import N
from ..LLMInterface import LLMInterface
from ..LLMEnums import AzureOpenAIEnum
from openai import OpenAI, AzureOpenAI, azure_endpoint
import logging


class AzureOpenAIProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        api_base: str = None,
        api_version: str = None,
        default_input_max_chars: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.generation_model_id = None
        self.embedding_model_id = None
        self.api_version = api_version
        self.default_input_max_chars = default_input_max_chars
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.embedding_size = None
        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.api_base,
            api_version=self.api_version,
            azure_deployment=self.generation_model_id,
        )
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str) -> str:
        return text.strip()[: self.default_input_max_chars]

    def generate_text(
        self,
        prompt: str,
        max_output_tokens: int,
        temperature: float = None,
        chat_history: list = [],
    ) -> str:

        if not self.client:
            self.logger.error("Azure OpenAI client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None
        max_output_tokens = (
            max_output_tokens
            if max_output_tokens
            else self.default_generation_max_output_tokens
        )
        temperature = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=AzureOpenAIEnum.USER.value)
        )
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )
        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):
            self.logger.error("No response received from Azure OpenAI.")
            return None
        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str) -> list[float]:
        if not self.client:
            self.logger.error("Azure OpenAI client is not initialized.")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        response = self.client.embeddings.create(
            input=text, model=self.embedding_model_id
        )
        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("No embedding data received from Azure OpenAI.")
            return None
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str) -> str:
        return {"role": role, "content": self.process_text(prompt)}
