import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "localhost"
        self.smtp_port = 587
        
    async def send_email(self, to_email: str, subject: str, body: str):
        """Send email notification (simulated for demo)"""
        try:
            # Simulate email sending delay
            await asyncio.sleep(0.1)
            
            logger.info(f"📧 Email sent to {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
