from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)  # Obsługa CORS

@app.route("/integrate", methods=["POST"])
def integrate():
    data = request.json
    try:
        function_str = data.get("function", "")
        if not function_str:
            return jsonify({"error": "Brak funkcji do całkowania"}), 400

        # Zamiana stringa na wyrażenie SymPy
        function = sp.sympify(function_str)

        # Automatyczne wykrywanie zmiennej całkowania
        symbols = list(function.free_symbols)
        if not symbols:
            return jsonify({"error": "Nie znaleziono zmiennej do całkowania"}), 400

        variable = symbols[0]  # Pobiera pierwszą znalezioną zmienną

        # Sprawdzamy, czy mamy całkę oznaczoną
        if "limits" in data:
            limits = tuple(data["limits"])
            a, b = limits[1], limits[2]

            # Sprawdzamy, czy funkcja zmienia znak w przedziale
            roots = sp.solveset(function, variable, domain=sp.Interval(a, b))

            # Jeśli nie zmienia znaku, liczymy normalnie
            if not roots or roots.is_EmptySet:
                result = sp.integrate(function, (variable, a, b))
            else:
                # Jeśli zmienia znak, dzielimy całkę na podprzedziały
                roots = sorted([r.evalf() for r in roots if r.is_real] + [a, b])
                result = sum(abs(sp.integrate(function, (variable, roots[i], roots[i+1]))) for i in range(len(roots)-1))

        else:
            # Jeśli to całka nieoznaczona
            result = sp.integrate(function, variable)

        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": f"Błąd całkowania: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
