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

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if scientist: 
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response(
               {"error": "Scientist not found"},
               404
            )
    
api.add_resource(ScientistById, '/scientists/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
