from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5000"])
# Enhanced Q&A database with multiple choice answers
qa_database = [
    {
        "id": 1,
        "question": "What is the capital of France?",
        "options": [
            {"id": "a", "text": "London", "correct": False},
            {"id": "b", "text": "Paris", "correct": True},
            {"id": "c", "text": "Berlin", "correct": False},
            {"id": "d", "text": "Madrid", "correct": False}
        ],
        "category": "geography",
        "difficulty": "easy"
    },
    {
        "id": 2,
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": [
            {"id": "a", "text": "Charles Dickens", "correct": False},
            {"id": "b", "text": "Jane Austen", "correct": False},
            {"id": "c", "text": "William Shakespeare", "correct": True},
            {"id": "d", "text": "Mark Twain", "correct": False}
        ],
        "category": "literature",
        "difficulty": "easy"
    },
    {
        "id": 3,
        "question": "What is the chemical symbol for gold?",
        "options": [
            {"id": "a", "text": "Ag", "correct": False},
            {"id": "b", "text": "Fe", "correct": False},
            {"id": "c", "text": "Ge", "correct": False},
            {"id": "d", "text": "Au", "correct": True}
        ],
        "category": "science",
        "difficulty": "medium"
    },
    {
        "id": 4,
        "question": "What is the largest planet in our solar system?",
        "options": [
            {"id": "a", "text": "Jupiter", "correct": True},
            {"id": "b", "text": "Saturn", "correct": False},
            {"id": "c", "text": "Neptune", "correct": False},
            {"id": "d", "text": "Mars", "correct": False}
        ],
        "category": "science",
        "difficulty": "easy"
    },
    {
        "id": 5,
        "question": "What is the square root of 144?",
        "options": [
            {"id": "a", "text": "14", "correct": False},
            {"id": "b", "text": "12", "correct": True},
            {"id": "c", "text": "10", "correct": False},
            {"id": "d", "text": "16", "correct": False}
        ],
        "category": "mathematics",
        "difficulty": "medium"
    }
]

@app.route('/api/questions', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    hide_correct = request.args.get('hide_correct', 'false').lower() == 'true'
    
    filtered_questions = qa_database
    
    if category:
        filtered_questions = [q for q in filtered_questions if q['category'] == category]
    if difficulty:
        filtered_questions = [q for q in filtered_questions if q['difficulty'] == difficulty]
    
    if hide_correct:
        filtered_questions = remove_correct_answers(filtered_questions)
    
    return jsonify(filtered_questions)

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    hide_correct = request.args.get('hide_correct', 'false').lower() == 'true'
    question = next((q for q in qa_database if q['id'] == question_id), None)
    
    if question:
        if hide_correct:
            question = remove_correct_answers([question])[0]
        return jsonify(question)
    return jsonify({"error": "Question not found"}), 404

@app.route('/api/random', methods=['GET'])
def get_random_question():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    hide_correct = request.args.get('hide_correct', 'false').lower() == 'true'
    
    filtered_questions = qa_database
    
    if category:
        filtered_questions = [q for q in filtered_questions if q['category'] == category]
    if difficulty:
        filtered_questions = [q for q in filtered_questions if q['difficulty'] == difficulty]
    
    if filtered_questions:
        question = random.choice(filtered_questions)
        if hide_correct:
            question = remove_correct_answers([question])[0]
        return jsonify(question)
    return jsonify({"error": "No questions found matching criteria"}), 404

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(set(q['category'] for q in qa_database))
    return jsonify(categories)

@app.route('/api/check/<int:question_id>', methods=['POST'])
def check_answer(question_id):
    question = next((q for q in qa_database if q['id'] == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    data = request.get_json()
    if not data or 'answer' not in data:
        return jsonify({"error": "Answer not provided"}), 400
    
    selected_answer = data['answer']
    correct_answer = next(opt['id'] for opt in question['options'] if opt['correct'])
    
    return jsonify({
        "correct": selected_answer == correct_answer,
        "correct_answer": correct_answer
    })

def remove_correct_answers(questions):
    """Remove 'correct' field from options to hide answers"""
    questions_copy = []
    for q in questions:
        q_copy = q.copy()
        q_copy['options'] = [{k: v for k, v in opt.items() if k != 'correct'} 
                           for opt in q['options']]
        questions_copy.append(q_copy)
    return questions_copy

if __name__ == '__main__':
    app.run(debug=True)