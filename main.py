from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)  # Obsługa CORS

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    try:
        input_str = data.get("input", "")
        if not input_str:
            return jsonify({"error": "Brak wyrażenia"}), 400

        # Rozpoznawanie operacji na podstawie pierwszego znaku
        operation = input_str[0]
        function_str = input_str[1:]

        # Obsługa granicy, format: g(expression, point)
        if operation == "g":
            if "," not in function_str:
                return jsonify({"error": "Brak punktu granicy"}), 400
            function_part, point_part = function_str.split(",", 1)
            function = sp.sympify(function_part)
            point = sp.sympify(point_part)
        else:
            function = sp.sympify(function_str)

        symbols = list(function.free_symbols)
        if not symbols:
            return jsonify({"error": "Nie znaleziono zmiennej w funkcji"}), 400

        variable = symbols[0]

        # Obsługa operacji
        if operation == "c":  # Całka
            result = sp.integrate(function, variable)
        elif operation == "p":  # Pochodna
            result = sp.diff(function, variable)
        elif operation == "g":  # Granica
            result = sp.limit(function, variable, point)
        elif operation == "a":  # Asymptoty
            vertical_asymptotes = sp.solve(sp.denom(function), variable)
            horizontal_asymptotes = [sp.limit(function, variable, sp.oo),
                                      sp.limit(function, variable, -sp.oo)]
            m = sp.limit(function / variable, variable, sp.oo)
            b = sp.limit(function - m * variable, variable, sp.oo)
            oblique_asymptote = f"y = {m}x + {b}" if m.is_real and m != 0 else None

            return jsonify({
                "vertical": [str(v) for v in vertical_asymptotes if v.is_real],
                "horizontal": [str(h) for h in horizontal_asymptotes if h.is_real],
                "oblique": oblique_asymptote
            })
        else:
            return jsonify({"error": "Nieznana operacja"}), 400

        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": f"Błąd obliczeń: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
