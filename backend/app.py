import pymysql
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'votre-cle-secrete'  # Changez ceci en production
jwt = JWTManager(app)

api = Api(app, title="Bank API", version="1.0", description="Bank API with Account and Transaction")

# Connexion à la base de données MySQL
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="14043176",
    database="banque_application"
)

mycursor = mydb.cursor()

account_model = api.model('Account', {
    'id': fields.Integer(readonly=True, description='The account unique identifier'),
    'name': fields.String(required=True, description='The account holder name'),
    'email': fields.String(required=True, description='The account holder email'),
    'phone': fields.String(required=True, description='The account holder phone number'),
    'cin': fields.String(required=True, description='The account holder CIN'),
    'balance': fields.Float(required=True, description='The account balance')
})

transaction_model = api.model('Transaction', {
    'sender_id': fields.Integer(required=True, description='The sender account ID'),
    'receiver_id': fields.Integer(required=True, description='The receiver account ID'),
    'amount': fields.Float(required=True, description='The amount to transfer')
})

admin_model = api.model('Admin', {
    'id': fields.Integer(readonly=True, description='The admin unique identifier'),
    'username': fields.String(required=True, description='Admin username'),
    'password': fields.String(required=True, description='Admin password'),
    'email': fields.String(required=True, description='Admin email'),
    'role': fields.String(required=True, description='Admin role')
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='User username'),
    'password': fields.String(required=True, description='User password'),
    'email': fields.String(required=True, description='User email'),
    'status': fields.String(required=True, description='User status')
})

# Route pour la gestion des comptes
@api.route('/accounts')
class AccountList(Resource):
    
    @api.doc('create_account')
    @api.expect(account_model)
    def post(self):
        """Add a new account"""
        data = request.json
        mycursor.execute("INSERT INTO accounts (name, email, phone, cin, balance) VALUES (%s, %s, %s, %s, %s)",
                         (data['name'], data['email'], data['phone'], data['cin'], data['balance']))
        mydb.commit()
        return {'message': 'Account created successfully'}, 201


@api.route('/accounts/<int:id>')
class Account(Resource):
    @api.doc('get_account')
    @api.marshal_with(account_model)
    def get(self, id):
        """Get an account by ID"""
        mycursor.execute("SELECT * FROM accounts WHERE id = %s", (id,))
        row = mycursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'cin': row[4],
                'balance': row[5]
            }
        else:
            return {'message': 'Account not found'}, 404

    @api.doc('update_account')
    @api.expect(account_model)
    def put(self, id):
        """Update an account by ID"""
        data = request.json
        mycursor.execute(""" 
            UPDATE accounts 
            SET name = %s, email = %s, phone = %s, cin = %s, balance = %s 
            WHERE id = %s
        """, (data['name'], data['email'], data['phone'], data['cin'], data['balance'], id))
        mydb.commit()
        
        if mycursor.rowcount == 0:
            return {'message': 'Account not found'}, 404
        
        return {'message': 'Account updated successfully'}, 200

    @api.doc('delete_account')
    def delete(self, id):
        """Delete an account by ID"""
        mycursor.execute("DELETE FROM accounts WHERE id = %s", (id,))
        mydb.commit()

        if mycursor.rowcount == 0:
            return {'message': 'Account not found'}, 404
        
        return {'message': 'Account deleted successfully'}, 200


# Route pour obtenir les comptes
@api.route('/api/user/accounts')
class UserAccounts(Resource):
    @jwt_required()
    def get(self):
        """Obtenir les comptes"""
        try:
            mycursor.execute("""
                SELECT id, name, email, phone, cin, balance 
                FROM accounts
            """)
            
            accounts = []
            for account in mycursor.fetchall():
                accounts.append({
                    'id': account[0],
                    'name': account[1],
                    'email': account[2],
                    'phone': account[3],
                    'cin': account[4],
                    'balance': float(account[5])
                })
            
            return accounts, 200
            
        except Exception as e:
            return {'message': f'Erreur lors de la récupération des comptes: {str(e)}'}, 500

