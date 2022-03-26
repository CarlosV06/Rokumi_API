# DEFINITION OF THE MODEL OF THE USER #

from email.policy import default
from app import DB
from werkzeug.security import generate_password_hash, check_password_hash

# USER

class UserModel(DB.Document):
    
    # ATTRIBUTES #
    
    first_name = DB.StringField(max_length = 60, required = True)
    last_name = DB.StringField(max_length = 60, required = True)
    email = DB.StringField(required = True, unique = True) 
    photo = DB.StringField(default = "")
    role = DB.StringField(default = "Normal User")
    password = DB.StringField(required = True)
    
    
    # ENCRYPT PASSWORD #
    
    def Encrypt(clave):
        return generate_password_hash(clave)
    
    # VERIFY PASSWORD #
    
    def Verify(clavebd, clave):
        return check_password_hash(clavebd, clave)
    
    