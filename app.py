#THIS FILE WILL DEFINE THE APPLICATION#

from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from config import *
import cloudinary

#BASIC APP CONFIGURATION#

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
load_dotenv()

# ENABLING CORS #
cors = CORS(app, supports_credentials = True)

# JWT #

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours = 2)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days = 25)
JWT = JWTManager(app)

# MONGOENGINE #

app.config['MONGODB_SETTINGS'] = {'host':os.getenv('URI_BBDD'), 'db':'Pelitacos_BD'}
DB = MongoEngine(app)

# CLOUDINARY #

cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
    api_secret=os.getenv('API_SECRET'))

# BLUEPRINTS FOR SEGMENTING CONTROLLERS #
from controllers.User_Routes import userRoutes
from controllers.Serie_Routes import serieRoutes

app.register_blueprint(userRoutes)
app.register_blueprint(serieRoutes)