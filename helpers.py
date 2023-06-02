from flask_pymongo import PyMongo
import bcrypt
import plotly.graph_objs as go
import plotly

mongo = PyMongo()


def get_hashed_password(password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)    
    # converting password to array of bytes
    bytes = password.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    # Hashing the password
    return bcrypt.hashpw(bytes, salt)


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
      # Taking user entered password 
    
    # checking password
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)