import os
import time
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, db_drop_and_create_all, remove_session, Actor, Movie, MovieCast

PRODUCER = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNYQUJxQlpUV2V4WXVUTXIydWlTQyJ9.eyJpc3MiOiJodHRwczovL21hbnVlbHJleWVzLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDkwMTQ4NzYxZGQ3NDAwNjkyYjBmYmQiLCJhdWQiOiJDYXBzdG9uZUZTTkRfQVBJIiwiaWF0IjoxNjIwNjc3MjE2LCJleHAiOjE2MjA3NjM2MTYsImF6cCI6IlFiRThFSU1GUGowb0U2QXNXT2pxMUcyaDdtVUpBMzRtIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOm1vdmllcyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwb3N0Om1vdmllcyJdfQ.NXURH0C8bggCK0z3tfCguLAoFWyfhi6FHCR_FNlo9g4Ol8qZGsszdqgGS_2NfynodtyLQErwdp_kOXpPlidJyBnp55kB3sxJ1kXZnndHasREqzi0JzQksFmT-fF-xV45S7aXYW8c6VNC8XXE-Vs16vcxghJ5XE1ic9lFS5cXV9MJIAf_VgVnT6I2yELjcGGBW6hkPfWTuzxnq0BQZzFhngaNWD3s9FcDFgH9aZiNvJpVtIwKCgAywWNKp3BZBEvAq7eT4p7YrA-F3Zj1pklUS2cb0TbcdKQ_2w8Pb85Jdc7VhnsIr1RWoKVbFiqkKnAg8aYumCtXM_KPH3JmuCQ_nQ')
DIRECTOR = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNYQUJxQlpUV2V4WXVUTXIydWlTQyJ9.eyJpc3MiOiJodHRwczovL21hbnVlbHJleWVzLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDkwMTQ2NmFkNzg0ZTAwNjkzY2FlNDMiLCJhdWQiOiJDYXBzdG9uZUZTTkRfQVBJIiwiaWF0IjoxNjIwNjc3MzA3LCJleHAiOjE2MjA3NjM3MDcsImF6cCI6IlFiRThFSU1GUGowb0U2QXNXT2pxMUcyaDdtVUpBMzRtIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjYXN0OmFjdG9ycyIsImRlbGV0ZTphY3RvcnMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIl19.nGZRBN9S3FUTaPhI1z0yBOQG5DbjoC316qyHAvM9NHiuum16uYrY68owAp_UIbt2TUkvJ27lq-TQccpLZdo7NhZyNjnfh0IIbcojbY1KhAwxm-ipzvcjAcHNvK-0px4kuxsKzNpFHGz2GHTb-jkuEumyPX5NEAMoZ13vHbqEocU2A4qcoVCIpjV_PyIj1GE0dyPLRvwhy9-UdfE-hleD_kkaYrNJXWblc8bMlbpFRO9HluQ0tLnqM9PIdJVC0CShet8-Az50pIxLiIgilxcDWA7yTG4yhIQoKLzg5jrFI2bxEAQGHzzjbti9T7ZyMczvpan7CEsWskOPP_F-M21gOA')
ASSISTANT = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNYQUJxQlpUV2V4WXVUTXIydWlTQyJ9.eyJpc3MiOiJodHRwczovL21hbnVlbHJleWVzLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDkwMTJiYmJmM2FkMDAwNzBjZDRhY2IiLCJhdWQiOiJDYXBzdG9uZUZTTkRfQVBJIiwiaWF0IjoxNjIwNjc3MzU1LCJleHAiOjE2MjA3NjM3NTUsImF6cCI6IlFiRThFSU1GUGowb0U2QXNXT2pxMUcyaDdtVUpBMzRtIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyJdfQ.S-ThD2QuMIi4Y4YX4-obpus6HjL5_roIbed88aaRm3OkfUC_cw7YIiuLoPrNWwCC7hdyKxXXc_xslbB11fEaua3_6tgds3-UdX9WEmwOpZ7X_BCpeH_ke47eCkX0fXcMdHW-cWH1ba4W-tSQvD6sWMVhyif-NMg7wvAagSfNoQod3C2JQmlhICPN2fcJ3FNe5eufC56vJgdHXJ86WQWSmTNEz2k7GbYy9FcP10AAOo15pMZ9D7UQX96tPWkjZgqvd5r6tmKVohebH5PtmPc1aKWjSggXHGiYv4RaYbC3-UHFQs4tMLqfCsmBYDJ2D0qND3-s5VoKCLoyLSZiN0GaUw')


