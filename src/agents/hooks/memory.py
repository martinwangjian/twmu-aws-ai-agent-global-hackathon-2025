# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Memory utilities for AgentCore."""

import json
import logging
from pathlib import Path
from typing import Any

from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)


class MemoryConfig:
    """Memory configuration from JSON file or environment."""

    _cached_config: dict[str, Any] | None = None
    _cached_path: str | None = None

    def __init__(self, config_path: str = "memory-config.json"):
        self.config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        if MemoryConfig._cached_config and MemoryConfig._cached_path == self.config_path:
            return

        # Try environment variable first
        import os

        memory_id = os.getenv("AGENTCORE_MEMORY_ARN")
        if memory_id:
            MemoryConfig._cached_config = {"memory_id": memory_id}
            MemoryConfig._cached_path = "env"
            logger.info(f"Using memory from environment: {memory_id}")
            return

        # Try config file
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Memory config not found: {self.config_path}")

        with open(config_file) as f:
            MemoryConfig._cached_config = json.load(f)
            MemoryConfig._cached_path = self.config_path
            logger.info(f"Using memory from config file: {self.config_path}")

    @property
    def memory_id(self) -> str:
        config = MemoryConfig._cached_config
        if config is None:
            raise ValueError("Memory config not loaded")
        return str(config["memory_id"])


def retrieve_memories_for_actor(
    memory_id: str, actor_id: str, search_query: str, memory_client: MemoryClient
) -> list[dict[str, Any]]:
    """Retrieve semantic memories for actor using AgentCore Memory."""
    namespace = f"/actor/{actor_id}/"

    try:
        memories = memory_client.retrieve_memories(
            memory_id=memory_id, namespace=namespace, query=search_query
        )
        logger.debug(f"Retrieved {len(memories) if memories else 0} memories for {actor_id}")
        return list(memories) if memories else []
    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        return []
