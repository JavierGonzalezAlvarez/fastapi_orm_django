# Versions
- python 3.11
- django 4.1.7 (ORM)
- postgres2
- fastapi 0.95.0
- linux: ubuntu 22.04

- $ virtualenv entorno_virtual -p python3.11
- $ source entorno_virtual/bin/activate
- $ pip install -r requirements.txt

## create database
$ sudo -u postgres psql
* create user and password if necessary
- user: test
- pass: 2525_ap
- CREATE DATABASE ecommerce WITH OWNER test;

## make Migrations
- path => /src/
- $ python3 manage.py makemigrations db
- $ python3 manage.py migrate db

## run api
path => /src/
$ gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --reload

## documentation
* http://127.0.0.1:8000/doc

## get data from url
* https://github.com/0x0is1/lowy-index-api-docs
* https://power.lowyinstitute.org/countries.json

## endpoints
* POST: http://127.0.0.1:8000/users
* GET: http://127.0.0.1:8000/firstuser
* GET: http://127.0.0.1:8000/allusers
* GET: http://127.0.0.1:8000/users/1/countries
* GET: http://127.0.0.1:8000/countries

## test
* path => /src/
* $ pytest

