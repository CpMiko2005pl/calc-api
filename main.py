from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)  # 🔴 Dodajemy obsługę CORS

@app.route("/integrate", methods=["POST"])
def integrate():
    data = request.json
    try:
        x = sp.Symbol('x')
        result = sp.integrate(data["function"], x)
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
