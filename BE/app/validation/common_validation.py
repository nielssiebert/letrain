from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_schema(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            schema = schema_class()
            try:
                validated_data = schema.load(data)
            except ValidationError as err:
                return jsonify(err.messages), 400
            return f(validated_data, *args, **kwargs)
        return decorated_function
    return decorator