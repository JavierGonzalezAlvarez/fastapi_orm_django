from manage import init_django
init_django()

from enum import Enum
from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field, ValidationError, validator
from asgiref.sync import sync_to_async
from fastapi.middleware.cors import CORSMiddleware

from django.db import IntegrityError
from db.models import Users
from typing import List, Dict
import logging
import requests

origins = [
    "http://localhost:4200",
    "http://localhost:8080",
]

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="api.log",
    )

#instance of FastAPI
app = FastAPI(
    title="Api Ecommerce",
    description="Api Ecommerce Asia high-qualitu products and competitive prices. 2023-04-02",
    version="0.1.0",
    terms_of_service="http://eccommerce/terms/",
    contact={
        "name": "Lazarillo",
        "url": "http://lazarillo_tormes/contact/",
        "email": "lazarillo@tormes.es",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users",
    },
    {
        "name": "add_user",
        "description": "Add an user",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
        {
        "name": "countries",
        "description": "Operations with countries",
    },
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CountriesList(BaseModel):
    '''list of user's countries'''
    values: Dict
 
    class Config:
        '''orm'''
        orm_mode = True

class Countries(BaseModel):
    '''countries for the user'''
    id: str
    name: str
    power: List[dict]
    scores: List[dict]

    class Config:
        '''orm'''
        orm_mode = True

class User(BaseModel):
    '''fields for users'''
    id: int | None = Field(default=1, gt=0, description="Id")
    username: str | None
    useremail: str | None
    countries: list[str] | None = []

    class Config:
        '''orm'''
        orm_mode = True


data_first = Users.objects.all().first()
data_all = Users.objects.all()

items = [
    { obj.id : User(id=obj.id, username=obj.username, useremail=obj.useremail, countries=obj.countries)}
        for obj in data_all
]
print(items)

@app.get("/")
async def main():
    '''main endpoint'''
    return {"msg": "Hello World"}

#task: 2
@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "User already exists"},
        400: {"description": "No parameters provided for update"},
    },
    tags=["add_user"]
)
async def add_user(
    item: User,
 ) -> dict[str, str | User]:
    '''Task2. Add an user with fields:
        - id: int (starting by 1)
        - username: str
        - useremail: str
        - countries: list of countries [str]
    '''
    # managing constrains
    for dictionary in items:
        if item.id in dictionary:
            raise HTTPException(
                status_code=409,
                detail=f"User with {item.id=} already exists."
            )

    #if not all(pay_load is None for pay_load in (item.id, item.username, item.useremail)):
    #    raise HTTPException(
    #        status_code=400, detail="Some fields are empty"
    #    )

    if item.id is None:
        raise HTTPException(
            status_code=400, detail="Field id is empty"
        )
    if item.username is None:
        raise HTTPException(
            status_code=400, detail="Field username is empty"
        )
    if item.useremail is None:
        raise HTTPException(
            status_code=400, detail="Field useremail is empty"
        )
    if item.countries is None:
        raise HTTPException(
            status_code=400, detail="Field countries is empty"
        )

    try:
        new_users = Users(
            id=item.id,
            username=item.username,
            useremail=item.useremail,
            countries=item.countries
        )
        await sync_to_async(new_users.save)()
        logging.info("Created user: {%s}", new_users)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Useremail already exists")

    return {
        "status": status.HTTP_201_CREATED,
        "added": item
    }

@app.get("/firstuser", tags=["users"])
async def firstuser() -> dict[str, dict[int, User]]:
    '''This endpoint isn't required in the challenge. Get first user from table users.
        - endpoint: http://127.0.0.1:8000/firstuser
    '''
    fist_user = {
       data_first.id : User(
                        id=data_first.id,
                        username=data_first.username,
                        useremail=data_first.useremail
                    )
    }
    return {"first user": fist_user}

@app.get("/allusers", tags=["users"])
async def allusers() -> dict[str, dict[int, User]]:
    '''This endpoint isn't required in the challenge. Get all users from table users.
        - endpoint: http://127.0.0.1:8000/allusers
    '''
    all_users = {
        obj.id : User(id=obj.id, username=obj.username, useremail=obj.useremail)
            for obj in data_all
    }
    return {"users": all_users}

def get_countries():
    '''
        function to get some data from the enpoint countries.json
    '''
    response = requests.get('https://power.lowyinstitute.org/countries.json', timeout=60)
    if response.status_code == 200:
        json_data = response.json()
    else:
        print(f'Request failed with status code {response.status_code}')

    items_countries = {
        c["id"] : Countries(id=c["id"], name=c["name"], power=c["power"], scores=c["scores"])
            for c in json_data["countries"]
    }
    return items_countries

#task: 3
@app.get("/countries", tags=["countries"])
async def countries() -> dict[str, dict[str, Countries]]:
    '''This endpoint isn't required in the challenge. Get all countries from the endpoint:
        - https://power.lowyinstitute.org/countries.json
    '''
    items_countries = get_countries()
    return {"countries": items_countries}

def get_countries_for_userid(user_id):
    '''getuserid'''
    return Users.objects.filter(id=user_id).values_list("countries", flat=True)

@app.get(
    "/users/{userId}/countries",
    responses={
        200: {"description": "User hasn't subscribe to any country"},
        400: {"description": "No parameter provided for update"},
        404: {"description": "User doesn't exist"},
    },
    tags=["users"]
)
def users_countries(
        userId: int = Path(
            title="userId",
            description="Unique integer that specifies an user",
            ge=1
        )   
) -> dict[str, dict[str, CountriesList]]:
    '''Task 3: get countries for one user'''
    user_dict = { user_obj.id for user_dict in items
                    for user_id, user_obj in user_dict.items() }

    if userId not in user_dict:
        raise HTTPException(
            status_code=404,
            detail=f"User with {userId=} doesn't exists."
        )

    list_countries_user = get_countries_for_userid(userId)
    list_filtered = list(list_countries_user)[0]
    items_countries = get_countries()

    all_countries = {}
    for country in items_countries.values():
        if country.id in list_filtered:
            total_score = 0
            for score in country.scores:
                if score['year'] >= 2018:
                    total_score += score['score']
            total_power = 0
            for power in country.power:
                if power['year'] >= 2018:
                    total_power += power['trend'] + power['influence'] \
                                + power['resources'] + power['expected']

            all_countries[country.id] = {"score": total_score, "power": total_power}

    items_country = {
        k : CountriesList(values=v)
            for k, v in all_countries.items()
    }
    return {"countries": items_country}