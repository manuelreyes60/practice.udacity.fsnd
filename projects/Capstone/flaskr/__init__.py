import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from models import setup_db, db_drop_and_create_all, Movie, Actor, MovieCast
from auth.auth import AuthError, requires_auth

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    db_drop_and_create_all()

    @app.route('/')
    def get_greeting():
        return "Welcome to the Casting Agency"

    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies(payload):
        return jsonify({
            'success': True,
            'movies': [movie.info() for movie in Movie.query.all()]
        }), 200

    @app.route('/movies/<int:id>')
    @requires_auth('get:movies')
    def get_movie(payload, id):
        movie = Movie.query.get(id)

        if movie is None:
            abort(404)

        return jsonify({'success': True, 'movie': movie.info() }), 200

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movie(payload):
        body = request.get_json()
        title = body.get("title")
        release_date = body.get("release_date")

        if not(title and release_date):
          abort(400)

        try:
            movie = Movie(
                title=title,
                release_date=release_date,
            )
            movie.insert()
        except:
            abort(422)

        return jsonify({'success': True, 'movie': [movie.info()]}), 200

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def edit_movie(payload, id):
        body = request.get_json()
        title = body.get("title")
        release_date = body.get("release_date")

        movie = Movie.query.get(id)

        if movie is None:
            abort(404)

        if title is None or release_date is None:
            abort(400)

        movie.title = title
        movie.release_date = release_date

        try:
            movie.update()  
        except:
            abort(422)

        return jsonify({ 'success': True, 'movie': movie.info() }), 200

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, id):
        movie = Movie.query.get(id)
        
        if movie is None:
            abort(404)

        try:
            movie.delete()
        except:
            abort(422)

        return jsonify({'success': True, 'delete': id}), 200

    @app.route('/movies/<int:id>/cast')
    @requires_auth('get:movies')
    def get_cast_movies(payload, id):
        movie = Movie.query.get(id)

        if movie is None:
            abort(404)

        allCasts = MovieCast.query.filter_by(movie_id=movie.id).join(Actor).all()
        actors = [Actor.query.get(cast.actor_id) for cast in allCasts]

        return jsonify({'success': True, 'cast': [actor.info() for actor in actors] }), 200

    @app.route('/actors')
    @requires_auth('get:actors')
    def get_actors(payload):
        return jsonify({
            'success': True,
            'actors': [actor.info() for actor in Actor.query.all()]
        }), 200

    @app.route('/actors/<int:id>')
    @requires_auth('get:actors')
    def get_actor(payload, id):
        actor = Actor.query.get(id)

        if actor is None:
            abort(404)

        return jsonify({'success': True, 'actor': actor.info() }), 200

    @app.route('/actors/<int:id>/movies')
    @requires_auth('get:actors')
    def get_actor_movies(payload, id):
        actor = Actor.query.get(id)

        if actor is None:
            abort(404)

        allCasts = MovieCast.query.filter_by(actor_id=actor.id).join(Movie).all()
        movies = [Movie.query.get(cast.movie_id) for cast in allCasts]

        return jsonify({'success': True, 'movies': [movie.info() for movie in movies] }), 200

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actor(payload):
        body = request.get_json()
        name = body.get("name")
        age = body.get("age")
        gender = body.get("gender")

        if not(name and age and gender):
          abort(400)

        try:
            actor = Actor(
                name = body['name'],
                age = body['age'],
                gender = body['gender'],
            )
            actor.insert()
        except:
            abort(422)

        return jsonify({'success': True, 'actor': [actor.info()]}), 200

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def edit_actor(payload, id):
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')

        actor = Actor.query.get(id)

        if actor is None:
            abort(404)

        if name is None or age is None or gender is None:
            abort(400)

        actor.name = name
        actor.age = age
        actor.gender = gender

        try:
            actor.update()  
        except:
            abort(422)

        return jsonify({ 'success': True, 'actor': actor.info() }), 200

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, id):
        actor = Actor.query.get(id)
        
        if actor is None:
            abort(404)

        try:
            actor.delete()
        except:
            abort(422)

        return jsonify({'success': True, 'delete': id}), 200

    @app.route('/cast', methods=['POST'])
    @requires_auth('cast:actors')
    def add_cast(payload):
        body = request.get_json()
        movie_id = body.get("movie_id")
        actor_id = body.get("actor_id")

        if not(movie_id and actor_id):
          abort(400)

        try:
            movieCast = MovieCast(
                movie_id = movie_id,
                actor_id = actor_id,
            )
            movieCast.insert()
        except:
            abort(422)

        return jsonify({'success': True, 'cast': [movieCast.info()]}), 200

    @app.errorhandler(AuthError)
    def handle_exception(err):
        return jsonify({
            "success": False,
            "error": err.status_code,
            "message": err.error['description']
        }), err.status_code

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app