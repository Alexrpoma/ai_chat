from typing import List, Optional, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Template for a single message in the history."""
    role: str = Field(..., description="The role of the sender, 'user' or 'assistant'.")
    content: str = Field(..., description="The content of the message.")

class ChatRequest(BaseModel):
    """Template for the chat request to the endpoint."""
    content: str = Field(..., description="The user's current question or entry.")
    contentType: str = Field("text", description="The content type. Default is 'text' for conversational responses.")
    history: List[ChatMessage] = Field([], description="The history of the previous conversation.")

    partyId: Optional[str] = Field(None, description="Unique identifier of the client/user.")
    sessionId: Optional[str] = Field(None, description="Unique identifier for the chat session.")
    serviceIdentifier: Optional[str] = Field(None, description="Identifier of the specific service (e.g., phone number).")

class ResponseMessage(BaseModel):
    partyId: Optional[str] = Field(None)
    sessionId: Optional[str] = Field(None)
    sender: str = "AGENT"
    content: str
    contentType: str = "text"

class ResponseData(BaseModel):
    transactionId: Optional[Any] = Field(None)
    messages: List[ResponseMessage]

class ChatResponse(BaseModel):
    responseCode: str = "OK"
    responseMessage: str = "OK"
    data: ResponseData