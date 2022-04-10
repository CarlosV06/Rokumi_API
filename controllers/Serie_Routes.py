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
                'id': str(serie.id),
                'name': serie.name,
                'cover': serie.cover,
                'status': serie.status,
                'posting_date': serie.posting_date,
                'author': serie.author,
                'posted_by':{
                    'userId': str(serie.posted_by.id),
                    'first_name': serie.posted_by.first_name,
                    'last_name': serie.posted_by.last_name,
                }
            })
            
            
        return jsonify(
            message = "Information received successfully.",
            status = "200",
            data = series
            ), 200
        
        
    except: return jsonify(message = "An error has occurred while getting the information.", status = "400"), 400
        
    
# GET THE PROFILE OF A SERIE #
@serieRoutes.route('/serie/<string:idSerie>', methods = ['GET'])
def getSerie_profile(idSerie):
    
    # LOCATION OF DATA RELATED TO THE SELECTED SERIE #
    serie = SerieModel.objects(id = idSerie).first()
    
    if not serie: return jsonify(message = "serie not found", status = "400"), 400

    chapters = []
    for chapter in ChapterModel.objects(serie = serie.id).all():
        
        chapters.append({
            'idChapter': str(chapter.id),
            'chapterName': chapter.name,
            'chapter_number':chapter.chapter_number,
            'released': chapter.released
        })

    serieInfo = {
        'idSerie': str(serie.id),
        'name': serie.name,
        'description': serie.description,
        'cover': serie.cover,
        'author': serie.author,
        'status': serie.status,
        'posting_date': serie.posting_date,
        'posted_by': {
                    'userId': str(serie.posted_by.id),
                    'first_name': serie.posted_by.first_name,
                    'last_name': serie.posted_by.last_name,
        },
        'chapters': chapters
    }
    
    return jsonify(message = "information received successfully.", status = "200", data = serieInfo), 200
    
