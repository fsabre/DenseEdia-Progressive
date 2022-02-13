"""Define the FastAPI app."""

from typing import List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import operations
from .. import exceptions, models

app = FastAPI(title="DenseEdia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    path="/edium",
    operation_id="create_one_edium",
    summary="Create one edium",
    response_model=models.EdiumModel,
    tags=["Edia"],
)
def create_one_edium(body: models.CreateEdiumModel) -> models.EdiumModel:
    """Create one edium."""
    return operations.create_one_edium(body)


@app.patch(
    path="/edium/{edium_id}",
    operation_id="modify_one_edium",
    summary="Modify one edium",
    response_model=models.EdiumModel,
    tags=["Edia"],
)
def modify_one_edium(edium_id: int, body: models.ModifyEdiumModel) -> models.EdiumModel:
    """Modify one edium."""
    try:
        return operations.modify_one_edium(edium_id, body)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])


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
    operation_id="get_elements_of_one_edium",
    summary="Get the elements of one edium and their versions",
    response_model=List[models.ElementModel],
    tags=["Elements"],
)
def get_elements_of_one_edium(
    edium_id: int,
    versions: models.VersionsMode.asType = Query(models.VersionsMode.NONE),
) -> List[models.ElementModel]:
    """Get the elements of one edium and their versions."""
    if versions == models.VersionsMode.ALL:
        raise HTTPException(status_code=501, detail="Retrieval of all versions is not implemented yet")
    return operations.get_elements_of_one_edium(edium_id, mode=versions)


@app.get(
    path="/element/{element_id}",
    operation_id="get_one_element",
    summary="Get one element and none, one or all of its versions",
    response_model=models.ElementModel,
    tags=["Elements"],
)
def get_one_element(
    element_id: int,
    versions: models.VersionsMode.asType = Query(models.VersionsMode.NONE),
) -> models.ElementModel:
    """Get one element and none, one or all of its versions."""
    try:
        return operations.get_one_element(element_id, mode=versions)
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


@app.delete(
    path="/element/{element_id}",
    operation_id="delete_one_element",
    summary="Delete one element",
    response_model=models.ElementModel,
    tags=["Elements"],
)
def delete_one_element(element_id: int) -> models.ElementModel:
    """Delete one element."""
    try:
        return operations.delete_one_element(element_id)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])


@app.post(
    path="/element/{element_id}/version",
    operation_id="create_one_version",
    summary="Create a new version for an element",
    response_model=models.VersionModel,
    tags=["Elements"],
)
def create_one_version(element_id: int, body: models.CreateVersionModel) -> models.VersionModel:
    """Create a new version for an element."""
    try:
        return operations.create_one_version(element_id, body)
    except exceptions.ObjectNotFound as err:
        raise HTTPException(status_code=404, detail=err.args[0])
