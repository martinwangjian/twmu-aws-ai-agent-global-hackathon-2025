# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Long-term memory hook for semantic search across sessions."""

import logging
import os

from bedrock_agentcore.memory import MemoryClient
from strands.hooks import BeforeInvocationEvent, HookProvider, HookRegistry

from .memory import retrieve_memories_for_actor

logger = logging.getLogger(__name__)


class LongTermMemoryHook(HookProvider):
    """Inject semantic search results from AgentCore Memory before model invocation."""

    def __init__(self, memory_id: str):
        self.memory_id = memory_id
        region = os.getenv("AWS_REGION", "us-east-1")
        self.memory_client = MemoryClient(region_name=region)

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_before_invocation)

    def on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """Retrieve relevant memories and inject as system context."""
        if not event.agent.messages:
            return

        last_message = event.agent.messages[-1]
        if last_message.get("role") != "USER":
            return

        user_query = last_message.get("content", "")
        if not user_query:
            return

        actor_id = event.agent.state.get("actor_id")
        if not actor_id:
            return

        try:
            memories = retrieve_memories_for_actor(
                memory_id=self.memory_id,
                actor_id=actor_id,
                search_query=user_query,
                memory_client=self.memory_client,
            )

            if memories:
                # Format memories as context
                context_parts = []
                for mem in memories:
                    content = mem.get("content", "")
                    context_parts.append(f"- {content}")

                context = "\n".join(context_parts)

                # Inject into system prompt
                if event.agent.system_prompt is None:
                    event.agent.system_prompt = ""

                event.agent.system_prompt += f"\n\nRelevant past context:\n{context}"
                logger.info(f"Injected {len(memories)} semantic memories into context")

        except Exception as e:
            logger.warning(f"Failed to retrieve semantic memories: {e}")
