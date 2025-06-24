from flask import Blueprint
from spectree import SpecTree
from pydantic import BaseModel, Field
from uuid import UUID

from .. import models as models
from .. import services as services

api = Blueprint("api", __name__)

from spectree import SpecTree, SecurityScheme

spec = SpecTree(
    "flask",
    app=api,
    security_schemes=[
        SecurityScheme(
            name="bearer_token",
            data={"type": "http", "scheme": "bearer"}
        )
    ],
    security=[{"bearer_token": []}]
)


class EntryData(BaseModel):
    name: str = Field(..., min_length=1)
    amount: float = Field(...)
    category: str | None = None


class EntryUpdateData(EntryData):
    id: UUID


class EntryID(BaseModel):
    id: UUID


@api.post("/create")
@spec.validate(json=EntryData, tags=["api"])
def create_entry(json: EntryData):
    models.create_entry(json.name, json.amount, json.category)
    return {"message": "Entry created"}


@api.get("/get")
@spec.validate(query=EntryID, tags=["api"])
def get_entry(query: EntryID):
    entry = models.get_entry(query.id)
    if entry:
        return [entry.id, entry.name, entry.montant, entry.categorie]
    return {"error": "Entry not found"}, 404


@api.get("/get_all")
@spec.validate(tags=["api"])
def get_all():
    return models.get_all_entries()


@api.put("/update")
@spec.validate(json=EntryUpdateData, tags=["api"])
def update_entry(json: EntryUpdateData):
    models.update_entry(json.id, json.name, json.amount, json.category)
    return {"message": "Entry updated"}


@api.delete("/delete")
@spec.validate(query=EntryID, tags=["api"])
def delete_entry(query: EntryID):
    models.delete_entry(query.id)
    return {"message": "Entry deleted"}


@api.get("/export_csv")
@spec.validate(tags=["api"])
def export_csv():
    return {"csv": services.export_to_csv().getvalue()}


class CSVText(BaseModel):
    content: str


@api.post("/import_csv")
@spec.validate(json=CSVText, tags=["api"])
def import_csv(json: CSVText):
    from io import StringIO
    stream = StringIO(json.content)
    services.import_from_csv(stream)
    return {"message": "CSV imported"}

