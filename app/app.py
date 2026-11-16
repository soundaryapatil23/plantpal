"""PlantPal API - a small plant-watering reminder REST service used to demonstrate a DevOps pipeline."""
import os

from flask import Flask, jsonify, request

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


def create_app():
    app = Flask(__name__)
    plants = [
        {"id": 1, "name": "Tulsi", "water_every_days": 2, "days_since_watered": 3},
        {"id": 2, "name": "Aloe Vera", "water_every_days": 7, "days_since_watered": 1},
    ]

    def find(plant_id):
        return next((p for p in plants if p["id"] == plant_id), None)

    @app.get("/")
    def index():
        return jsonify(service="plantpal", version=APP_VERSION)

    @app.get("/health")
    def health():
        return jsonify(status="UP")

    @app.get("/plants")
    def list_plants():
        return jsonify(plants)

    @app.post("/plants")
    def add_plant():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        every = data.get("water_every_days")
        if not name or not isinstance(name, str):
            return jsonify(error="'name' is required"), 400
        if isinstance(every, bool) or not isinstance(every, int) or every <= 0:
            return jsonify(error="'water_every_days' must be a positive integer"), 400
        plant = {"id": len(plants) + 1, "name": name,
                 "water_every_days": every, "days_since_watered": 0}
        plants.append(plant)
        return jsonify(plant), 201

    @app.post("/plants/<int:plant_id>/water")
    def water_plant(plant_id):
        plant = find(plant_id)
        if plant is None:
            return jsonify(error="plant not found"), 404
        plant["days_since_watered"] = 0
        return jsonify(plant)

    @app.get("/plants/due")
    def due_plants():
        return jsonify([p for p in plants if p["days_since_watered"] >= p["water_every_days"]])

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
