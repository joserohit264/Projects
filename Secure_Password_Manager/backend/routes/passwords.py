from flask import Blueprint, request, jsonify, session
from backend.models import db, Password
from backend.utils.crypto import encrypt_password, decrypt_password
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64

passwords_bp = Blueprint('passwords', __name__)

def get_encryption_key():
    key_b64 = session.get('encryption_key')
    if not key_b64:
        return None
    return base64.b64decode(key_b64)

@passwords_bp.route('', methods=['GET'])
@jwt_required()
def get_passwords():
    user_id = get_jwt_identity()
    key = get_encryption_key()
    
    if not key:
        return jsonify({'error': 'Encryption key not found. Please login again.'}), 401

    passwords = Password.query.filter_by(user_id=user_id).all()
    results = []
    
    for p in passwords:
        try:
            decrypted_password = decrypt_password(p.encrypted_data, key)
            p_dict = p.to_dict()
            p_dict['password'] = decrypted_password
            results.append(p_dict)
        except Exception as e:
            # Handle decryption errors (e.g., if key is wrong, though it shouldn't be if logged in)
            p_dict = p.to_dict()
            p_dict['password'] = "Error decrypting"
            results.append(p_dict)

    return jsonify(results), 200

@passwords_bp.route('', methods=['POST'])
@jwt_required()
def add_password():
    user_id = get_jwt_identity()
    key = get_encryption_key()
    
    if not key:
        return jsonify({'error': 'Encryption key not found. Please login again.'}), 401

    data = request.get_json()
    website = data.get('website')
    username = data.get('username')
    password_plaintext = data.get('password')
    category = data.get('category', 'Uncategorized')
    favorite = data.get('favorite', False)

    if not website or not username or not password_plaintext:
        return jsonify({'error': 'Missing required fields'}), 400

    encrypted_data = encrypt_password(password_plaintext, key)

    new_password = Password(
        user_id=user_id,
        website=website,
        username=username,
        encrypted_data=encrypted_data,
        category=category,
        favorite=favorite
    )
    
    db.session.add(new_password)
    db.session.commit()

    return jsonify(new_password.to_dict()), 201

@passwords_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_password(id):
    user_id = get_jwt_identity()
    key = get_encryption_key()
    
    if not key:
        return jsonify({'error': 'Encryption key not found. Please login again.'}), 401

    password_entry = Password.query.filter_by(id=id, user_id=user_id).first()
    if not password_entry:
        return jsonify({'error': 'Password not found'}), 404

    data = request.get_json()
    
    if 'website' in data:
        password_entry.website = data['website']
    if 'username' in data:
        password_entry.username = data['username']
    if 'password' in data:
        password_entry.encrypted_data = encrypt_password(data['password'], key)
    if 'category' in data:
        password_entry.category = data['category']
    if 'favorite' in data:
        password_entry.favorite = data['favorite']

    db.session.commit()
    return jsonify(password_entry.to_dict()), 200

@passwords_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_password(id):
    user_id = get_jwt_identity()
    password_entry = Password.query.filter_by(id=id, user_id=user_id).first()
    
    if not password_entry:
        return jsonify({'error': 'Password not found'}), 404

    db.session.delete(password_entry)
    db.session.commit()
    return jsonify({'message': 'Password deleted'}), 200
