from flask import Flask, jsonify, request
from database_handler import getFOLSentences, getFOLSentenceById, createDatabase, DatabaseConnection, getRandomSentences
from nltk.sem import Expression
from nltk.inference import Prover9
import time
import threading
import logging
app = Flask(__name__)

logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] in %(module)s: %(message)s'
)


def initialize_database():
    db = DatabaseConnection()
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'sentence'
        )
    """)

    exists = cur.fetchone()[0]

    if not exists:
        print("Initializing database...")
        try:
            createDatabase()
        except Exception as e:
            print(f"Failed to initialize database: {e}")
    else:
        print("Database already initialized.")

    cur.close()
    conn.close()
    db.disconnect()


@app.route('/api/sentences', methods=['GET'])
def fetchAllSentences():
    try:
        sentences = getFOLSentences()
        return jsonify(sentences), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch sentences", "details": str(e)}), 500


@app.route('/api/sentences/<int:sentence_id>', methods=['GET'])
def fetchSentenceById(sentence_id):
    try:
        sentence = getFOLSentenceById(sentence_id)
        if not sentence:
            return jsonify({"error": "Sentence not found"}), 404
        return jsonify(sentence), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch sentence", "details": str(e)}), 500


class DatabaseConnectionError:
    pass


import traceback

@app.route('/api/random-sentences', methods=['GET'])
def fetchRandomSentences():
    try:
        sentences = getRandomSentences()

        return jsonify(sentences), 200
    except Exception as e:
        error_details = traceback.format_exc()
        app.logger.error("Error fetching random sentences: %s", error_details)
        return jsonify({
            "error": "Failed to fetch random sentences",
            "details": str(e),
            "trace": error_details
        }), 500



def check_equivalence(student_answer, model_answer, timeout=5):
    prover = Prover9()
    student_expr = Expression.fromstring(student_answer)
    model_expr = Expression.fromstring(model_answer)

    def prove_with_timeout():
        return prover.prove(student_expr, [model_expr])

    prove_thread = threading.Thread(target=prove_with_timeout)
    prove_thread.start()
    prove_thread.join(timeout)

    if prove_thread.is_alive():
        return "Time limit exceeded", None

    result = "Equivalent" if prove_with_timeout() else "Not equivalent"
    proof = prover.proof() if hasattr(prover, 'proof') else None

    return result, proof


def calculate_score(feedback):
    difficulty_weights = {
        'low': 1,
        'medium': 2,
        'high': 3
    }
    total_score = 0
    max_score = 0

    for item in feedback:
        difficulty = item['difficulty']
        weight = difficulty_weights.get(difficulty, 0)
        max_score += weight
        if item['result'] == 'Equivalent':
            total_score += weight

    normalized_score = (total_score / max_score) * 10 if max_score > 0 else 0
    return round(normalized_score, 2)

@app.route('/api/submit-answers', methods=['POST'])
def submitAnswers():
    try:
        answers = request.json
        if not answers or not isinstance(answers, list):
            return jsonify({"error": "Invalid data format"}), 400

        feedback = []
        for answer in answers:
            if not answer.get('answer'):
                feedback.append({
                    "id": answer['id'],
                    "student_answer": answer['answer'],
                    "model_answer": None,
                    "result": "Invalid input",
                    "proof": None,
                    "difficulty": "low"
                })
                continue

            model_answer_data = getFOLSentenceById(answer['id'])
            model_answer = model_answer_data['fol_sentence']
            difficulty = model_answer_data['difficulty']
            result, proof = check_equivalence(answer['answer'], model_answer)
            feedback.append({
                "id": answer['id'],
                "student_answer": answer['answer'],
                "model_answer": model_answer,
                "result": result,
                "proof": str(proof) if proof else None,
                "difficulty": difficulty
            })

        score = calculate_score(feedback)
        return jsonify({"message": "Answers received successfully!", "feedback": feedback, "score": score}), 200
    except Exception as e:
        return jsonify({"error": "Failed to process answers", "details": str(e)}), 500


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
