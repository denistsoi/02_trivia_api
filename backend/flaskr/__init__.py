import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    db = SQLAlchemy()

    CORS(app, resources={r"*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PATCH, DELETE, OPTIONS")
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route("/categories")
    @cross_origin()
    def get_categories():
        try:
            if request.method != "GET":
                abort(405)

            categories = Category.query.all()

            return jsonify({
                "status": True,
                "status_code": 200,
                "categories": [cat.type for cat in categories]
            })
        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route("/questions", methods=["GET"])
    @cross_origin()
    def get_questions():
        if request.method != "GET" and request.method != "POST":
            abort(405)

        try:
            page = request.args.get("page", 1, type=int)
            limit = request.args.get("limit", 10, type=int)
            offset = (page - 1) * limit
            questions = Question.query.offset(offset).limit(limit).all()

            if (len(questions) == 0):
                abort(404)

            return jsonify({
                "success": True,
                "status": 200,
                "total_questions": len(questions),
                "questions": [q.format() for q in questions],
                "current_category": None,
                "categories": [c.type for c in Category.query.all()]
            })
        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    @cross_origin()
    def delete_question(question_id):
        try:
            if request.method != "DELETE":
                abort(405)

            # delete_question = Question.query.delete()
            question = Question.query.get(question_id)
            if (question is None):
                abort(422)

            question.delete()

            return jsonify({
                "success": True,
                "message": f"Question was deleted: {question_id}"
            })

        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route("/questions", methods=["POST"])
    @cross_origin()
    def create_question_or_search_question():
        # TODO:
        # create question or search
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)

        search = body.get("search", None)

        try:
            if search:
                search_questions = Question.query.filter(
                    Question.question.ilike("%{}%".format(search))).all()

                return jsonify({
                    "success": True,
                    "status_code": 200,
                    "total_questions": len(search_questions),
                    "questions": [q.format() for q in search_questions]
                })
            else:

                try:
                    new_question = Question(
                        question=question,
                        answer=answer,
                        category=category,
                        difficulty=difficulty
                    )
                    new_question.insert()
                except:
                    db.session.rollback()
                    abort(422)

                finally:
                    db.session.close()

                return jsonify({
                    "success": True,
                    "status_code": 200
                })
        except:
            abort(422)
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    @cross_origin()
    def get_categories_questions(category_id):
        questions = Question.query.filter_by(
            category=str(category_id)).all()

        if (not questions or len(questions) == 0):
            abort(404)

        return jsonify({
            "success": True,
            "category_id": category_id,
            "total_questions": len(questions),
            "questions": [q.format() for q in questions]
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route("/play", methods=["POST"])
    @cross_origin()
    def play():
        try:
            body = request.get_json()
            category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            category_id = category.get("id", None)

            if (category_id):

                has_category = Category.query.filter_by(
                    id=str(category_id)).first()

                if (has_category is None):
                    abort(422)

                if (previous_questions):
                    filtered_questions = [q.format()
                                          for q in Question.query.filter(
                        Question.id.notin_(previous_questions),
                        Question.category == str(category_id)).all()
                    ]

                    next_question = random.choice(filtered_questions)

                    return jsonify({
                        "success": True,
                        "question": next_question
                    })

                else:
                    questions = [question.format()
                                 for question in Question.query.all()]

                    next_question = random.choice(questions)
                    return jsonify({
                        "success": True,
                        "question": next_question
                    })

            else:
                questions = [question.format()
                             for question in Question.query.all()]

                next_question = random.choice(questions)
                return jsonify({
                    "success": True,
                    "question": next_question
                }), 200

        except Exception as error:
            raise error
        finally:
            pass
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "message": "Not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def not_processable(e):
        return jsonify({
            "success": False,
            "message": "Not processable"
        }), 422

    return app
