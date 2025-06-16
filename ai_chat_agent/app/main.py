from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models.chat_models import ChatRequest, ChatResponse, ResponseMessage, ResponseData
from .services.agent_service import AgentService

app = FastAPI(
    title="Alva Agent API",
    description="A REST service for interacting with the Alva AI agent.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_service = AgentService()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    try:

        history_dicts = [msg.model_dump() for msg in request.history]

        metadata = {
            "partyId": request.partyId,
            "sessionId": request.sessionId,
            "serviceIdentifier": request.serviceIdentifier
        }

        # Filter any None value to not pass empty keys
        metadata = {k: v for k, v in metadata.items() if v is not None}

        processed_result = await agent_service.process_chat(
            prompt=request.content,
            history=history_dicts,
            metadata={
                "partyId": request.partyId,
                "sessionId": request.sessionId,
                "serviceIdentifier": request.serviceIdentifier
            }
        )

        response_message = ResponseMessage(
            partyId=request.partyId,
            sessionId=request.sessionId,
            content=processed_result.content
        )

        response_data = ResponseData(
            transactionId=processed_result.transactionId,
            messages=[response_message]
        )

        return ChatResponse(data=response_data)

    except Exception as e:
        print(f"❌ Fatal error on the /chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred."
        )


@app.get("/", include_in_schema=False)
def read_root():
    return {
        "message": "The Alva Agent Server is up and running. Use the POST /chat endpoint to interact. Visit /docs for API documentation."}