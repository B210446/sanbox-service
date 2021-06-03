from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from faker import Faker
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import requests

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

for i in range(1, 70):
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
async def read_home(key: str, user: str, page: Optional[int] = 1):
    end = 15*page
    start = (end-15)+1

    return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[start:end],
        "links": {
            "self": "https://localhost:3000/api/v1/home?page=1",
            "next": "https://localhost:3000/api/v1/home?page=2",
            "prev": None
        }
    }


@app.get("/api/v1/wishlist")
async def read_whistlist(key: str, user: str, page: Optional[int] = 1):
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
async def read_review(key: str, user: str, page: Optional[int] = 1):
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
async def search_places(key: str, user: str, q: Optional[str] = None, image: Optional[UploadFile] = File(None), page: Optional[int] = 1):
    
    end = 15*page
    start = (end-15)+1

    if image is not None:
        return {
        "status": "success",
        "message": "Successfully fetched with image",
        "code": 200,
        "data": destinations[start:end],
        "links": {
            "self": "https://localhost:3000/api/v1/search?page=1",
            "next": "https://localhost:3000/api/v1/search?page=2",
            "prev": None
        }
    }
    else:
        return {
        "status": "success",
        "message": "Successfully fetched",
        "code": 200,
        "data": destinations[start:end],
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
async def create_review_place(id, key: str, user: str = Form(...), desc: str = Form(...), rating: int = Form(...), images: Optional[List[UploadFile]] = File(None), ):
    if images is not None:
        return {
        "status": "success",
        "message": "Successfully Create Data with Image",
        "code": 201,
        "data": None,
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
        }
    else:
        return {
        "status": "success",
        "message": "Successfully Create Data",
        "code": 201,
        "data": None,
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
        }


# ===========================================================================================================================
# ================================================ Service Google ===========================================================
# ===========================================================================================================================

API_KEY = "AIzaSyDBmn1-rBVvIQU6gKIDpvqfCRJut_uVgeA"

@app.get("/api/v1/google/place/nearbysearch")
async def nearby_search(location: Optional[str] = None):
    query = {
        "location": location,
        "type": "tourist_attraction",
        "rankby": "distance",
        "key": API_KEY
    }
    req = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=query)
    resp = req.json()

    if (resp["status"] == "OK"):

        data = mappingPlaces(resp)
        next_page_token = None
        
        if "next_page_token" in resp:
            next_page_token = resp["next_page_token"]

        return {
        "status": "success",
        "message": "Successfully fetch data",
        "code": 201,
        "data": data,
        "links": {
            "next_page_token": next_page_token
        }
        }
    else:
        return {
        "status": "failure",
        "message": "Request Failed",
        "code": 422,
        "data": None,
        "links": {
            "next_page_token": None
        }
        }


@app.get("/api/v1/google/place/search")
async def places_search(q: str):
    query = {
        "region": "id",
        "query": q,
        "type": "tourist_attraction",
        "key": API_KEY
    }
    req = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=query)
    resp = req.json()

    if (resp["status"] == "OK"):

        data = mappingPlaces(resp)
        next_page_token = None

        if "next_page_token" in resp:
            next_page_token = resp["next_page_token"]

        return {
        "status": "success",
        "message": "Successfully fetch data",
        "code": 201,
        "data": data,
        "links": {
            "next_page_token": next_page_token
        }
        }
    else:
        return {
        "status": "failure",
        "message": "Request Failed",
        "code": 422,
        "data": None,
        "links": {
            "next_page_token": None
        }
        }

@app.get("/api/v1/google/place/detail")
async def get_google_place(place_id: str):
    query = {
        "place_id": place_id,
        "key": API_KEY
    }
    req = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=query)
    resp = req.json()

    if (resp["status"] == "OK"):

        data = mappingPlace(resp)

        return {
        "status": "success",
        "message": "Successfully fetch data",
        "code": 201,
        "data": data,
        "links": {
            "self": None,
            "next": None,
            "prev": None,
        }
        }
    else:
        return {
        "status": "failure",
        "message": "Request Failed",
        "code": 422,
        "data": None,
        "links": {
            "self": None,
            "next": None,
            "prev": None
        }
        }
    
def mappingPlaces(resp: dict):
    places = []

    for place in resp["results"]:

        if "photos" not in place:
            continue

        poster = {
            "url": "https://maps.googleapis.com/maps/api/place/photo?key="+API_KEY+"&maxwidth=800&photoreference="+place["photos"][0]["photo_reference"],
            "content_description": place["name"]
        }

        location = None
        if "vicinity" in place:
            location = place["vicinity"]

        if "formatted_address" in place:
            location = place["formatted_address"]

        data = {
        "id": place["place_id"],
        "name": place["name"],
        "poster": poster,
        "location": location,
        "lat": place["geometry"]["location"]["lat"],
        "lng": place["geometry"]["location"]["lng"],
        "is_favorite":  False,
        "rating": place["rating"],
        }

        places.append(data)
    
    return places


def mappingPlace(resp: dict):
    place = resp["result"]

    photos = []
    reviews = []

    for photo in place["photos"]:
        image = {
        "url": "https://maps.googleapis.com/maps/api/place/photo?key="+API_KEY+"&maxwidth=800&photoreference="+photo["photo_reference"],
        "content_description": place["name"]
        }
        photos.append(image)

    for item in place["reviews"]:
        review = {
        "username": item["author_name"],
        "place_id": place["place_id"],
        "rating": item["rating"],
        "desc": item["text"],
        "date": item["time"],
        }
        reviews.append(review)


    wiki = getDescriptionFromWiki(place["name"])

    desc = ""
    for item in wiki["query"]["pages"]:

        if "extract" in wiki["query"]["pages"][item]:
            desc = wiki["query"]["pages"][item]["extract"]

    data = {
    "id": place["place_id"],
    "name": place["name"],
    "image_path": photos,
    "location": place["vicinity"],
    "lat": place["geometry"]["location"]["lat"],
    "lng": place["geometry"]["location"]["lng"],
    "description": desc,
    "open_link": place["website"],
    "is_favorite":  False,
    "rating": place["rating"],
    "top_reviews": reviews,
    }

    return data


def getDescriptionFromWiki(title: str):
    query = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": None,
        "explaintext": None,
        "redirects": 1,
        "titles": title
    }
    req = requests.get("https://en.wikipedia.org/w/api.php", params=query)
    resp = req.json()

    return resp


# https://search.google.com/local/reviews?placeid=ChIJaac90jeuEmsR0Evy-Wh9AQ8