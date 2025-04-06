import json
import time
import uuid
from datetime import datetime

import httpx_sse
from fastapi import FastAPI, Header
from fastapi.responses import StreamingResponse
from httpx import AsyncClient

from .env import (
    TRAE_APP_ID,
    TRAE_DEVICE_BRAND,
    TRAE_DEVICE_CPU,
    TRAE_DEVICE_ID,
    TRAE_DEVICE_TYPE,
    TRAE_IDE_TOKEN,
    TRAE_IDE_VERSION,
    TRAE_IDE_VERSION_CODE,
    TRAE_IDE_VERSION_TYPE,
    TRAE_MACHINE_ID,
    TRAE_OS_VERSION,
)
from .types import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionRequest,
    Model,
)

app = FastAPI(
    title="Trae2OpenAI Proxy",
    description="A api proxy to make trae's builtin models openai compatible",
    version="0.1.0",
)


@app.get("/v1/models")
async def list_models(ide_token: str = Header(TRAE_IDE_TOKEN, alias="Authorization")) -> list[Model]:
    ide_token = ide_token.removeprefix("Bearer ")
    async with AsyncClient() as client:
        response = await client.get(
            "https://trae-api-sg.mchost.guru/api/ide/v1/model_list",
            params={"type": "llm_raw_chat"},
            headers={
                "x-app-id": TRAE_APP_ID,
                "x-device-brand": TRAE_DEVICE_BRAND,
                "x-device-cpu": TRAE_DEVICE_CPU,
                "x-device-id": TRAE_DEVICE_ID,
                "x-device-type": TRAE_DEVICE_TYPE,
                "x-ide-token": ide_token,
                "x-ide-version": TRAE_IDE_VERSION,
                "x-ide-version-code": TRAE_IDE_VERSION_CODE,
                "x-ide-version-type": TRAE_IDE_VERSION_TYPE,
                "x-machine-id": TRAE_MACHINE_ID,
                "x-os-version": TRAE_OS_VERSION,
            },
        )
        return [Model(created=0, id=model["name"]) for model in response.json()["model_configs"]]


@app.post("/v1/chat/completions")
async def create_chat_completions(
    request: ChatCompletionRequest, ide_token: str = Header(TRAE_IDE_TOKEN, alias="Authorization")
) -> StreamingResponse:
    ide_token = ide_token.removeprefix("Bearer ")
    current_turn = sum(1 for msg in request.messages if msg.role == "user")
    last_assistant_message = next(filter(lambda msg: msg.role == "assistant", reversed(request.messages)), None)

    async def stream_response():
        async with AsyncClient() as client:
            async with httpx_sse.aconnect_sse(
                client,
                "POST",
                "https://trae-api-sg.mchost.guru/api/ide/v1/chat",
                headers={
                    "x-app-id": TRAE_APP_ID,
                    "x-device-brand": TRAE_DEVICE_BRAND,
                    "x-device-cpu": TRAE_DEVICE_CPU,
                    "x-device-id": TRAE_DEVICE_ID,
                    "x-device-type": TRAE_DEVICE_TYPE,
                    "x-ide-token": ide_token,
                    "x-ide-version": TRAE_IDE_VERSION,
                    "x-ide-version-code": TRAE_IDE_VERSION_CODE,
                    "x-ide-version-type": TRAE_IDE_VERSION_TYPE,
                    "x-machine-id": TRAE_MACHINE_ID,
                    "x-os-version": TRAE_OS_VERSION,
                },
                json={
                    "chat_history": [msg.model_dump() for msg in request.messages[:-1]],
                    "context_resolvers": [],
                    "conversation_id": str(uuid.uuid4()),
                    "current_turn": current_turn,
                    "generate_suggested_questions": False,
                    "intent_name": "general_qa_intent",
                    "is_preset": True,
                    "last_llm_response_info": (
                        {"turn": current_turn - 1, "is_error": False, "response": last_assistant_message.content}
                        if last_assistant_message
                        else {}
                    ),
                    "model_name": request.model,
                    "multi_media": [],
                    "provider": "",
                    "session_id": str(uuid.uuid4()),
                    "user_input": request.messages[-1].content,
                    "valid_turns": list(range(current_turn)),
                    "variables": json.dumps(
                        {"locale": "zh-cn", "current_time": datetime.now().strftime("%Y%m%d %H:%M:%S %A")}
                    ),
                },
            ) as response:
                chunk = ChatCompletionChunk(
                    choices=[],
                    created=int(time.time()),
                    id="",
                    model=request.model,
                )
                async for sse in response.aiter_sse():
                    sse_data = sse.json()
                    if sse.event == "metadata":
                        chunk.id = str(sse_data["prompt_completion_id"])
                    elif sse.event == "output":
                        content = sse_data["response"]
                        reasoning_content = sse_data["reasoning_content"]
                        chunk.choices = [
                            ChatCompletionChunkChoice(
                                delta={"role": "assistant", "content": content, "reasoning_content": reasoning_content}
                            )
                        ]
                        yield f"data: {chunk.model_dump_json()}\n\n"
                    elif sse.event == "token_usage":
                        chunk.choices = []
                        chunk.usage = {
                            "completion_tokens": sse_data["completion_tokens"],
                            "prompt_tokens": sse_data["prompt_tokens"],
                            "total_tokens": sse_data["total_tokens"],
                        }
                        yield f"data: {chunk.model_dump_json()}\n\n"
                    elif sse.event == "done":
                        chunk.choices = [ChatCompletionChunkChoice(delta={}, finish_reason="stop")]
                        yield f"data: {chunk.model_dump_json()}\n\ndata: [DONE]\n\n"
                    elif sse.event == "error":
                        chunk.choices = [
                            ChatCompletionChunkChoice(
                                delta={"role": "assistant", "content": sse.data}, finish_reason="error"
                            )
                        ]
                        yield f"data: {chunk.model_dump_json()}\n\ndata: [DONE]\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
