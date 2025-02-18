from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from os import getenv
from dotenv import load_dotenv
from typing import List, Dict, Optional
from http import HTTPStatus

load_dotenv()

app = Flask(__name__)
CORS(app, origins=getenv("ORIGINS", "http://localhost:3000").split(","))


class QuizQuestion:
    def __init__(
        self,
        id: int,
        question: str,
        options: List[Dict],
        category: str,
        difficulty: str,
    ):
        self.id = id
        self.question = question
        self.options = options
        self.category = category
        self.difficulty = difficulty

    def to_dict(self, hide_correct: bool = False) -> Dict:
        question_dict = {
            "id": self.id,
            "question": self.question,
            "options": (
                self.options
                if not hide_correct
                else [
                    {k: v for k, v in opt.items() if k != "correct"}
                    for opt in self.options
                ]
            ),
        }
        return question_dict


# Enhanced Q&A database with data validation
qa_database = [
    QuizQuestion(
        id=1,
        question="What is the capital of France?",
        options=[
            {"id": "a", "text": "London", "correct": False},
            {"id": "b", "text": "Paris", "correct": True},
            {"id": "c", "text": "Berlin", "correct": False},
            {"id": "d", "text": "Madrid", "correct": False},
        ],
        category="geography",
        difficulty="easy",
    ),
    QuizQuestion(
        id=2,
        question="Who wrote 'Romeo and Juliet'?",
        options=[
            {"id": "a", "text": "Charles Dickens", "correct": False},
            {"id": "b", "text": "Jane Austen", "correct": False},
            {"id": "c", "text": "William Shakespeare", "correct": True},
            {"id": "d", "text": "Mark Twain", "correct": False},
        ],
        category="literature",
        difficulty="easy",
    ),
    QuizQuestion(
        id=3,
        question="What is the chemical symbol for gold?",
        options=[
            {"id": "a", "text": "Ag", "correct": False},
            {"id": "b", "text": "Fe", "correct": False},
            {"id": "c", "text": "Ge", "correct": False},
            {"id": "d", "text": "Au", "correct": True},
        ],
        category="science",
        difficulty="medium",
    ),
    QuizQuestion(
        id=4,
        question="What is the largest planet in our solar system?",
        options=[
            {"id": "a", "text": "Jupiter", "correct": True},
            {"id": "b", "text": "Saturn", "correct": False},
            {"id": "c", "text": "Neptune", "correct": False},
            {"id": "d", "text": "Mars", "correct": False},
        ],
        category="science",
        difficulty="easy",
    ),
    QuizQuestion(
        id=5,
        question="What is the square root of 144?",
        options=[
            {"id": "a", "text": "14", "correct": False},
            {"id": "b", "text": "12", "correct": True},
            {"id": "c", "text": "10", "correct": False},
            {"id": "d", "text": "16", "correct": False},
        ],
        category="mathematics",
        difficulty="medium",
    ),
]


def filter_questions(
    questions: List[QuizQuestion],
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> List[QuizQuestion]:
    """Filter questions based on category and difficulty."""
    filtered = questions
    if category:
        filtered = [q for q in filtered if q.category.lower() == category.lower()]
    if difficulty:
        filtered = [q for q in filtered if q.difficulty.lower() == difficulty.lower()]
    return filtered


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """Get up to 5 random questions with optional filtering."""

    if not qa_database:
        return (
            jsonify({"error": "No questions found matching criteria"}),
            HTTPStatus.NOT_FOUND,
        )

    selected_questions = random.sample(
        qa_database, min(5, len(qa_database))
    )

    return jsonify([q.to_dict(False) for q in selected_questions])


# @app.route("/api/random", methods=["GET"])
# def get_random_question():
#     """Get a random question with optional filtering."""
#     category = request.args.get("category")
#     difficulty = request.args.get("difficulty")
#     hide_correct = request.args.get("hide_correct", "false").lower() == "true"

#     filtered_questions = filter_questions(qa_database, category, difficulty)

#     if not filtered_questions:
#         return jsonify({"error": "No questions found matching criteria"}), HTTPStatus.NOT_FOUND

#     question = random.choice(filtered_questions)
#     return jsonify(question.to_dict(hide_correct))


@app.route("/api/check/<int:question_id>", methods=["POST"])
def check_answer(question_id: int):
    """Check if the provided answer is correct and return detailed response."""
    question = next((q for q in qa_database if q.id == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), HTTPStatus.NOT_FOUND

    try:
        data = request.get_json()
        if not data or "selectedAnswer" not in data:
            return jsonify({"error": "Answer not provided"}), HTTPStatus.BAD_REQUEST

        selected_answer_id = data["selectedAnswer"]
        selected_answer_text = next(
            (
                opt["text"]
                for opt in question.options
                if opt["id"] == selected_answer_id
            ),
            None,
        )
        correct_option = next(opt for opt in question.options if opt["correct"])
        correct_answer_text = correct_option["text"]
        correct_answer_id = correct_option["id"]

        if selected_answer_text is None:
            return (
                jsonify({"error": "Invalid answer selection"}),
                HTTPStatus.BAD_REQUEST,
            )

        return jsonify(
            {
                "question": question.question,
                "selectedAnswer": selected_answer_text,
                "currentAnswer": correct_answer_text,
                "isCurrentAnswer": selected_answer_id == correct_answer_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(debug=getenv("FLASK_DEBUG", "true").lower() == "true", port=getenv("FLASK_PORT", "5000"))
