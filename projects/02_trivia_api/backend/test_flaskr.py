import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://manuel:1234@localhost:5432/{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.app.config["SQLALCHEMY_DATABASE_URI"] = self.database_path
            self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
            self.db.app = self.app
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    def test_get_questions(self):
        questionsCount = Question.query.count()
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], questionsCount)
        self.assertEqual(data['current_category'], None)

    def test_delete_question(self):
        testQuestion = Question(
            question="12345",
            answer="12345",
            difficulty=1,
            category=1,
        )
        testQuestion.insert()
        response = self.client().delete(f"/questions/{testQuestion.id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.query.get(testQuestion.id), None)

    def test_delete_question_422(self):
        response = self.client().delete("/questions/999")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_question(self):
        testQuestion = Question(
            question="12345",
            answer="12345",
            difficulty=1,
            category=1,
        )

        testQuestion.insert()
        
        response = self.client().post("/questions/search", data=json.dumps({"searchTerm": "12345"}), headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 1)
        self.assertTrue(data["questions"][0]['question'], "12345")
        self.assertTrue(data["questions"][0]['answer'], "12345")
        self.assertTrue(data["questions"][0]['difficulty'], 1)
        self.assertTrue(data["questions"][0]['category'], 1)
        
        testQuestion.delete()

    def test_create_question(self):
        testQuestion = {
            "question": "test question",
            "answer": "test answer",
            "difficulty": 1,
            "category": 1,
        }

        response = self.client().post("/questions", data=json.dumps(testQuestion), headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"]["question"], testQuestion["question"])
        self.assertEqual(data["question"]["answer"], testQuestion["answer"])
        self.assertEqual(data["question"]["difficulty"], testQuestion["difficulty"])
        self.assertEqual(data["question"]["category"], testQuestion["category"])

        response = self.client().post("/questions/search", data=json.dumps({"searchTerm": "test question"}), headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        data = json.loads(response.data.decode())
        id = data["questions"][0]['id']
        response = self.client().delete(f"/questions/{id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.query.get(id), None)

    def test_create_question_400(self):
        testQuestion = {
            "question": "test question",
            "answer": "test answer"
        }

        response = self.client().post("/questions", data=json.dumps(testQuestion), headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_get_question_from_category(self):
        response = self.client().get("categories/4/questions")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 4)
        self.assertEqual(data["current_category"], 'History')

    def test_get_quizzes(self):
        previous_questions = [question.id for question in Question.query.all()]
        
        testQuestion = Question(
            question="12345",
            answer="12345",
            difficulty=1,
            category=1,
        )

        testQuestion.insert()

        response = self.client().post("/quizzes", data=json.dumps({
                    "previous_questions": previous_questions,
                    "quiz_category": {"id": "1"},
                }), headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                })

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["question"]["question"], testQuestion.question)
        self.assertEqual(data["question"]["answer"], testQuestion.answer)
        self.assertEqual(data["question"]["difficulty"], testQuestion.difficulty)
        self.assertEqual(data["question"]["category"], testQuestion.category)

        testQuestion.delete()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()