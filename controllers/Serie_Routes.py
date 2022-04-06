# THIS FILE WILL DEFINE THE ROUTES RELATED TO SERIES #

from flask import request, jsonify, Blueprint
from models.User_Model import UserModel
from models.Serie_Model import SerieModel
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from cloudinary import api, uploader

serieRoutes = Blueprint('serieRoutes', __name__)


# UPLOAD NEW SERIE #
@serieRoutes.route('/serie/new', methods = ['POST'])
@jwt_required()
def uploadSerie():
    user = get_jwt_identity()
    
    # RECEPTION OF SERIES INFORMATION #
    data = request.form
    
    # VALIDATION TO CHECK IF THE INFORMATION WAS GIVEN CORRECTLY #
    if not data:
        
        return jsonify(
            message = "Fill up the information requirements. One or more spaces were not completed.", 
            status = "400"), 400
    
    # VALIDATION TO CHECK IF THE SERIE ALREADY EXISTS #
    coincidence = SerieModel.objects(name = data['serieName']).first()
    if coincidence:
        
        return jsonify(message = "Serie already exists.", status = "400", serie = coincidence.name), 400
    
    
    name = data['serieName']
    author = data['serieAuthor']
    status = data['serieStatus']
    description = data['serieDescription']
    
    newSerie = SerieModel(name = name, author = author, status = status, description = description, posted_by = user).save()
    
    cover = request.files['cover']
    if cover:
        
        serieCover = uploader.upload(cover, folder = f'Rokumi/{newSerie.id}', public_id = 'serieCover')
        newSerie.update(cover = serieCover['url'])
        newSerie.reload()
    
    
    return jsonify(
        message = "Serie uploaded successfully.",
        status = "201",
        serieName = newSerie.name,
        serieAuthor = newSerie.author,
        serieCover = newSerie.cover,
        postingDate = newSerie.posting_date,
        postedBy = newSerie.posted_by,
        description = newSerie.description
    ), 201

