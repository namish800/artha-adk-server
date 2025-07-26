import asyncio
import vertexai
from vertexai import agent_engines

from google import adk
from google.adk.memory import VertexAiMemoryBankService
from google.adk.memory.base_memory_service import SearchMemoryResponse

from google.adk.sessions.session import Session
from google.adk.events.event import Event

service = VertexAiMemoryBankService(agent_engine_id="3801134842523942912")


async def main():
    # agent_engine = agent_engines.create()
    # print(f"Created Agent Engine: {agent_engine.resource_name}")

    event ={
        "content": {
            "parts": [
                {
                    "text": "Hi, I am Namish"
                }
            ],
            "role": "user"
        },
        "usageMetadata": {
            "candidatesTokenCount": 138,
            "candidatesTokensDetails": [
                {
                    "modality": "TEXT",
                    "tokenCount": 138
                }
            ],
            "promptTokenCount": 18928,
            "promptTokensDetails": [
                {
                    "modality": "TEXT",
                    "tokenCount": 18928
                }
            ],
            "totalTokenCount": 19066,
            "trafficType": "ON_DEMAND"
        },
        "invocationId": "e-0b9404c6-2797-4942-b98f-241e158ef405",
        "author": "financial_assistant",
        "actions": {
            "stateDelta": {},
            "artifactDelta": {},
            "requestedAuthConfigs": {}
        },
        "id": "d5322041-609f-46b3-9e0e-09e2694c8101",
        "timestamp": 1753290329.133947
    }

    # mock session
    session = Session(
        id="123",
        app_name="fi_app",
        user_id="user123",
        state={},
        events=[
            Event(**event)
        ]
    )
    # await service.add_session_to_memory(session)
    response: SearchMemoryResponse = await service.search_memory(app_name="simple_agent", user_id="c5a8df11-1dfb-484b-a169-32a83d0b927a", query="Is user in debt?")
    print(response)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    _ = load_dotenv()
    asyncio.run(main())