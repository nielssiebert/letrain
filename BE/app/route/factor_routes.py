from flask import Blueprint, request, jsonify
from ..model.factor import Factor
from .. import db
from ..auth import auth

factor_bp = Blueprint('factor_bp', __name__)

@factor_bp.route('/factors', methods=['GET'])
@auth.login_required
def get_factors():
    factors = Factor.query.all()
    return jsonify([factor.to_dict() for factor in factors])

@factor_bp.route('/factors', methods=['POST'])
@auth.login_required
def create_factor():
    data = request.get_json()
    new_factor = Factor(**data)
    db.session.add(new_factor)
    db.session.commit()
    return jsonify(new_factor.to_dict()), 201

@factor_bp.route('/factors/<id>', methods=['GET'])
@auth.login_required
def get_factor(id):
    factor = Factor.query.get_or_404(id)
    return jsonify(factor.to_dict())

@factor_bp.route('/factors/<id>', methods=['PUT'])
@auth.login_required
def update_factor(id):
    factor = Factor.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(factor, key, value)
    db.session.commit()
    return jsonify(factor.to_dict())

@factor_bp.route('/factors/<id>', methods=['DELETE'])
@auth.login_required
def delete_factor(id):
    factor = Factor.query.get_or_404(id)
    db.session.delete(factor)
    db.session.commit()
    return '', 204