# Route pour obtenir les transactions
@api.route('/api/user/transactions')
class UserTransactions(Resource):
    @jwt_required()
    def get(self):
        """Obtenir les transactions"""
        try:
            mycursor.execute("""
                SELECT t.id, 
                       s.name as sender_name, 
                       r.name as receiver_name,
                       t.amount, 
                       t.transaction_date
                FROM transactions t
                JOIN accounts s ON t.sender_id = s.id
                JOIN accounts r ON t.receiver_id = r.id
                ORDER BY t.transaction_date DESC
            """)
            
            transactions = []
            for transaction in mycursor.fetchall():
                transactions.append({
                    'id': transaction[0],
                    'sender_name': transaction[1],
                    'receiver_name': transaction[2],
                    'amount': float(transaction[3]),
                    'date': transaction[4].strftime('%Y-%m-%d %H:%M:%S') if transaction[4] else None
                })
            
            return transactions, 200
            
        except Exception as e:
            return {'message': f'Erreur lors de la récupération des transactions: {str(e)}'}, 500


# Route pour la gestion des transactions
@api.route('/transactions')
class TransactionList(Resource):
   
    @api.doc('create_transaction')
    @api.expect(transaction_model)
    def post(self):
        """Create a new transaction and update balances"""
        data = request.json
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        amount = data['amount']

        # Vérifier si les comptes ont suffisamment de fonds pour la transaction
        mycursor.execute("SELECT balance FROM accounts WHERE id = %s", (sender_id,))
        sender_balance = mycursor.fetchone()

        if not sender_balance:
            return {'message': 'Sender account not found'}, 404
        
        if sender_balance[0] < amount:
            return {'message': 'Insufficient funds'}, 400

        # Insérer la transaction
        mycursor.execute(""" 
            INSERT INTO transactions (sender_id, receiver_id, amount) 
            VALUES (%s, %s, %s)
        """, (sender_id, receiver_id, amount))
        mydb.commit()

        # Mettre à jour les soldes des deux comptes
        mycursor.execute(""" 
            UPDATE accounts 
            SET balance = balance - %s 
            WHERE id = %s
        """, (amount, sender_id))
        mydb.commit()

        mycursor.execute(""" 
            UPDATE accounts 
            SET balance = balance + %s 
            WHERE id = %s
        """, (amount, receiver_id))
        mydb.commit()

        return {'message': 'Transaction created and balances updated successfully'}, 201


# Route pour obtenir les transactions d'un utilisateur
@api.route('/user/transactions')
class UserTransactions(Resource):
    @jwt_required()
    def get(self):
        """Obtenir les transactions de l'utilisateur connecté"""
        try:
            current_user = get_jwt_identity()
            user_id = current_user['user_id']

            mycursor.execute("""
                SELECT t.id, t.amount, t.transaction_type, t.created_at,
                       sa.account_number as sender_account,
                       ra.account_number as receiver_account
                FROM transactions t
                LEFT JOIN accounts sa ON t.sender_account_id = sa.id
                LEFT JOIN accounts ra ON t.receiver_account_id = ra.id
                WHERE sa.user_id = %s OR ra.user_id = %s
                ORDER BY t.created_at DESC
                LIMIT 10
            """, (user_id, user_id))
            
            transactions = []
            for transaction in mycursor.fetchall():
                transactions.append({
                    'id': transaction[0],
                    'amount': float(transaction[1]),
                    'transaction_type': transaction[2],
                    'created_at': transaction[3].strftime('%Y-%m-%d %H:%M:%S') if transaction[3] else None,
                    'sender_account': transaction[4],
                    'receiver_account': transaction[5]
                })
            
            return transactions, 200
            
        except Exception as e:
            return {'message': f'Erreur lors de la récupération des transactions: {str(e)}'}, 500


