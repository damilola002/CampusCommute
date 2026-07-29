from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)


# Fake driver starting location
driver_location = {
    "lat": 32.7298,
    "lng": -97.1163
}


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# API that gives the frontend driver coordinates
@app.route("/driver_location")
def get_driver_location():

    # Simulate driver moving
    driver_location["lat"] += random.uniform(-0.0005, 0.0005)
    driver_location["lng"] += random.uniform(-0.0005, 0.0005)

    return jsonify(driver_location)



if __name__ == "__main__":
    app.run(debug=True)