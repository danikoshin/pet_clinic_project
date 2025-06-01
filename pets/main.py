from enum import Enum
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db: Dict[int, Dog] = {
    0: Dog(name='Bob', pk=0, kind=DogType.terrier),
    1: Dog(name='Marli', pk=1, kind=DogType.bulldog),
    2: Dog(name='Snoopy', pk=2, kind=DogType.dalmatian),
    3: Dog(name='Rex', pk=3, kind=DogType.dalmatian),
    4: Dog(name='Pongo', pk=4, kind=DogType.dalmatian),
    5: Dog(name='Tillman', pk=5, kind=DogType.bulldog),
    6: Dog(name='Uga', pk=6, kind=DogType.bulldog)
}

post_db: List[Timestamp] = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]

_post_id_counter = max(p.id for p in post_db) + 1 if post_db else 0


@app.get('/')
async def root():
    return {}


@app.post("/post", response_model=Timestamp, summary="Create Timestamp Post")
async def create_timestamp_post():
    global _post_id_counter
    new_id = _post_id_counter
    current_timestamp = int(time.time())

    new_post = Timestamp(id=new_id, timestamp=current_timestamp)
    post_db.append(new_post)
    _post_id_counter += 1
    return new_post


@app.get("/dog", response_model=List[Dog], summary="Get Dogs")
async def get_dogs(kind: Optional[DogType] = Query(None, description="Filter by dog kind")):
    if kind:
        return [dog for dog in dogs_db.values() if dog.kind == kind]
    return list(dogs_db.values())


@app.post("/dog", response_model=Dog, summary="Create Dog")
async def create_dog(dog: Dog):
    if dog.pk in dogs_db:
        raise HTTPException(status_code=409, detail=f"Dog with pk {dog.pk} already exists.")
    dogs_db[dog.pk] = dog
    return dog


@app.get("/dog/{pk}", response_model=Dog, summary="Get Dog By Pk")
async def get_dog_by_pk(pk: int):
    dog = dogs_db.get(pk)
    if dog is None:
        raise HTTPException(status_code=404, detail=f"Dog with pk {pk} not found.")
    return dog


@app.patch("/dog/{pk}", response_model=Dog, summary="Update Dog")
async def update_dog(pk: int, dog_update: Dog):
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail=f"Dog with pk {pk} not found.")

    if dog_update.pk != pk:
        raise HTTPException(
            status_code=400,
            detail=f"Path pk ({pk}) does not match pk in request body ({dog_update.pk})."
        )

    dogs_db[pk] = dog_update
    return dogs_db[pk]