@api.route('/transactions/<int:id>')
class Transaction(Resource):
    @api.doc('get_transaction')
    @api.marshal_with(transaction_model)
    def get(self, id):
        """Get a transaction by ID"""
        mycursor.execute("SELECT * FROM transactions WHERE id = %s", (id,))
        row = mycursor.fetchone()
        if row:
            return {
                'sender_id': row[1],
                'receiver_id': row[2],
                'amount': row[3]
            }
        else:
            return {'message': 'Transaction not found'}, 404

    @api.doc('update_transaction')
    @api.expect(transaction_model)
    def put(self, id):
        """Update a transaction by ID"""
        data = request.json
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        amount = data['amount']

        mycursor.execute(""" 
            UPDATE transactions
            SET sender_id = %s, receiver_id = %s, amount = %s
            WHERE id = %s
        """, (sender_id, receiver_id, amount, id))
        mydb.commit()

        if mycursor.rowcount == 0:
            return {'message': 'Transaction not found'}, 404

        return {'message': 'Transaction updated successfully'}, 200

    @api.doc('delete_transaction')
    def delete(self, id):
        """Delete a transaction by ID"""
        mycursor.execute("DELETE FROM transactions WHERE id = %s", (id,))
        mydb.commit()

        if mycursor.rowcount == 0:
            return {'message': 'Transaction not found'}, 404

        return {'message': 'Transaction deleted successfully'}, 200


# Routes pour la gestion des admins
@api.route('/admins')
class AdminList(Resource):
    @api.doc('create_admin')
    @api.expect(admin_model)
    def post(self):
        """Add a new admin"""
        data = request.json
        # Hachage du mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        mycursor.execute("INSERT INTO admins (username, password, email, role) VALUES (%s, %s, %s, %s)",
                        (data['username'], hashed_password, data['email'], data['role']))
        mydb.commit()
        return {'message': 'Admin created successfully'}, 201

    @api.doc('get_all_admins')
    @api.marshal_list_with(admin_model)
    def get(self):
        """Get all admins"""
        mycursor.execute("SELECT * FROM admins")
        rows = mycursor.fetchall()
        admins = []
        for row in rows:
            admins.append({
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'role': row[4]
            })
        return admins

