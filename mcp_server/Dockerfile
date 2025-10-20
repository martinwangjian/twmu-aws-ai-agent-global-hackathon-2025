FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp 'strands-agents-tools[a2a_client]'

COPY a2a_orchestrator_mcp.py .

CMD ["python", "a2a_orchestrator_mcp.py"]
