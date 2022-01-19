"""Define the FastAPI app."""

from typing import List

from fastapi import FastAPI

from . import models
from .. import operations

app = FastAPI(title="DenseEdia")


@app.get(
    path="/edium",
    operation_id="get_all_edia",
    summary="Get the list of all edia",
    response_model=List[models.EdiumSimpleGetModel],
    tags=["Edia"],
)
def get_all_edia() -> List[models.EdiumSimpleGetModel]:
    """Get the list of all edia."""
    edia = operations.get_all_edia()
    content = [edium.to_simple_model() for edium in edia]
    return content
