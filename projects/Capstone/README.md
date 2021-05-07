# Capstone Project: Casting Agency

Capstone project for [Udacity](https://www.udacity.com/) Full Stack Web Development Nanodegree.

The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies.

Site live at : [https://fsnd-capstone-manuelreyes.herokuapp.com/](https://fsnd-capstone-manuelreyes.herokuapp.com/)

There are three Roles:

    Casting Assistant
        Can view actors and movies
    Casting Director
        All permissions a Casting Assistant
        Add or delete an actor from the database
        Modify actors or movies
    Executive Producer
        All permissions a Casting Director
        Add or delete a movie from the database

## Getting Started

### Setup Virtual Environment

Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the Capstone directory and running:

```
pip3 install -r requirements.txt
```

This will install all of the required packages descriped in the `requirements.txt` file.

## API

### Endpoints

GET '/movies'
```
- Return all movies
- Request Arguments: None
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "movies": [
        {
            "id": 1,
            "release_date": "Thu, 11 May 2017 00:00:00 GMT",
            "title": "Test Title"
        }
    ],
    "success": true
}
```

GET '/movies/<int:id>'
```
- Return the movie based on the id
- Request Arguments: movie id
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "movie": {
        "id": 1,
        "release_date": "Thu, 11 May 2017 00:00:00 GMT",
        "title": "Test Title"
    },
    "success": true
}
```

POST '/movies'
```
- Add a new movie
- Request Arguments:

{
    "title": "Test Title",
    "release_date": "2017-05-11"
}

- Authorization : Executive Producer. 
- Returns on success:
{
    "movie": {
        "id": 1,
        "release_date": "Thu, 11 May 2017 00:00:00 GMT",
        "title": "Test Title"
    },
    "success": true
}
```

PATCH '/movies/<int:id>'
```
- Modified the movie that matches the input id
- Request Arguments:

{
    "title": "Test Title 2",
    "release_date": "2017-05-11"
}

- Authorization : Executive Producer. 
- Returns on success:
{
    "movie": {
        "id": 1,
        "release_date": "Thu, 11 May 2017 00:00:00 GMT",
        "title": "Test Title 2"
    },
    "success": true
}
```

DELETE '/movies/<int:id>'
```
- Delete the movie that matches the input id
- Request Arguments: movie id
- Authorization : Executive Producer. 
- Returns on success:
{
    "delete": 1,
    "success": true
}
```

GET '/movies/<int:id>/cast'
```
- Get the movie cast that matches the input id
- Request Arguments: movie id
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "cast": [
        {
            "age": 32,
            "gender": "M",
            "id": 1,
            "name": "test actor"
        }
    ],
    "success": true
}
```

GET '/actors'
```
- Return all actors
- Request Arguments: None
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "actors": [
        {
            "age": 32,
            "gender": "M",
            "id": 1,
            "name": "test actor"
        }
    ],
    "success": true
}
```

GET '/actors/<int:id>'
```
- Return the actor based on the id
- Request Arguments: actor id
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "actor": {
        "age": 32,
        "gender": "M",
        "id": 1,
        "name": "test actor"
    },
    "success": true
}
```

POST '/actors'
```
- Add a new actor
- Request Arguments:

{
    "name": "test actor",
    "age": 32,
    "gender": "M"
}

- Authorization : Casting Director, Executive Producer. 
- Returns on success:
{
    "actor": [
        {
            "age": 32,
            "gender": "M",
            "id": 1,
            "name": "test actor"
        }
    ],
    "success": true
}
```

PATCH '/actors/<int:id>'
```
- Modified the actor that matches the input id
- Request Arguments:

{
    "name": "Test Name 2",
    "age": 35,
    "gender": "M"
}

- Authorization : Casting Director, Executive Producer. 
- Returns on success:
{
    "actor": {
        "age": 35,
        "gender": "M",
        "id": 1,
        "name": "Test Name 2"
    },
    "success": true
}
```

DELETE '/actors/<int:id>'
```
- Delete the actor that matches the input id
- Request Arguments: actor id
- Authorization : Casting Director, Executive Producer. 
- Returns on success:
{
    "delete": 1,
    "success": true
}
```

GET '/actors/<int:id>/movies'
```
- Get the actor movies that matches the input id
- Request Arguments: actor id
- Authorization : Casting Assistant, Casting Director, Executive Producer. 
- Returns on success:
{
    "movies": [
        {
            "id": 1,
            "release_date": "Thu, 11 May 2017 00:00:00 GMT",
            "title": "Test Title"
        }
    ],
    "success": true
}
```

POST '/cast'
```
- Cast an existing actor to an existing movie
- Request Arguments:

{
    "movie_id": 2,
    "actor_id": 1
}

- Authorization : Casting Director, Executive Producer. 
- Returns on success:
{
    "cast": [
        {
            "actor_id": 1,
            "id": 1,
            "movie_id": 2
        }
    ],
    "success": true
}
```