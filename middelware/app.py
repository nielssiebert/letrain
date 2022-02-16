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
    response = Response(valves, mimetype="application/json", status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/valves', methods=['POST'])
def add_valve():
    body =request.get_json()
    valve = Valve(**body).save()
    id = valve.id
    response = Response({'id': str(id)}, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/valves/<id>', methods=['PUT'])
def update_valve(id):
    body = request.get_json()
    Valve.objects.get(id=id).update(**body)
    response = Response({'id': str(id)}, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/valve/<id>', methods=['DELETE'])
def delete_valve(id):
    Valve.objects.get(id=id).delete()
    response = Response({'id': str(id)}, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/valves/<id>')
def get_valve(id):
    valves = Valve.objects.get(id=id).to_json()
    response = Response(valves, mimetype="application/json", status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    
#app.run()




