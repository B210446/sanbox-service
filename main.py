from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from faker import Faker
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel

fake = Faker()
app = FastAPI()

destinations = []
reviews = []


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code = 422,
        content = {
            "status": "failure",
            "message": "Validation Error : " + str(exc),
            "code": 422,
            "data": None,
            "links": {
                "self": None,
                "next": None,
                "prev": None
                }
         } ,
    )

for i in range(1, 50):
    temp = []
    imagePath = []
    for _ in range(1, 5):
        path = {
            "url": fake.image_url(),
            "content_description": fake.slug()
        }

        imagePath.append(path)

    for j in range(1, 15):
        review = {
                "id": j,
                "username": fake.simple_profile()["username"],
                "place_id": i,
                "rating": fake.random_int(min=1, max=5),
                "desc": fake.sentence(nb_words=10),
                "date": fake.date_this_year(),
                "link": "https://localhost:3000/api/v1/place/"+str(i)+"/review",
            }

        reviews.append(review)
        temp.append(review)

    data = {
        "id": i,
        "name": fake.street_name(),
        "image_path": imagePath,
        "location": fake.street_name(),
        "long": fake.longitude(),
        "latt": fake.latitude(),
        "description": fake.paragraph(nb_sentences=5),
        "open_link": fake.url(),
        "review_link": "https://localhost:3000/api/v1/place/"+str(i)+"/review",
        "is_favorite":  fake.boolean(chance_of_getting_true=25),
        "rating": fake.random_int(min=1, max=5),
        "top_reviews": temp,
    }

    destinations.append(data)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v1/home")
async def read_home(key: str, user: str, page: Optional[int] = None):
    return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[0:20],
        "links": {
            "self": "https://localhost:3000/api/v1/home?page=1",
            "next": "https://localhost:3000/api/v1/home?page=2",
            "prev": None
        }
    }


@app.get("/api/v1/wishlist")
async def read_whistlist(key: str, user: str, page: Optional[int] = None):
     return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[0:10],
        "links": {
            "self": "https://localhost:3000/api/v1/wishlist?page=1",
            "next": None,
            "prev": None
        }
    }


@app.get("/api/v1/review")
async def read_review(key: str, user: str, page: Optional[int] = None):
    return{
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": reviews[0:10],
        "links": {
            "self": "https://localhost:3000/api/v1/review?page=1",
            "next": None,
            "prev": None
        }
    }


@app.post("/api/v1/search")
async def search_places(key: str, user: str, q: Optional[str] = None, image: Optional[UploadFile] = File(...), page: Optional[int] = None):
    return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[0:10],
        "links": {
            "self": "https://localhost:3000/api/v1/search?page=1",
            "next": "https://localhost:3000/api/v1/search?page=2",
            "prev": None
        }
    }


@app.get("/api/v1/place/{id}")
async def get_place(id, key: str, user: str):
    return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[0],
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
    }


@app.get("/api/v1/place/{id}/review")
async def get_review_place(id, key: str, page: Optional[int] = None):
     return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[0]["top_reviews"],
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
    }


@app.post("/api/v1/place/{id}/review")
async def create_review_place(id, key: str, user: str = Form(...), desc: str = Form(...), date: str = Form(...), rating: float = Form(...)):
    return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 201,
        "data": None,
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
    }