class CapstoneTestCase(unittest.TestCase):

    assistantHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'Authorization': f'Bearer {ASSISTANT}'
    }

    directorHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'Authorization': f'Bearer {DIRECTOR}'
    }

    producerHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'Authorization': f'Bearer {PRODUCER}'
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    testActor = {
        "name": "Test Actor",
        "age": 35,
        "gender": "M"
    }

    modifiedActor = {
        "name": "Test Actor 2",
        "age": 35,
        "gender": "M"
    }

    testMovie = {
        "title": "Test Title",
        "release_date": "2017-05-11"
    }

    modifiedMovie = {
        "title": "Test Title 2",
        "release_date": "2017-05-11"
    }

    castingTest = {
        "movie_id": 1,
        "actor_id": 1,
    }

    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['DATABASE_URL']
        
        with self.app.app_context():
            setup_db(self.app, self.database_path)

    def setUp(self):
        db_drop_and_create_all()
            
    def tearDown(self):
        pass


    def test_create_actor_without_auth(self):
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")

    def test_create_actor_with_auth(self):
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"][0]["age"], self.testActor["age"])
        self.assertEqual(data["actor"][0]["gender"], self.testActor["gender"])
        self.assertEqual(data["actor"][0]["name"], self.testActor["name"])

    def test_create_movie_without_auth(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")


    def test_create_movie_with_auth(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"][0]["release_date"], "Thu, 11 May 2017 00:00:00 GMT")
        self.assertEqual(data["movie"][0]["title"], self.testMovie["title"])

    def test_get_movies_without_auth(self):
        response = self.client().get("/movies", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_actors_without_auth(self):
        response = self.client().get("/actors", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_movie_without_auth(self):
        response = self.client().get("/movies/1", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_actor_without_auth(self):
        response = self.client().get("/actors/1", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_movie_not_found(self):
        response = self.client().get("/movies/1", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_get_actor_not_found(self):
        response = self.client().get("/actors/1", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_get_movies(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)
        response = self.client().get("/movies", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movies"][0]["release_date"], "Thu, 11 May 2017 00:00:00 GMT")
        self.assertEqual(data["movies"][0]["title"], self.testMovie["title"])

        response = self.client().get("/movies/1", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"]["release_date"], "Thu, 11 May 2017 00:00:00 GMT")
        self.assertEqual(data["movie"]["title"], self.testMovie["title"])

    def test_get_actors(self):
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.directorHeaders)
        response = self.client().get("/actors", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actors"][0]["age"], self.testActor["age"])
        self.assertEqual(data["actors"][0]["gender"], self.testActor["gender"])
        self.assertEqual(data["actors"][0]["name"], self.testActor["name"])

        response = self.client().get("/actors/1", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"]["age"], self.testActor["age"])
        self.assertEqual(data["actor"]["gender"], self.testActor["gender"])
        self.assertEqual(data["actor"]["name"], self.testActor["name"])

    def test_patch_actor_without_auth(self):
        response = self.client().patch("/actors/1", data=json.dumps(self.modifiedActor), headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")

    def test_patch_movie_without_auth(self):
        response = self.client().patch("/movies/1", data=json.dumps(self.modifiedMovie), headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")

    def test_patch_actor_not_found(self):
        response = self.client().patch("/actors/2", data=json.dumps(self.modifiedActor), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
    
    def test_patch_movie_not_found(self):
        response = self.client().patch("/movies/2", data=json.dumps(self.modifiedMovie), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_patch_actor(self):
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.directorHeaders)
        response = self.client().patch("/actors/1", data=json.dumps(self.modifiedActor), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"]["age"], self.modifiedActor["age"])
        self.assertEqual(data["actor"]["gender"], self.modifiedActor["gender"])
        self.assertEqual(data["actor"]["name"], self.modifiedActor["name"])

    def test_patch_movie(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)
        response = self.client().patch("/movies/1", data=json.dumps(self.modifiedMovie), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie"]["title"], self.modifiedMovie["title"])

    def test_delete_actor_without_auth(self):
        response = self.client().delete("/actors/1", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")
    
    def test_delete_movie_without_auth(self):
        response = self.client().delete("/movies/1", headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")

    def test_delete_actor_not_found(self):
        response = self.client().delete("/actors/2", headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
    
    def test_delete_movie_not_found(self):
        response = self.client().delete("/movies/2", headers = self.producerHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_actor(self):
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.directorHeaders)
        response = self.client().get("/actors", headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["actors"][0]["age"], self.testActor["age"])
        self.assertEqual(data["actors"][0]["gender"], self.testActor["gender"])
        self.assertEqual(data["actors"][0]["name"], self.testActor["name"])

        response = self.client().delete("/actors/1", headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        response = self.client().get("/actors", headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["actors"]), 0)

    def test_delete_movie(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)
        response = self.client().get("/movies", headers = self.producerHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["movies"]), 1)

        response = self.client().delete("/movies/1", headers = self.producerHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        response = self.client().get("/movies", headers = self.producerHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["movies"]), 0)

    def test_cast_actor_without_auth(self):
        response = self.client().post("/cast", data=json.dumps(self.castingTest), headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["message"], "Permission not found.")

    def test_cast_actor_bad_request(self):
        invalidCastingTest = {
            "movie_id": 1,
        }

        response = self.client().post("/cast", data=json.dumps(invalidCastingTest), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "bad request")

    def test_cast_actor(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.producerHeaders)
        response = self.client().post("/cast", data=json.dumps(self.castingTest), headers = self.directorHeaders)

        data = json.loads(response.data.decode())
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["cast"][0]["actor_id"], 1)
        self.assertEqual(data["cast"][0]["movie_id"], 1)

    def test_get_movie_cast_no_auth(self):
        response = self.client().get("/movies/1/cast", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")


    def test_get_actor_movies_no_auth(self):
        response = self.client().get("/actors/1/movies", headers = self.headers)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_actor_movies_no_found(self):
        response = self.client().get("/actors/2/movies", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_get_movie_cast_no_found(self):
        response = self.client().get("/movies/2/cast", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")

    def test_get_actor_movie_cast(self):
        response = self.client().post("/movies", data=json.dumps(self.testMovie), headers = self.producerHeaders)
        response = self.client().post("/actors", data=json.dumps(self.testActor), headers = self.producerHeaders)
        response = self.client().post("/cast", data=json.dumps(self.castingTest), headers = self.directorHeaders)
        response = self.client().get("/actors/1/movies", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movies"][0]["title"], self.testMovie["title"] )

        response = self.client().get("/movies/1/cast", headers = self.assistantHeaders)

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["cast"][0]["name"], self.testActor["name"] )

if __name__ == "__main__":
    unittest.main()