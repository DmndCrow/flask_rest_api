from flask import Flask
from db_connection import script
from db_connection import blueprint


app = Flask(__name__)
app.register_blueprint(blueprint.api)


@app.route('/')
def hello():
    return 'Hello World! I have been seen {} times.\n'.format(1)


if __name__ == '__main__':
    script.upload_data()
    app.run(host="0.0.0.0", debug=True)
