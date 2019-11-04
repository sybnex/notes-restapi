from flask import Flask
from flask_restful import Api, Resource, reqparse

import sys
import logging
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")

class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '5000' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)

app = Flask(__name__)
api = Api(app)

notes = [
    {
        "name": "light",
        "data": False
    },
    {
        "name": "test",
        "data": 78
    }
]

class Note(Resource):
    def get(self, name):
        for note in notes:
            if(name == note["name"]):
                return note, 200
        return "Note not found", 404

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                return "Note with name {} already exists".format(name), 400

        note = {
            "name": name,
            "data": args["data"]
        }
        notes.append(note)
        return note, 201

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                note["data"] = args["data"]
                return note, 200
        
        note = {
            "name": name,
            "data": args["data"]
        }
        notes.append(note)
        return note, 201

    def delete(self, name):
        global notes
        notes = [note for note in notes if note["name"] != name]
        return "{} is deleted.".format(name), 200
      
api.add_resource(Note, "/note/<string:name>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)

