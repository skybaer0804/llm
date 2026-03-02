from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all gateway agents."""

    name: str

    @abstractmethod
    async def run(self, message: str, credentials: dict | None = None) -> dict:
        """Execute the agent with a user message.

        Returns {"response": str, "tool_calls_count": int, ...}
        """
        ...
