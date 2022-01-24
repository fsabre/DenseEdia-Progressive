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


@app.post(
    path="/edium/{edium_id}",
    operation_id="create_one_edium",
    summary="Create one edium",
    response_model=models.EdiumModel,
    tags=["Edia"],
)
def create_one_edium(body: models.CreateEdiumModel) -> models.EdiumModel:
    """Create one edium."""
    return operations.create_one_edium(body)


@app.delete(
    path="/edium/{edium_id}",
    operation_id="delete_one_edium",
    summary="Delete one edium",
    response_model=models.EdiumModel,
    tags=["Edia"],
)
def delete_one_edium(edium_id: int) -> models.EdiumModel:
    """Delete one edium."""
    try:
        return operations.delete_one_edium(edium_id)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])


@app.get(
    path="/edium/{edium_id}/elements",
    operation_id="get_one_edium_elements",
    summary="Get one edium elements and their last version",
    response_model=List[models.ElementModel],
    tags=["Elements"],
)
def get_one_edium_elements(edium_id: int) -> List[models.ElementModel]:
    """Get one edium elements and their last version."""
    return operations.get_one_edium_elements(edium_id)


@app.get(
    path="/element/{element_id}",
    operation_id="get_one_element",
    summary="Get one element and its last version",
    response_model=models.ElementModel,
    tags=["Elements"],
)
def get_one_element(element_id: int) -> models.ElementModel:
    """Get one element and its last version."""
    try:
        return operations.get_one_element(element_id)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])


@app.get(
    path="/element/{element_id}/full",
    operation_id="get_one_full_element",
    summary="Get one element and all its versions",
    response_model=models.ElementModel,
    tags=["Elements"],
)
def get_one_full_element(element_id: int) -> models.ElementModel:
    """Get one element and all its versions."""
    try:
        return operations.get_one_full_element(element_id)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])


@app.post(
    path="/edium/{edium_id}/element",
    operation_id="create_one_element",
    summary="Create one element and its first version",
    response_model=models.ElementModel,
    tags=["Elements"],
)
def create_one_element(edium_id: int, body: models.CreateElementModel) -> models.ElementModel:
    """Create one element and its last version."""
    try:
        return operations.create_one_element(edium_id, body)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])
    except exceptions.DuplicateElementName as err:
        raise HTTPException(status_code=409, detail=err.args[0])
