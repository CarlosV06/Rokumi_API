#THIS FILE WILL DEFINE SOME CONFIGS FOR THE APPLICATION#

import os

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    
class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    
class ProductionConfig(Config):
    debug = False