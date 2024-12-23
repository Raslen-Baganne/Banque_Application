from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import bcrypt
from app import mydb, mycursor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Vérifier d'abord dans la table admins
    mycursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
    user = mycursor.fetchone()
    role = 'admin' if user else 'user'

    if not user:
        # Si pas trouvé dans admins, chercher dans users
        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = mycursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):  # Index 2 est le mot de passe haché
        access_token = create_access_token(identity={'username': username, 'role': role})
        return jsonify({
            'token': access_token,
            'role': role,
            'username': username
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Vérifier si l'utilisateur existe déjà
    mycursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    if mycursor.fetchone():
        return jsonify({'message': 'Username or email already exists'}), 400

    # Hacher le mot de passe
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Créer un nouvel utilisateur
    try:
        mycursor.execute(
            "INSERT INTO users (username, password, email, status) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, email, 'active')
        )
        mydb.commit()
        
        # Créer un token pour le nouvel utilisateur
        access_token = create_access_token(identity={'username': username, 'role': 'user'})
        return jsonify({
            'message': 'User created successfully',
            'token': access_token,
            'role': 'user',
            'username': username
        }), 201
    except Exception as e:
        mydb.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/user-profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user = get_jwt_identity()
    username = current_user.get('username')
    role = current_user.get('role')

    if role == 'admin':
        mycursor.execute("SELECT id, username, email, role FROM admins WHERE username = %s", (username,))
    else:
        mycursor.execute("SELECT id, username, email, status FROM users WHERE username = %s", (username,))

    user = mycursor.fetchone()
    if user:
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'role' if role == 'admin' else 'status': user[3]
        }
        return jsonify(user_data), 200
    
    return jsonify({'message': 'User not found'}), 404
