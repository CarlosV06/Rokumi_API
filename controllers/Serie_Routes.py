# THIS FILE WILL DEFINE THE ROUTES RELATED TO SERIES #

from flask import request, jsonify, Blueprint
from models.Chapter_Model import ChapterModel
from models.Tracking_Model import TrackingModel
from models.User_Model import UserModel
from models.Serie_Model import SerieModel
from flask_jwt_extended import get_jwt_identity, jwt_required
from cloudinary import api, uploader

serieRoutes = Blueprint('serieRoutes', __name__)


# UPLOAD NEW SERIE #
@serieRoutes.route('/serie', methods = ['POST'])
@jwt_required()
def uploadSerie():
    user = get_jwt_identity()
    
    # RECEPTION OF SERIES INFORMATION #
    data = request.form
    
    # VALIDATION TO CHECK IF THE INFORMATION WAS GIVEN CORRECTLY #
    if not data:
        
        return jsonify(
            message = "Fill up the information requirements. One or more spaces were not completed.", 
            status = 400), 400
    
    # VALIDATION TO CHECK IF THE SERIE ALREADY EXISTS #
    coincidence = SerieModel.objects(name = data['serieName']).first()
    if coincidence:
        
        return jsonify(message = "Serie already exists.", status = 400, serie = coincidence.name), 400
    
    
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
    
    # SAVING UPLOADER USER'S TRACKING #
    
    Tracking = TrackingModel(user = get_jwt_identity(), serie = str(newSerie.id))
    Tracking.save()
    
    return jsonify(
        message = "Serie uploaded successfully.",
        status = "201",
        serieName = newSerie.name,
        serieAuthor = newSerie.author,
        serieCover = newSerie.cover,
        postingDate = newSerie.posting_date,
        postedBy = str(newSerie.posted_by.id),
        description = newSerie.description
    ), 201
    
# GET ALL SERIES #
@serieRoutes.route('/serie', methods = ['GET'])
def getSeries():
    
    try:
        # GETTING ALL THE SERIES #
        series = []
        for serie in SerieModel.objects().all():
            
            series.append({
                'idSerie': str(serie.id),
                'name': serie.name,
                'cover': serie.cover,
                'status': serie.status,
                'posting_date': serie.posting_date,
                'author': serie.author,
                'posted_by':{
                    'idUser': str(serie.posted_by.id),
                    'first_name': serie.posted_by.first_name,
                    'last_name': serie.posted_by.last_name,
                },
            })
            
            
        return jsonify(
            message = "Information received successfully.",
            status = "200",
            data = series
            ), 200
        
        
    except: return jsonify(message = "An error has occurred while getting the information.", status = 400), 400

# SERIES THAT BELONG TO THE LOGGED USER ONLY #
@serieRoutes.route('/serie/mySeries', methods = ['GET'])
@jwt_required()
def userOwning_series():
    
    userSeries = []
    for serie in SerieModel.objects(posted_by = get_jwt_identity()).all():

        following = False
        tracking = TrackingModel.objects(serie = serie.id, user = get_jwt_identity()).first()
        if tracking is not None:
            following = True
        
        userSeries.append({
            'idSerie' : str(serie.id),
            'name': serie.name,
            'cover':serie.cover,
            'author': serie.author,
            'posting_date': serie.posting_date,
            'status': serie.status,
            'following': following
        })
    
    return jsonify(
        message = "Information received successfully.",
        status = 200,
        series = userSeries
    ), 200

# GET THE PROFILE OF A SERIE #
@serieRoutes.route('/serie/<string:idSerie>', methods = ['GET'])
def getSerie_profile(idSerie):
    
    # LOCATION OF DATA RELATED TO THE SELECTED SERIE #
    serie = SerieModel.objects(id = idSerie).first()
    
    if not serie: return jsonify(message = "serie not found", status = 400), 400

    chapters = []
    for chapter in ChapterModel.objects(serie = serie.id).all():
        
        chapters.append({
            'idChapter': str(chapter.id),
            'chapterName': chapter.name,
            'chapter_number':chapter.chapter_number,
            'released': chapter.released
        })

    following = False
    tracking = TrackingModel.objects(serie = serie.id, user = get_jwt_identity()).first()
    if tracking is not None:
        following = True
    
    serieInfo = {
        'idSerie': str(serie.id),
        'name': serie.name,
        'description': serie.description,
        'cover': serie.cover,
        'author': serie.author,
        'status': serie.status,
        'posting_date': serie.posting_date,
        'posted_by': {
                    'idUser': str(serie.posted_by.id),
                    'first_name': serie.posted_by.first_name,
                    'last_name': serie.posted_by.last_name,
        },
        'chapters': chapters,
        'following': following
    }
    
    return jsonify(message = "information received successfully.", status = 200, data = serieInfo), 200
    

# EDITION OF A SERIE #
@serieRoutes.route('/serie/<string:idSerie>', methods = ['PUT'])
@jwt_required()
def editSerie(idSerie):
    data = request.form
    user = UserModel.objects(id = get_jwt_identity()).first()
    serie_obj = SerieModel.objects(id = idSerie).first()
    
    # VALIDATION TO CHECK IF THE INFORMATION WAS GIVEN #
    if not data: return jsonify(message = "No data provided or a parameter is missing.", status = 400), 400
    
    else: 
        name = data['serieName']
        author = data['serieAuthor']
        status = data['serieStatus']
        cover = request.files['cover']
        description = data['serieDescription']
        
        # VALIDATION TO CHECK IF THE SERIE WAS UPLOADED BY THE LOGGED USER OR IF THE USER IS AN ADMIN #
        if str(serie_obj.posted_by.id) == str(user.id):
            
            serie_obj.update(name = name, author = author, status = status, description = description)
            serie_obj.reload()
            
            if cover:
               serieCover = uploader.upload(cover, folder = f'Rokumi/{serie_obj.id}', public_id = 'serieCover')
               serie_obj.update(cover = serieCover['url'])
               serie_obj.reload()
            

            return jsonify(
                message = "Changes saved successfully.",
                status = 200,
            ), 200
            
            
        if user.role == 'administrator':
             
            serie_obj.update(name = name, author = author, status = status, description = description)
            serie_obj.reload()
            
            if cover:
               serieCover = uploader.upload(cover, folder = f'Rokumi/{serie_obj.id}', public_id = 'serieCover')
               serie_obj.update(cover = serieCover['url'])
               serie_obj.reload()
            

            return jsonify(
                message = "Changes saved successfully.",
                status = 200,
                ), 200
    
     
        return jsonify(message = "You are not allowed to edit this serie. You are neither an administrator nor owner of the serie.",
                       status = 400), 400
        

