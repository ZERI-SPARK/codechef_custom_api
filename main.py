from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS

from user_data import UserData, UsernameError, PlatformError, BrokenChangesError

app = Flask(__name__)
CORS(app)
api = Api(app)

class Details(Resource):
    def get(self, platform, username):
        user_data = UserData(username)
        try:
            return jsonify(user_data.get_details(platform))
        except UsernameError:
            return jsonify({'status': 'Failed', 'details': 'Invalid username'}), 400
        except PlatformError:
            return jsonify({'status': 'Failed', 'details': 'Invalid Platform'}), 400
        except BrokenChangesError:
            return jsonify({'status': 'Failed', 'details': 'API broken due to site changes'}), 500

api.add_resource(Details, '/api/<string:platform>/<string:username>')

@app.errorhandler(404)
def invalid_route(e):
    return jsonify({'status': 'Failed', 'details': 'Route not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
