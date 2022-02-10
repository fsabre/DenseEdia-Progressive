"""Provide a function to run the FastAPI."""

import uvicorn

from .app import app
from ..constants import API_PORT


def launch_server() -> None:
    """Run the FastApi server."""
    print(f"Documentation page at http://localhost:{API_PORT}/docs")
    uvicorn.run(app, port=API_PORT)