@api.route('/admins/<int:id>')
class Admin(Resource):
    @api.doc('get_admin')
    @api.marshal_with(admin_model)
    def get(self, id):
        """Get an admin by ID"""
        mycursor.execute("SELECT * FROM admins WHERE id = %s", (id,))
        row = mycursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'role': row[4]
            }
        return {'message': 'Admin not found'}, 404

    @api.doc('update_admin')
    @api.expect(admin_model)
    def put(self, id):
        """Update an admin by ID"""
        data = request.json
        # Hachage du nouveau mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        mycursor.execute("""
            UPDATE admins 
            SET username = %s, password = %s, email = %s, role = %s 
            WHERE id = %s
        """, (data['username'], hashed_password, data['email'], data['role'], id))
        mydb.commit()
        if mycursor.rowcount == 0:
            return {'message': 'Admin not found'}, 404
        return {'message': 'Admin updated successfully'}, 200

    @api.doc('delete_admin')
    def delete(self, id):
        """Delete an admin by ID"""
        mycursor.execute("DELETE FROM admins WHERE id = %s", (id,))
        mydb.commit()
        if mycursor.rowcount == 0:
            return {'message': 'Admin not found'}, 404
        return {'message': 'Admin deleted successfully'}, 200


# Routes pour la gestion des users
@api.route('/users')
class UserList(Resource):
    @api.doc('create_user')
    @api.expect(user_model)
    def post(self):
        """Add a new user"""
        data = request.json
        # Hachage du mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        mycursor.execute("INSERT INTO users (username, password, email, status) VALUES (%s, %s, %s, %s)",
                        (data['username'], hashed_password, data['email'], data['status']))
        mydb.commit()
        return {'message': 'User created successfully'}, 201

    @api.doc('get_all_users')
    @api.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        mycursor.execute("SELECT * FROM users")
        rows = mycursor.fetchall()
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'status': row[4]
            })
        return users

@api.route('/users/<int:id>')
class User(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, id):
        """Get a user by ID"""
        mycursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        row = mycursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'status': row[4]
            }
        return {'message': 'User not found'}, 404

    @api.doc('update_user')
    @api.expect(user_model)
    def put(self, id):
        """Update a user by ID"""
        data = request.json
        # Hachage du nouveau mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        mycursor.execute("""
            UPDATE users 
            SET username = %s, password = %s, email = %s, status = %s 
            WHERE id = %s
        """, (data['username'], hashed_password, data['email'], data['status'], id))
        mydb.commit()
        if mycursor.rowcount == 0:
            return {'message': 'User not found'}, 404
        return {'message': 'User updated successfully'}, 200

    @api.doc('delete_user')
    def delete(self, id):
        """Delete a user by ID"""
        mycursor.execute("DELETE FROM users WHERE id = %s", (id,))
        mydb.commit()
        if mycursor.rowcount == 0:
            return {'message': 'User not found'}, 404
        return {'message': 'User deleted successfully'}, 200


# Route pour l'inscription des utilisateurs
@api.route('/register')
class UserRegistration(Resource):
    @api.doc('register_user')
    @api.expect(user_model)
    def post(self):
        """Inscrire un nouvel utilisateur"""
        try:
            data = request.json
            
            # Vérifier si l'utilisateur existe déjà
            mycursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", 
                           (data['username'], data['email']))
            if mycursor.fetchone():
                return {'message': "L'utilisateur ou l'email existe déjà"}, 400

            # Hacher le mot de passe
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Insérer le nouvel utilisateur
            mycursor.execute("""
                INSERT INTO users (username, password, email, status) 
                VALUES (%s, %s, %s, 'active')
            """, (data['username'], hashed_password, data['email']))
            mydb.commit()
            
            return {'message': 'Utilisateur créé avec succès'}, 201
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de l\'inscription: {str(e)}'}, 500


# Route pour la connexion
@api.route('/login')
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Vérifier d'abord dans la table admins
            mycursor.execute("SELECT id, username, password, role FROM admins WHERE username = %s", (username,))
            user = mycursor.fetchone()
            is_admin = True

            # Si pas trouvé dans admins, chercher dans users
            if not user:
                mycursor.execute("SELECT id, username, password, 'user' as role FROM users WHERE username = %s", (username,))
                user = mycursor.fetchone()
                is_admin = False

            if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                # Créer le token JWT
                access_token = create_access_token(identity=user[1])
                return {
                    'token': access_token,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'role': user[3]
                    }
                }, 200
            else:
                return {'message': 'Nom d\'utilisateur ou mot de passe incorrect'}, 401

        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            return {'message': 'Erreur lors de la connexion'}, 500


# Route pour créer un nouveau compte
@api.route('/api/accounts')
class AccountCreate(Resource):
    @jwt_required()
    def post(self):
        """Créer un nouveau compte"""
        try:
            data = request.get_json()
            
            # Vérifier si l'email existe déjà
            mycursor.execute("SELECT id FROM accounts WHERE email = %s", (data['email'],))
            if mycursor.fetchone():
                return {'message': 'Un compte avec cet email existe déjà'}, 400
                
            # Vérifier si le CIN existe déjà
            mycursor.execute("SELECT id FROM accounts WHERE cin = %s", (data['cin'],))
            if mycursor.fetchone():
                return {'message': 'Un compte avec ce CIN existe déjà'}, 400
            
            # Insérer le nouveau compte
            mycursor.execute("""
                INSERT INTO accounts (name, email, phone, cin, balance)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['name'], data['email'], data['phone'], data['cin'], data['balance']))
            
            mydb.commit()
            return {'message': 'Compte créé avec succès'}, 201
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la création du compte: {str(e)}'}, 500

