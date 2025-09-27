# Providers

Concrete LLM provider implementations live here and satisfy `LLMInterface`.

## AzureOpenAIProvider.py
Wraps the Azure OpenAI Chat and Embedding APIs. Requires endpoint, API version, API key, and deployment names. Use the `OPENAI` enum value to instantiate it via the factory.

## CohereProvider.py
Bridges to Cohere's Chat and Embed APIs. Supply `COHERE_API_KEY` together with model identifiers (the current `Settings` class exposes this as `CHHERE_API_KEY`). Use the `COHERE` enum value to instantiate it via the factory.

Additional providers should follow the same pattern: accept configuration via settings, set generation/embedding models, and honour the shared interface contract.
