from flask import Flask, request, Response
from data.db import initialize_db
from data.models import Valve, ValveTime

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://192.168.178.100:27017/letrain'
}

initialize_db(app)

@app.route("/")
def index():
    return "<h1>Hello!</h1>"

@app.route('/valves')
def get_valves():
    valves = Valve.objects().to_json()
    return Response(valves, mimetype="application/json", status=200)

@app.route('/valves', methods=['POST'])
def add_valve():
    body =request.get_json()
    valve = Valve(**body).save()
    id = valve.id
    return {'id': str(id)}, 200

@app.route('/valves/<id>', methods=['PUT'])
def update_valve(id):
    body = request.get_json()
    Valve.objects.get(id=id).update(**body)
    return '', 200

@app.route('/valve/<id>', methods=['DELETE'])
def delete_valve(id):
    Valve.objects.get(id=id).delete()
    return '', 200

@app.route('/valves/<id>')
def get_valve(id):
    valves = Valve.objects.get(id=id).to_json()
    return Response(valves, mimetype="application/json", status=200)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    
#app.run()