# Route pour effectuer une transaction
@api.route('/api/transactions')
class TransactionCreate(Resource):
    @jwt_required()
    def post(self):
        """Effectuer une nouvelle transaction"""
        try:
            data = request.get_json()
            sender_id = data['sender_id']
            receiver_id = data['receiver_id']
            amount = float(data['amount'])
            
            # Vérifier si les comptes existent
            mycursor.execute("SELECT balance FROM accounts WHERE id = %s", (sender_id,))
            sender = mycursor.fetchone()
            if not sender:
                return {'message': 'Compte expéditeur non trouvé'}, 404
                
            mycursor.execute("SELECT balance FROM accounts WHERE id = %s", (receiver_id,))
            receiver = mycursor.fetchone()
            if not receiver:
                return {'message': 'Compte destinataire non trouvé'}, 404
            
            # Vérifier si le solde est suffisant
            sender_balance = float(sender[0])
            if sender_balance < amount:
                return {'message': 'Solde insuffisant'}, 400
            
            # Mettre à jour les soldes
            mycursor.execute("""
                UPDATE accounts SET balance = balance - %s WHERE id = %s
            """, (amount, sender_id))
            
            mycursor.execute("""
                UPDATE accounts SET balance = balance + %s WHERE id = %s
            """, (amount, receiver_id))
            
            # Enregistrer la transaction
            mycursor.execute("""
                INSERT INTO transactions (sender_id, receiver_id, amount, transaction_date)
                VALUES (%s, %s, %s, NOW())
            """, (sender_id, receiver_id, amount))
            
            mydb.commit()
            return {'message': 'Transaction effectuée avec succès'}, 201
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la transaction: {str(e)}'}, 500


# Route pour supprimer et modifier un compte
@api.route('/api/accounts/<int:account_id>')
class AccountActions(Resource):
    @jwt_required()
    def delete(self, account_id):
        """Supprimer un compte"""
        try:
            # Vérifier si le compte existe
            mycursor.execute("SELECT id FROM accounts WHERE id = %s", (account_id,))
            if not mycursor.fetchone():
                return {'message': 'Compte non trouvé'}, 404
            
            # Supprimer d'abord les transactions liées à ce compte
            mycursor.execute("""
                DELETE FROM transactions 
                WHERE sender_id = %s OR receiver_id = %s
            """, (account_id, account_id))
            
            # Supprimer le compte
            mycursor.execute("DELETE FROM accounts WHERE id = %s", (account_id,))
            mydb.commit()
            
            return {'message': 'Compte et transactions associées supprimés avec succès'}, 200
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la suppression du compte: {str(e)}'}, 500

    @jwt_required()
    def put(self, account_id):
        """Modifier un compte"""
        try:
            data = request.get_json()
            
            # Vérifier si le compte existe
            mycursor.execute("SELECT id FROM accounts WHERE id = %s", (account_id,))
            if not mycursor.fetchone():
                return {'message': 'Compte non trouvé'}, 404
            
            # Vérifier si l'email existe déjà pour un autre compte
            mycursor.execute("SELECT id FROM accounts WHERE email = %s AND id != %s", 
                           (data['email'], account_id))
            if mycursor.fetchone():
                return {'message': 'Un autre compte utilise déjà cet email'}, 400
            
            # Vérifier si le CIN existe déjà pour un autre compte
            mycursor.execute("SELECT id FROM accounts WHERE cin = %s AND id != %s", 
                           (data['cin'], account_id))
            if mycursor.fetchone():
                return {'message': 'Un autre compte utilise déjà ce CIN'}, 400
            
            # Mettre à jour le compte
            mycursor.execute("""
                UPDATE accounts 
                SET name = %s, email = %s, phone = %s, cin = %s, balance = %s
                WHERE id = %s
            """, (data['name'], data['email'], data['phone'], data['cin'], 
                  data['balance'], account_id))
            
            mydb.commit()
            return {'message': 'Compte mis à jour avec succès'}, 200
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la mise à jour du compte: {str(e)}'}, 500

