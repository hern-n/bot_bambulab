from typing import Optional
import logging
import re
import os

import dotenv
from agentmail import AgentMail

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))


def create_inbox() -> str:
    """Create an inbox and return its ID."""
    inbox = client.inboxes.create()
    logger.info("Inbox created successfully")
    return inbox.inbox_id


def get_email(inbox_id: str) -> Optional[str]:
    """Return the HTML body of the first email from the inbox with the given ID."""
    response = client.inboxes.messages.list(inbox_id=inbox_id, limit=1)
    messages = response.messages if hasattr(response, "messages") else response
    if messages:
        email = messages[0]
        message_id = getattr(email, "message_id", None)
        if message_id:
            full_email = client.inboxes.messages.get(
                inbox_id=inbox_id, message_id=message_id
            )
            return (
                getattr(full_email, "html", None)
                or getattr(full_email, "extracted_html", None)
                or getattr(full_email, "text", None)
                or getattr(full_email, "extracted_text", None)
            )
    return None


def get_code(html: str) -> Optional[int]:
    """Extract the 6-digit verification code from the email HTML."""
    match = re.search(r"font-size:24px[^>]*>\s*(\d{6})\s*<", html)
    return str(match.group(1)) if match else None


def delete_inbox(inbox_id: str) -> None:
    client.inboxes.delete(inbox_id=inbox_id)
    logger.info(f"Deleted Inbox: {inbox_id}")


def delete_all_inboxes() -> None:
    for i in list_inboxes():
        delete_inbox(i[0])


def list_inboxes() -> list[tuple[str, str]]:
    """Return all inboxes with their IDs. Returns list of (inbox_id, name) tuples."""
    response = client.inboxes.list()
    inboxes = response.inboxes if hasattr(response, "inboxes") else response
    return [(inbox.inbox_id, getattr(inbox, "name", "")) for inbox in inboxes]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    delete_all_inboxes()
    inbox_id = create_inbox()
    logger.info(f"Created inbox: {inbox_id}")

    input_str = input()
    code = get_code(get_email(inbox_id))
    logger.info(f"Verification code: {code}")
