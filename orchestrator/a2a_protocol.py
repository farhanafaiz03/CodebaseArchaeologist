"""
Simple in-memory Agent-to-Agent (A2A) protocol using asyncio queues.
Agents can register inbox queues and send messages to each other by name.
This is intentionally lightweight and suitable for local/demo use.
"""

import asyncio
from typing import Dict, Any


class A2AProtocol:
    def __init__(self):
        # agent_name -> asyncio.Queue
        self._inboxes: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def register(self, agent_name: str):
        async with self._lock:
            if agent_name in self._inboxes:
                return
            self._inboxes[agent_name] = asyncio.Queue()

    async def send(self, to_agent: str, message: Dict[str, Any]):
        """Send a message to another agent's inbox."""
        if to_agent not in self._inboxes:
            raise ValueError(f"Agent {to_agent} not registered.")
        await self._inboxes[to_agent].put(message)

    async def recv(self, agent_name: str, timeout: float = None):
        """Receive next message for agent (awaits)."""
        if agent_name not in self._inboxes:
            raise ValueError(f"Agent {agent_name} not registered.")
        if timeout is None:
            msg = await self._inboxes[agent_name].get()
            return msg
        else:
            try:
                msg = await asyncio.wait_for(self._inboxes[agent_name].get(), timeout=timeout)
                return msg
            except asyncio.TimeoutError:
                return None

    async def unregister(self, agent_name: str):
        async with self._lock:
            if agent_name in self._inboxes:
                del self._inboxes[agent_name]
