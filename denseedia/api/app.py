"""Define the FastAPI app."""

from typing import List

from fastapi import FastAPI, HTTPException

from . import operations
from .. import exceptions, models

app = FastAPI(title="DenseEdia")


@app.get(
    path="/edium",
    operation_id="get_all_edia",
    summary="Get the list of all edia",
    response_model=List[models.EdiumModel],
    tags=["Edia"],
)
def get_all_edia() -> List[models.EdiumModel]:
    """Get the list of all edia."""
    return operations.get_all_edia()


@app.get(
    path="/edium/{edium_id}",
    operation_id="get_one_edium",
    summary="Get one edium",
    response_model=models.EdiumModel,
    tags=["Edia"],
)
def get_one_edium(edium_id: int) -> models.EdiumModel:
    """Get one edium."""
    try:
        return operations.get_one_edium(edium_id)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])
