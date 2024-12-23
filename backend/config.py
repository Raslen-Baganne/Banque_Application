import os

class Config:
    SECRET_KEY = 'votre_clé_secrète_très_sécurisée'  # À changer en production
    JWT_SECRET_KEY = 'jwt_secret_key_très_sécurisée'  # À changer en production
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 heure
    CORS_HEADERS = 'Content-Type'