# Route pour supprimer une transaction
@api.route('/api/transactions/<int:transaction_id>')
class TransactionActions(Resource):
    @jwt_required()
    def delete(self, transaction_id):
        """Supprimer une transaction"""
        try:
            # Vérifier si la transaction existe
            mycursor.execute("""
                SELECT sender_id, receiver_id, amount 
                FROM transactions 
                WHERE id = %s
            """, (transaction_id,))
            transaction = mycursor.fetchone()
            
            if not transaction:
                return {'message': 'Transaction non trouvée'}, 404
            
            # Annuler la transaction en remboursant les comptes
            sender_id, receiver_id, amount = transaction
            
            # Rembourser l'expéditeur
            mycursor.execute("""
                UPDATE accounts 
                SET balance = balance + %s 
                WHERE id = %s
            """, (amount, sender_id))
            
            # Débiter le destinataire
            mycursor.execute("""
                UPDATE accounts 
                SET balance = balance - %s 
                WHERE id = %s
            """, (amount, receiver_id))
            
            # Supprimer la transaction
            mycursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
            
            mydb.commit()
            return {'message': 'Transaction supprimée et remboursée avec succès'}, 200
            
        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la suppression de la transaction: {str(e)}'}, 500


# Routes pour la gestion des utilisateurs (admin)
@api.route('/api/admin/users')
class AdminUsers(Resource):
    @jwt_required()
    def get(self):
        """Récupérer tous les utilisateurs"""
        try:
            # Vérifier si l'utilisateur est admin
            current_user = get_jwt_identity()
            mycursor.execute("SELECT role FROM admins WHERE username = %s", (current_user,))
            admin = mycursor.fetchone()
            if not admin or admin[0] != 'admin':
                return {'message': 'Accès non autorisé'}, 403

            # Récupérer tous les utilisateurs
            mycursor.execute("""
                SELECT id, username, email, status, created_at 
                FROM users
                ORDER BY created_at DESC
            """)
            users = []
            for user in mycursor.fetchall():
                users.append({
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'status': user[3],
                    'created_at': user[4].isoformat() if user[4] else None
                })
            return users, 200
            
        except Exception as e:
            return {'message': f'Erreur lors de la récupération des utilisateurs: {str(e)}'}, 500

    @jwt_required()
    def post(self):
        """Créer un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur est admin
            current_user = get_jwt_identity()
            mycursor.execute("SELECT role FROM admins WHERE username = %s", (current_user,))
            admin = mycursor.fetchone()
            if not admin or admin[0] != 'admin':
                return {'message': 'Accès non autorisé'}, 403

            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            status = data.get('status', 'active')

            # Vérifier si l'utilisateur existe déjà
            mycursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                           (username, email))
            if mycursor.fetchone():
                return {'message': 'Nom d\'utilisateur ou email déjà utilisé'}, 400

            # Hasher le mot de passe
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Créer l'utilisateur
            mycursor.execute("""
                INSERT INTO users (username, password, email, status, created_at) 
                VALUES (%s, %s, %s, %s, NOW())
            """, (username, hashed_password, email, status))
            mydb.commit()

            return {'message': 'Utilisateur créé avec succès'}, 201

        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la création de l\'utilisateur: {str(e)}'}, 500

@api.route('/api/admin/users/<int:user_id>')
class AdminUserActions(Resource):
    @jwt_required()
    def put(self, user_id):
        """Modifier un utilisateur"""
        try:
            # Vérifier si l'utilisateur est admin
            current_user = get_jwt_identity()
            mycursor.execute("SELECT role FROM admins WHERE username = %s", (current_user,))
            admin = mycursor.fetchone()
            if not admin or admin[0] != 'admin':
                return {'message': 'Accès non autorisé'}, 403

            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            status = data.get('status')

            # Vérifier si l'utilisateur existe
            mycursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not mycursor.fetchone():
                return {'message': 'Utilisateur non trouvé'}, 404

            # Vérifier si le nom d'utilisateur ou l'email est déjà utilisé par un autre utilisateur
            mycursor.execute("""
                SELECT id FROM users 
                WHERE (username = %s OR email = %s) AND id != %s
            """, (username, email, user_id))
            if mycursor.fetchone():
                return {'message': 'Nom d\'utilisateur ou email déjà utilisé'}, 400

            # Mettre à jour l'utilisateur
            if password:  # Si un nouveau mot de passe est fourni
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                mycursor.execute("""
                    UPDATE users 
                    SET username = %s, email = %s, password = %s, status = %s
                    WHERE id = %s
                """, (username, email, hashed_password, status, user_id))
            else:  # Si pas de nouveau mot de passe
                mycursor.execute("""
                    UPDATE users 
                    SET username = %s, email = %s, status = %s
                    WHERE id = %s
                """, (username, email, status, user_id))

            mydb.commit()
            return {'message': 'Utilisateur mis à jour avec succès'}, 200

        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la mise à jour de l\'utilisateur: {str(e)}'}, 500

    @jwt_required()
    def delete(self, user_id):
        """Supprimer un utilisateur"""
        try:
            # Vérifier si l'utilisateur est admin
            current_user = get_jwt_identity()
            mycursor.execute("SELECT role FROM admins WHERE username = %s", (current_user,))
            admin = mycursor.fetchone()
            if not admin or admin[0] != 'admin':
                return {'message': 'Accès non autorisé'}, 403

            # Vérifier si l'utilisateur existe
            mycursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not mycursor.fetchone():
                return {'message': 'Utilisateur non trouvé'}, 404

            # Empêcher la suppression du dernier admin
            mycursor.execute("SELECT COUNT(*) FROM admins WHERE role = 'admin'")
            admin_count = mycursor.fetchone()[0]
            
            mycursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
            user_role = mycursor.fetchone()[0]
            
            if user_role == 'admin' and admin_count <= 1:
                return {'message': 'Impossible de supprimer le dernier administrateur'}, 400

            # Supprimer l'utilisateur
            mycursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            mydb.commit()

            return {'message': 'Utilisateur supprimé avec succès'}, 200

        except Exception as e:
            mydb.rollback()
            return {'message': f'Erreur lors de la suppression de l\'utilisateur: {str(e)}'}, 500


# Route temporaire pour réinitialiser le mot de passe admin
@app.route('/reset_admin', methods=['GET'])
def reset_admin():
    try:
        # Hasher le mot de passe 'password'
        password = 'password'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # D'abord, vérifions si l'admin existe
        mycursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        existing_admin = mycursor.fetchone()
        
        if existing_admin:
            # Mettre à jour l'admin existant
            mycursor.execute("""
                UPDATE admins 
                SET password = %s, email = %s, role = %s 
                WHERE username = %s
            """, (hashed_password, 'admin@mail.com', 'admin', 'admin'))
        else:
            # Créer un nouvel admin
            mycursor.execute("""
                INSERT INTO admins (username, password, email, role, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, ('admin', hashed_password, 'admin@mail.com', 'admin'))
        
        mydb.commit()
        
        # Vérifier que la mise à jour a bien fonctionné
        mycursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        admin = mycursor.fetchone()
        if admin:
            return f'Admin reset successfully. ID: {admin[0]}, Username: {admin[1]}, Email: {admin[3]}, Role: {admin[4]}'
        else:
            return 'Error: Admin not found after reset'
            
    except Exception as e:
        mydb.rollback()
        return f'Error: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)