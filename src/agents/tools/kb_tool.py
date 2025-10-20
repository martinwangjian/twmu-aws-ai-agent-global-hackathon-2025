# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Knowledge Base retrieval tool for restaurant information."""

import logging
import os

import boto3
from strands import tool

logger = logging.getLogger(__name__)

KB_ID = os.getenv("RESTAURANT_KB_ID", "ZN8KCFCWX3")


@tool
def search_restaurant_info(query: str) -> str:
    """Search restaurant information including menu items, hours, and allergen details.

    Args:
        query: Search query (e.g., "What's on the menu?", "Do you have gluten-free options?")
    """
    try:
        # Create client inside function to use current credentials
        client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
        
        response = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
        )

        results = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {}).get("text", "")
            if content:
                results.append(content)

        return "\n\n".join(results) if results else "No information found."

    except Exception as e:
        logger.error(f"KB retrieval error: {e}")
        return f"Error retrieving information: {str(e)}"
