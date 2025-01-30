from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)  # 🔴 Obsługa CORS

@app.route("/integrate", methods=["POST"])
def integrate():
    data = request.json
    try:
        # Automatycznie wykrywa zmienną w podanej funkcji
        symbols = list(sp.sympify(data["function"]).free_symbols)
        if not symbols:
            return jsonify({"error": "Brak zmiennej do całkowania"})
        
        variable = symbols[0]  # Pobiera pierwszą znalezioną zmienną
        result = sp.integrate(data["function"], variable)
        
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/compare", methods=["POST"])
def compare():
    data = request.json
    try:
        expr1 = sp.simplify(sp.sympify(data["result1"]))
        expr2 = sp.simplify(sp.sympify(data["result2"]))

        # Algebraiczne sprawdzenie równości
        algebraic_equality = sp.simplify(expr1 - expr2) == 0

        # Numeryczne sprawdzenie równości
        var = list(expr1.free_symbols)[0] if expr1.free_symbols else sp.Symbol("x")
        test_values = [-10, -5, -1, 0, 1, 5, 10]
        numerical_equality = all(abs(sp.N(expr1.subs(var, v)) - sp.N(expr2.subs(var, v))) < 1e-6 for v in test_values)

        # Ocena końcowa
        similarity_score = 1.0 if algebraic_equality else (0.7 if numerical_equality else 0.3)
        return jsonify({"similarity_score": similarity_score})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
