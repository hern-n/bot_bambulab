import logging
import os

import dotenv
from agentmail import AgentMail

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the client
client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))


def delete_inbox(inbox_id: str) -> None:
    client.inboxes.delete(inbox_id=inbox_id)
    logger.info(f"Deleted Inbox: {inbox_id}")


# --- Create an Inbox ---
# Creates a new inbox with a default agentmail.to domain
delete_inbox("fantasticrain702@agentmail.to")
delete_inbox("adventurousdiscussion965@agentmail.to")
delete_inbox("tensefootball732@agentmail.to")
