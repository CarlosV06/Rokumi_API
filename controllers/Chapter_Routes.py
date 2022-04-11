# THIS FILE WILL DEFINE ALL THE ROUTES RELATED TO A CHAPTER #

import datetime
from email import message
import time
from xml.etree.ElementTree import Comment
from flask import request, jsonify, Blueprint
from models.Chapter_Model import ChapterModel
from models.Comment_Model import CommentModel
from models.User_Model import UserModel
from models.Serie_Model import SerieModel
from flask_jwt_extended import get_jwt_identity, jwt_required
from cloudinary import api, uploader

chapterRoutes = Blueprint('chapterRoutes', __name__)

# UPLOAD A CHAPTER #
@chapterRoutes.route('/chapter/<string:serie_id>', methods = ['POST'])
@jwt_required()
def uploadChapter(serie_id):

    # RECEPTION OF USER'S DATA #
    data = request.form
    
    if not data:
        return jsonify(message = "Data was not given.", status = "400"), 400
    
    # LOCATION OF THE SERIE #
    serie = SerieModel.objects(id = serie_id).first()
    
    name = data['chapterName']
    chapter_number = data['chapterNumber']
    
    coincidence = ChapterModel.objects(name = name).first()
    if coincidence and coincidence.chapter_number is chapter_number:
        return jsonify(message = "Chapter already exists", status = "400"), 400
    
    newChapter = ChapterModel(name = name, chapter_number = chapter_number, serie = str(serie.id))
    newChapter.save()
    
    # UPLOADING THE PAGES OF THE SERIE TO CLOUDINARY AND SAVING THEIR URL #
    
    if 'pages' in request.files:
        pages_urls = []
        
        for index, page in enumerate(request.files.getlist('pages'), start = 1):
            print(index, page.filename)
            uploadPage = uploader.upload(page, folder = f'Rokumi/{str(serie.id)}/{newChapter.name}/{index}', public_id = str(time.time()))
            pages_urls.append(uploadPage['url'])
            
        newChapter.update(pages = pages_urls)
        newChapter.reload()
        
        
    return jsonify(
        message = "The chapter has been added successfully!",
        status = "201",
        idChapter = str(newChapter.id),
        chapterName = newChapter.name,
        number = newChapter.chapter_number,
        serie = newChapter.serie,
        user = get_jwt_identity()
    ), 201


# READ A CHAPTER #
@chapterRoutes.route('/chapter/<string:idChapter>', methods = ['GET'])
def readChapter(idChapter):
    
    # LOCATION OF THE INFORMATION AND PAGES OF THE CHAPTER #
    chapter_obj = ChapterModel.objects(id = idChapter).first()
    if not chapter_obj: return jsonify(message = "Chapter not found.", status = "400"), 400
    
    else:
        
        if 'pages' in chapter_obj:
            pages = []
            
            for page in chapter_obj.pages:
                pages.append(page)
        
        chapter = {
            'idChapter': str(chapter_obj.id),
            'name': chapter_obj.name,
            'chapter_number': chapter_obj.chapter_number,
            'serie': {
                'serieName': chapter_obj.serie.name,
                'idSerie': str(chapter_obj.serie.id)
            },
            'released': chapter_obj.released,
            'pages': pages
        }
        
                
        return jsonify(
            message = "Information received successfully.",
            status = "200",
            chapterInfo = chapter
        ), 200
    
