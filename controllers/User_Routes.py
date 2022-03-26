# THIS FILE WILL CONTAIN ALL ROUTES RELATED TO USER #

from flask import request, jsonify, Blueprint
from models.User_Model import UserModel
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from cloudinary import api, uploader

userRoutes = Blueprint('userRoutes', __name__)

# SIGN UP #
@userRoutes.route('/user/signUp', methods = ['POST'])
def user_signUp():
    
    # GETTING USER'S INFO #
    data = request.json
    firstName = data['firstName']
    lastName = data['lastName']
    email = data['email']
    password = UserModel.Encrypt(data['password']) 
    
    # USER ALREADY EXISTS #
    existingUser = UserModel.objects(email = email).first()
    if existingUser:
        
        return jsonify(message = "The user already exists. Use another email or sign in.", status = "409"), 409
    
    else:
    # CREATING A NEW USER #

        newUser = UserModel(fist_name = firstName, last_name = lastName, email = email, password = password).save()
        
        # ACCESS TOKEN FOR THE REGISTERED USER #
        access_token = create_access_token(identity = newUser.email)
    
        return jsonify(
            message = "User created successfully.",
            status = "201",
            access_token = access_token,
            firstName = newUser.first_name,
            lastName = newUser.last_name,
            email = newUser.email,
            photo = newUser.photo,
            role = newUser.role
        ), 201


# SIGN IN #
@userRoutes.route('/user/signIn', methods = ['POST'])
def user_signIn():
    
    return ""