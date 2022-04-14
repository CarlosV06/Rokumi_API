# THIS FILE WILL CONTAIN ALL ROUTES RELATED TO USER #

from flask import request, jsonify, Blueprint
from models.Tracking_Model import TrackingModel
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
        
        return jsonify(message = "The user already exists. Use another email or sign in.", status = 409), 409
    
    else:
    # CREATING A NEW USER #
        newUser = UserModel(first_name = firstName, last_name = lastName, email = email, password = password).save()
        
        # ACCESS TOKEN FOR THE REGISTERED USER #
        access_token = create_access_token(identity = str(newUser.id))
    
        return jsonify(
            message = "User created successfully.",
            status = 201,
            idUser = str(newUser.id),
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
    
    # GETTING USER'S INFO #
    
    data = request.json
    email = data['email']
    password = data['password']
    
    user = UserModel.objects(email = email).first()
    
    if user is not None and UserModel.Verify(user.password, password):
        # ACCESS TOKEN FOR THE AUTHENTICATED USER #
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify(
            message = "Process completed successfully.",
            access_token = access_token,
            status = 200,
            email = user.email,
            photo = user.photo,
            role = user.role,
            idUser = str(user.id),
            firstName = user.first_name,
            lastName = user.last_name
        ), 200
        
    else:
        # USER DOES NOT EXIST OR WRONG INFO GIVEN #
        return jsonify(message = "Wrong credentials or the user does not exist.", status = 409), 409
    

# USER'S PROFILE #
@userRoutes.route('/user', methods = ['GET'])
@jwt_required()
def get_userProfile():
    # GETTING BASIC USER'S INFORMATION #
    user_session = UserModel.objects(id = get_jwt_identity()).first()
      
    user = {
        'idUser': str(user_session.id),
        'firstName': user_session.first_name,
        'lastName': user_session.last_name,
        'email': user_session.email,
        'photo': user_session.photo,
        'role': user_session.role
    }
      
    
    return jsonify(
        message = "User's information received successfully.",
        status = 200,
        userInformation = user
    ), 200    
  
    
# USER'S TRACKING LIST #
@userRoutes.route('/user/trackingList', methods = ['GET'])
@jwt_required()
def get_trackingList():
    # TRACKING LIST OF THE USER #
    tracking_list = []
    ownerUser = False
    for tracking in TrackingModel.objects(user = get_jwt_identity()).all():
        
        uploaded_by = str(tracking.serie.posted_by.id)
        
        if uploaded_by == get_jwt_identity():
            ownerUser = True
        
        tracking_list.append({
            'idSerie' : str(tracking.serie.id),
            'name': tracking.serie.name,
            'cover':tracking.serie.cover,
            'author': tracking.serie.author,
            'posting_date': tracking.serie.posting_date,
            'status': tracking.serie.status,
            'posted_by': {
                'idUser': str(tracking.serie.posted_by.id),
                'first_name': tracking.serie.posted_by.first_name,
                'last_name': tracking.serie.posted_by.last_name,
                'email' : tracking.serie.posted_by.email
            },
            'owning': ownerUser
        })
    
    return jsonify(
        message = "Information received successfully",
        status = 200,
        tracking_list = tracking_list
    ), 200

# LIST OF SERIES THAT BELONG TO THE LOGGED USER ONLY #
@userRoutes.route('/user/mySeries', methods = ['GET'])
@jwt_required()
def userOwning_series():
    
    return ""


# EDITION OF BASIC INFORMATION OF THE USER #
@userRoutes.route('/user', methods = ['PUT'])
@jwt_required()
def editUser_information():
    
    data = request.json
    email = data['email']
    firstName = data['firstName']
    lastName = data['lastName']
    
    user_session = UserModel.objects(id = get_jwt_identity()).first()
    
    # CHECKING IF THE USER EXISTS #
    if user_session:
        # CHANGING USER'S INFORMATION #
        user_session.update(email = email, first_name = firstName, last_name = lastName)
        user_session.reload()
        
        return jsonify(
            message = "Changes saved successfully.",
            status = 201,
            firstName = user_session.first_name,
            lastName = user_session.last_name,
            email = user_session.email,
            id = str(user_session.id)
        ), 201
        
    else:
        
        return jsonify(message = "User not found.", status = 409), 409
     

# EDITION OF USER'S PASSWORD #
@userRoutes.route('/user/changePassword', methods = ['PUT'])
@jwt_required()
def editUser_password():
    
    # GETTING USER'S CREDENTIALS AND VALIDATING THEM #
    
    user = UserModel.objects(id = get_jwt_identity()).first()
    
    data = request.json
    oldPassword = data['oldPassword']
    newPassword = data['newPassword']
    
    if newPassword and UserModel.Verify(user.password, oldPassword):
        # SETTING NEW PASSWORD #
        user.update(password = UserModel.Encrypt(newPassword))
        user.reload()
        
        return jsonify(
            message = "Password changed successfully.",
            status = 201
        ), 201
    
    else:
        
        return jsonify(
            message = "Missing fields or wrong credentials.",
            status = 400
        ), 400


# EDITION OF USER'S PROFILE PICTURE #
@userRoutes.route('/user/profilePicture', methods = ['POST'])
@jwt_required()
def setPicture():
    
    # USER'S PICTURE RECEPTION #
    user = UserModel.objects(id = get_jwt_identity()).first()
    user_photo = request.files['profilePicture']
    
    if user_photo:
        # USER'S PHOTO IS SAVED #
        upload = uploader.upload(user_photo, folder = f'Rokumi/{user.id}', public_id = 'profilePicture')
        user.update(photo = upload['url'])
    
        return jsonify(message = "Changes saved successfully.", status = 200), 200
    
    else:
         
        return jsonify(message = "A valid file was not selected.", status = 400), 400


# DELETION OF AN EXISTING USER #
@userRoutes.route('/user', methods = ['DELETE'])
@jwt_required()
def deleteUser():
    
    # VALIDATION TO CHECK IF THE USER EXISTS, THEN DELETES ITS INFORMATION #
    user = UserModel.objects(id = get_jwt_identity()).first()
    
    if user:
        user.delete()
        
        return jsonify(message = "User deleted successfully.", status = 200), 200
    
    else: 
        
        return jsonify(message = "User does not exist.", status = 409), 409

# LOGOUT #
@userRoutes.route('/user/logout', methods = ['POST'])
@jwt_required()
def logout():
    
    return jsonify(message = "Session terminated successfully.", status = 200, user = get_jwt_identity(), loggedOut = "True"), 200