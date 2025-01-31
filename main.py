from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)  # Obsługa CORS

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    try:
        input_str = data.get("input", "").strip()
        if not input_str:
            return jsonify({"error": "Brak wyrażenia"}), 400

        operation = input_str[0]
        function_str = input_str[1:]

        function = sp.sympify(function_str)
        symbols = list(function.free_symbols)
        if not symbols:
            return jsonify({"error": "Nie znaleziono zmiennej w funkcji"}), 400

        variable = symbols[0]

        if operation == "c":  # Całka
            result = sp.integrate(function, variable)
        elif operation == "p":  # Pochodna
            result = sp.diff(function, variable)
        elif operation == "g":  # Granica
            point = data.get("point", None)
            if point is None:
                return jsonify({"error": "Brak punktu granicy"}), 400
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
        elif operation == "e":  # Ekstrema lokalne
            first_derivative = sp.diff(function, variable)
            critical_points = sp.solve(first_derivative, variable)

            extrema = []
            for point in critical_points:
                second_derivative = sp.diff(first_derivative, variable)
                second_derivative_value = second_derivative.subs(variable, point)

                if second_derivative_value.is_real:
                    if second_derivative_value > 0:
                        extrema.append({"x": str(point), "type": "minimum"})
                    elif second_derivative_value < 0:
                        extrema.append({"x": str(point), "type": "maksimum"})
                    else:
                        extrema.append({"x": str(point), "type": "punkt siodłowy"})

            return jsonify({"extrema": extrema})

        elif operation == "w":  # Wypukłość i wklęsłość
            second_derivative = sp.diff(sp.diff(function, variable))
            inflection_points = sp.solve(second_derivative, variable)

            concave_intervals = []
            convex_intervals = []

            if inflection_points:
                sorted_points = sorted([p for p in inflection_points if p.is_real])
                prev = -sp.oo  # Start od -∞

                for point in sorted_points:
                    test_value = second_derivative.subs(variable, (prev + point) / 2)
                    if test_value > 0:
                        convex_intervals.append(f"({prev}, {point})")
                    else:
                        concave_intervals.append(f"({prev}, {point})")
                    prev = point

                test_value = second_derivative.subs(variable, prev + 1)
                if test_value > 0:
                    convex_intervals.append(f"({prev}, ∞)")
                else:
                    concave_intervals.append(f"({prev}, ∞)")

            return jsonify({
                "convex": convex_intervals,
                "concave": concave_intervals,
                "inflection_points": [str(p) for p in inflection_points if p.is_real]
            })

        else:
            return jsonify({"error": "Nieznana operacja"}), 400

        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": f"Błąd obliczeń: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
