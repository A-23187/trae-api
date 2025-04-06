from typing import Any, Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    content: str | list[dict[str, Any]]
    name: str | None = None
    role: Literal["system", "user", "assistant", "tool", "function"]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    max_completion_tokens: int | None = None
    modalities: list[str] | None = None
    response_format: dict[str, Any] | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    stream: bool | None = False
    stream_options: dict[str, Any] | None = None
    temperature: float | None = 1
    tool_choice: Literal["none", "auto", "required"] | dict[str, Any] | None = None
    tools: list[dict[str, Any]] | None = None
    top_k: int | None = 20
    top_p: float | None = 1
    web_search_options: dict[str, Any] | None = None


class ChatCompletionChunkChoice(BaseModel):
    delta: dict[str, Any]
    finish_reason: str | None = None
    index: int = 0
    logprobs: dict[str, Any] | None = None


class ChatCompletionChunk(BaseModel):
    choices: list[ChatCompletionChunkChoice]
    created: int
    id: str
    model: str
    object: str = "chat.completion.chunk"
    service_tier: str | None = None
    system_fingerprint: str = ""
    usage: dict[str, Any] | None = None


class Model(BaseModel):
    created: int
    id: str
    object: str = "model"
    owned_by: str = "trae"
