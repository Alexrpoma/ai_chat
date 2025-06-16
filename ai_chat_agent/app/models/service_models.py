from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class ProcessedChatResult:
    content: str
    transactionId: Optional[Any] = None