from flask import Blueprint, request, jsonify, session
from backend.models import db, User
from backend.utils.crypto import generate_salt, hash_master_password, derive_encryption_key
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import base64

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    salt = generate_salt()
    # Hash for authentication
    password_hash = hash_master_password(password, salt)

    new_user = User(username=username, password_hash=password_hash, salt=salt)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify password
    # Note: In production, use constant time comparison
    derived_hash = hash_master_password(password, user.salt)
    
    if derived_hash != user.password_hash:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Derive encryption key and store in session (base64 encoded for JSON serialization in session)
    encryption_key = derive_encryption_key(password, user.salt)
    session['encryption_key'] = base64.b64encode(encryption_key).decode('utf-8')

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('encryption_key', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict()), 200
