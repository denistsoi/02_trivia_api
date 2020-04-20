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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            "question": "What is the animal for House HufflePuff",
            "answer": "Badger",
            "category": 7,
            "difficulty": 5
        }

        self.start_quiz = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }

        self.start_quiz_error = {
            "quiz_category": {
                "id": 9999
            },
            "previous_questions": []
        }
        self.start_quiz_no_category = {
            "quiz_category": {},
            "previous_questions": []
        }

        self.start_quiz_category_with_previous_questions = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": [20]
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 10)

    def test_get_questions_with_page(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        self.assertEqual(len(data["questions"]), 10)

    def test_error_get_questions_with_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not processable")

    def test_create_question(self):
        response = self.client().post(
            "/questions",
            json=self.new_question
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"], True)

    def test_search_question(self):
        response = self.client().post("/questions", json={"search": "title"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 2)

    def test_search_no_results(self):
        response = self.client().post(
            "/questions", json={"search": "nope nope"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_delete_question(self):
        # find harry potter test question

        question = Question.query.filter_by(
            answer="Badger").first()

        response = self.client().delete(f"/questions/{question.id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_if_questions_does_not_exist(self):
        response = self.client().delete("/questions/1000")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_categories_with_questions(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_404_categories_with_questions(self):
        response = self.client().get("/categories/1000/questions")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_play(self):
        response = self.client().post("/play", json=self.start_quiz)
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_error(self):
        response = self.client().post("/play", json=self.start_quiz_error)
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_play_no_category(self):
        response = self.client().post("/play", json=self.start_quiz_no_category)
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_category_with_previous_questions(self):
        response = self.client().post(
            "/play", json=self.start_quiz_category_with_previous_questions)
        data = json.loads(response.data)

        self.assertTrue(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])


if __name__ == "__main__":
    unittest.main()
