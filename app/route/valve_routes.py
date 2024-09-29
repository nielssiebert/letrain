from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .. import db
from ..model.valve import Valve, ValveSchema
from ..validation.common_validation import validate_schema
from ..auth import auth

valve_bp = Blueprint('main', __name__)


@valve_bp.route('/valves', methods=['GET'])
@auth.login_required
def get_valves():
    valves = Valve.query.all()
    return jsonify([valve for valve in valves])

@valve_bp.route('/valves/<unique_name>', methods=['GET'])
@auth.login_required
def get_valve(unique_name):
    valve = Valve.query.get_or_404(unique_name)
    return jsonify(valve)

@valve_bp.route('/valves', methods=['POST'])
@auth.login_required
@validate_schema(ValveSchema)
def create_valve(validated_valve):
    new_valve = Valve(**validated_valve)
    db.session.add(new_valve)
    db.session.commit()
    return jsonify(new_valve), 201

@valve_bp.route('/valves/<unique_name>', methods=['PUT'])
@auth.login_required
def update_valve(unique_name):
    valve = Valve.query.get_or_404(unique_name)
    data = request.get_json()
    for key, value in data.items():
        setattr(valve, key, value)
    db.session.commit()
    return jsonify(valve)

@valve_bp.route('/valves/<unique_name>', methods=['DELETE'])
@auth.login_required
def delete_valve(unique_name):
    valve = Valve.query.get_or_404(unique_name)
    db.session.delete(valve)
    db.session.commit()
    return '', 204

@valve_bp.route('/valves/<unique_name>/switch_on', methods=['POST'])
@auth.login_required
def switch_valve_on(unique_name):
    valve = Valve.query.get_or_404(unique_name)
    # Implement switching on logic here
    return jsonify({'status': 'switched on'})

@valve_bp.route('/valves/<unique_name>/switch_off', methods=['POST'])
@auth.login_required
def switch_valve_off(unique_name):
    valve = Valve.query.get_or_404(unique_name)
    # Implement switching off logic here
    return jsonify({'status': 'switched off'})
