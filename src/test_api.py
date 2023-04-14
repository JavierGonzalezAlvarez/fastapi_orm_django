'''
## test
* path => /src/
* $ pytest
'''

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from pydantic import BaseModel, Field
from typing import List, Dict
import requests

class User(BaseModel):
    '''fields for users'''
    id: int | None = Field(default=1, gt=0, description="Id")
    username: str | None
    useremail: str | None
    countries: list[str] | None = []

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

class CountriesList(BaseModel):
    '''list of user's countries'''
    values: Dict
 
    class Config:
        '''orm'''
        orm_mode = True

items = [
    { 1 : User(id=1, username="peter1", useremail="peter1@gmail.com", countries=["JP"])},
    { 2 : User(id=2, username="peter2", useremail="peter2@gmail.com", countries=[])}
]

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

#instance of FastAPI
app = FastAPI()

@app.get("/")
async def main():
    '''main endpoint'''
    return {"msg": "Hello World"}

@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "User already exists"},
        400: {"description": "No parameters provided for update"},
    },
)
async def add_user(
    item: User,
 ) -> dict[str, str | User]:
    '''test add_user'''
    return {
        "status": status.HTTP_201_CREATED,
        "added": item
    }

@app.get(
    "/users/{userId}/countries",
    responses={
        200: {"description": "User hasn't subscribe to any country"},
        400: {"description": "No parameter provided for update"},
        404: {"description": "User doesn't exist"},
    }
)
async def users_countries(userId: int) -> dict[str, dict[str, CountriesList]]:
    '''Task 3: get countries for one user'''
    userId = 1
    list_filtered = ['JP']
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
                    total_power += power['trend'] + power['influence'] + power['resources'] + power['expected']
            all_countries[country.id] = {"score": total_score, "power": total_power}
    items_country = {
        k : CountriesList(values=v)
            for k, v in all_countries.items()
    }
    return {"countries": items_country}

client = TestClient(app)

def test_main():
    '''test root'''
    response = client.get("/")
    assert response.status_code == 200    
    assert response.json() == {"msg": "Hello World"}

def test_add_user():
    '''test for endpoint /users'''
    response = client.post(
        "/users",
        json={"id": 1, "username": "peter", "useremail": "peter@gmail.com", "countries": []},
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "201",
        "added": {
            "id": 1,
            "username": "peter",
            "useremail": "peter@gmail.com",
            "countries": []
        }
    }

def test_users_countries1():
    '''test for endpoint /users/{userId}/countries'''    
    response = client.get("/users/1/countries")
    assert response.status_code == 200
    assert response.json() == {
        "countries":
            {"JP":
                {"values":
                    {
                        "score":159.478486,
                        "power":444.54699999999997
                    }
                }
            }
        }