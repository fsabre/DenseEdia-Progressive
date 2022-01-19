"""Provide a function to run the FastAPI."""

import uvicorn

from .app import app


def launch_server() -> None:
    """Run the FastApi server."""
    uvicorn.run(app)
