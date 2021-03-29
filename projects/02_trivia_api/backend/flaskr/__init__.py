import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)  
  CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS')
    return response

  @app.route('/categories')
  def get_categories():
    return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in Category.query.all()}
    })

  @app.route('/questions')
  def get_questions():
    selection = Question.query.all()
    return jsonify({
        'success': True,
        'questions': paginate_questions(request, selection),
        'total_questions': len(selection),
        'categories': {category.id: category.type for category in Category.query.all()},
        'current_category': None
    })

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
        question = Question.query.filter_by(id=id).first()

        if not question:
          abort(404)

        question.delete()

        return '', 204

    except:
        abort(422)

  @app.route("/questions", methods=["POST"])
  def create_question():
      body = request.get_json()
      question = body.get("question")
      answer = body.get("answer")
      category = body.get("category")
      difficulty = body.get("difficulty")

      if not(question and answer and category and difficulty):
          abort(400)

      try:
          question = Question(
              question=question,
              answer=answer,
              category=category,
              difficulty=difficulty,
          )
          question.insert()
      except:
          abort(422)

      return jsonify({"success": True, "question": question.format()}), 200

  @app.route("/questions/search", methods=["POST"])
  def search_question():
    body = request.get_json()
    searchTerm = body.get("searchTerm")
    results = Question.query.filter(func.lower(Question.question).contains(searchTerm)).all()

    return (
      jsonify(
        {
          "success": True,
          "questions": paginate_questions(request, results),
          "total_questions": len(results),
          "current_category": None,
        }
      ),
      200,
    )

  @app.route('/categories/<int:id>/questions')
  def get_questions_from_category(id):
    category = Category.query.filter_by(id=id).first()
    selection = Question.query.filter_by(category=category.id).all()
    return jsonify({
        'success': True,
        'questions': paginate_questions(request, selection),
        'total_questions': len(selection),
        'current_category': category.type
    })

  @app.route("/quizzes", methods=["POST"])
  def get_quizzes():
    data = request.get_json()
    previous_questions = data.get("previous_questions")
    quiz_category = data.get("quiz_category")

    if (quiz_category['id'] == 0):
        questions = Question.query.all()
    else:
        questions = Question.query.filter_by(category=quiz_category['id']).all()

    if(len(previous_questions) == len(questions)):
      return jsonify({"success": True, }), 200
    
    question = random.choice(questions)
    while(question.id in previous_questions):
      question = random.choice(questions)

    return jsonify({"success": True, "question": question.format(), }), 200

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

  return app

    