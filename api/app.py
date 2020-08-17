from flask import Flask, jsonify
from db_connection import script
from db_connection import blueprint


app = Flask(__name__)
app.register_blueprint(blueprint.api)


@app.route('/')
def hello():
    return 'Hello World! I have been seen {} times.\n'.format(1)


@app.route('/api/build')
def build():
    script.upload_data()
    return jsonify({'message': 'built successfully'}), 200


if __name__ == '__main__':
    print('call upload data from app.py main')
    script.upload_data()
    app.run(host="0.0.0.0", debug=True)
