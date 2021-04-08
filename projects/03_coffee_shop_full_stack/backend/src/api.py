import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({'success': True, 'drinks': [drink.short() for drink in drinks]}), 200

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    return jsonify({'success': True, 'drinks': [drink.long() for drink in drinks]}), 200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()

    try:
        drink = Drink(
            title=body['title'],
            recipe=json.dumps(body['recipe']),
        )
        drink.insert()
    except:
        abort(422)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.filter_by(id=id).first()

    if not drink:
        abort(404)

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        drink.insert()
    except:
        abort(422)

    return jsonify({'success': True,'drinks': [drink.long()]}), 200

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter_by(id=id).first()

    if not drink:
        abort(404)

    try:
        drink.delete()
    except:
        abort(422)

    return jsonify({'success': True, 'delete': id}), 200

'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

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