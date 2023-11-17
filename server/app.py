#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)

    def post(self):
        params = request.json
        try:
            scientist = Scientist(name=params['name'], field_of_study=params['field_of_study'])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)

        db.session.add(scientist)
        db.session.commit()
        response = make_response(
            scientist.to_dict(rules=('-missions',)),
            200
        )
        return response

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if scientist: 
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response(
               {"error": "Scientist not found"},
               400
            )

    def patch(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404) 
        
        params = request.json
        for attr in params:
            try:
                setattr(scientist, attr, params[attr])
            except ValueError as v_error:
                return make_response({"errors": [str(v_error)]}, 400)

        db.session.commit()
        response = make_response(
            scientist.to_dict(rules=('-missions',)),
            202
        )
        return response

    def delete(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)

        db.session.delete(scientist)
        db.session.commit()
        response = make_response(
            {},
            204
        )
        return response     
    
api.add_resource(ScientistById, '/scientists/<int:id>')

@app.route('/planets')
def get_planets():
    planets = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
    return make_response(planets, 200)

@app.route('/missions', methods=["POST"])
def post_mission():
    if request.method == "POST":
        params = request.json
        try:
            new_mission = Mission(name=params['name'], planet_id=params['planet_id'], scientist_id=params['scientist_id'])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)

        db.session.add(new_mission)
        db.session.commit()

        response = make_response(
            new_mission.to_dict(),
            201
        )
        return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
