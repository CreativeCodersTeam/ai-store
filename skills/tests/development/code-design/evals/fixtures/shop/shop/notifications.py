from typing import List, Tuple


class EmailSender:
    """Records outgoing mail; production wiring replaces it with an SMTP sender."""

    def __init__(self) -> None:
        self.sent: List[Tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject, body))
