from flask import Blueprint, request, jsonify
from .. import db
from ..model.trigger import Trigger
from ..auth import auth

trigger_bp = Blueprint('trigger_bp', __name__)

@trigger_bp.route('/triggers', methods=['GET'])
@auth.login_required
def get_triggers():
    triggers = Trigger.query.all()
    return jsonify([trigger for trigger in triggers])

@trigger_bp.route('/triggers', methods=['POST'])
@auth.login_required
def create_trigger():
    data = request.get_json()
    new_trigger = Trigger(**data)
    db.session.add(new_trigger)
    db.session.commit()
    return jsonify(new_trigger), 201

@trigger_bp.route('/triggers/<unique_name>', methods=['GET'])
@auth.login_required
def get_trigger(unique_name):
    trigger = Trigger.query.get_or_404(unique_name)
    return jsonify(trigger)

@trigger_bp.route('/triggers/<unique_name>', methods=['PUT'])
@auth.login_required
def update_trigger(unique_name):
    trigger = Trigger.query.get_or_404(unique_name)
    data = request.get_json()
    for key, value in data.items():
        setattr(trigger, key, value)
    db.session.commit()
    return jsonify(trigger)

@trigger_bp.route('/triggers/<unique_name>', methods=['DELETE'])
@auth.login_required
def delete_trigger(unique_name):
    trigger = Trigger.query.get_or_404(unique_name)
    db.session.delete(trigger)
    db.session.commit()
    return '', 204