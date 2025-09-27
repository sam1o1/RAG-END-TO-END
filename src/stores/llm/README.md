# LLM Store

The `stores/llm/` package defines the abstractions that allow Mini RAG to talk to external language model providers for both text generation and embeddings.

## Key Modules
- `LLMInterface.py` — Abstract base class describing the required methods for any provider.
- `LLMEnums.py` — Shared enums for provider identifiers, chat roles, and embedding document types.
- `LLMProviderFactory.py` — Creates provider instances based on `GENERATION_BACKEND`/`EMBEDDING_BACKEND` settings.
- `providers/` — Concrete implementations. Azure OpenAI and Cohere are currently available.

## Usage Notes
- The FastAPI startup event builds `generation` and `embedding` clients by calling the factory with settings drawn from `.env`.
- Azure OpenAI expects endpoint, API key, API version, and deployment names to be present.
- Cohere requires an API key; document or query embeddings can be selected via the `DocumentTypeEnum`.
- New providers can be added by implementing `LLMInterface` and registering them inside `LLMProviderFactory.create()`.
