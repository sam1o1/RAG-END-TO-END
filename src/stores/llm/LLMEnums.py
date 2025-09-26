from enum import Enum


class LLMEnum(Enum):

    OPENAI = "OPENAI"
    COHERE = "COHERE"


class AzureOpenAIEnum(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
