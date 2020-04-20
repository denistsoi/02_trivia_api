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

    @app.route("/categories")
    @cross_origin()
    def get_categories():
        try:
            if request.method != "GET":
                abort(405)

            categories = {}

            for category in Category.query.all():
                id = category.id
                categories[id] = category.type

            return jsonify({
                "success": True,
                "status_code": 200,
                "categories": categories
            })
        except:
            abort(422)

    @app.route("/questions", methods=["GET"])
    @cross_origin()
    def get_questions():
        if request.method != "GET" and request.method != "POST":
            abort(405)

        try:
            page = request.args.get("page", 1, type=int)
            offset = (page - 1) * 10
            total_questions = Question.query.count()
            questions = Question.query.offset(offset).limit(10).all()

            if (len(questions) == 0):
                abort(404)

            return jsonify({
                "success": True,
                "status": 200,
                "total_questions": total_questions,
                "questions": [q.format() for q in questions],
                "current_category": None,
                "categories": [c.type for c in Category.query.all()]
            })
        except:
            abort(422)

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

                if (has_category == None):
                    abort(422)

                if (previous_questions):
                    filtered_questions = [q.format()
                                          for q in Question.query.filter(
                        Question.id.notin_(previous_questions),
                        Question.category == str(category_id)).all()
                    ]

                    if (not filtered_questions):
                        abort(404)

                    next_question = random.choice(filtered_questions)

                    return jsonify({
                        "success": True,
                        "question": next_question
                    })

                else:
                    questions = [question.format()
                                 for question in Question.query.filter_by(category=str(category_id)).all()]

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
