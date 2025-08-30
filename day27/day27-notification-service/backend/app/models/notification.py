import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class Notification:
    def __init__(self, user_id: str, event_type: str, title: str, message: str, data: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.event_type = event_type
        self.title = title
        self.message = message
        self.data = data
        self.status = NotificationStatus.PENDING
        self.created_at = datetime.utcnow()
        self.read_at: Optional[datetime] = None

class NotificationRequest(BaseModel):
    user_id: str
    event_type: str
    title: str
    message: str
    data: Dict[str, Any] = {}

class NotificationPreference(BaseModel):
    user_id: str
    event_type: str
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
