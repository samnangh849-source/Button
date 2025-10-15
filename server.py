from flask import Flask, request, render_template

# Initialize the Flask application
app = Flask(__name__)

@app.route("/print")
def print_label():
    """
    Renders the label page with data from URL query parameters.
    Example URL: /print?name=Sok%20Dara&phone=092345678&total=25.00&payment=COD%20(Unpaid)
    """
    # Get data from the URL query string with fallback to empty strings
    data = {
        "name": request.args.get("name", "N/A"),
        "phone": request.args.get("phone", "N/A"),
        "total": request.args.get("total", "0.00"),
        "payment": request.args.get("payment", "N/A")
    }
    # Render the HTML template, passing the data to it
    return render_template("label.html", **data)

if __name__ == "__main__":
    # Run the app on localhost, port 5000
    # The debug=True flag provides helpful error messages during development
    app.run(port=5000, debug=True)
