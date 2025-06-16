# app/models/context_models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatContext:

    partyId: Optional[str] = None
    sessionId: Optional[str] = None
    serviceIdentifier: Optional[str] = None