# THIS FILE WILL DEFINE ALL THE ROUTES RELATED TO A USER'S COMMENT #

from cgitb import text
import datetime
import time
from flask import request, jsonify, Blueprint
from models.Chapter_Model import ChapterModel
from models.Comment_Model import CommentModel
from models.User_Model import UserModel
from models.Serie_Model import SerieModel
from flask_jwt_extended import get_jwt_identity, jwt_required

commentRoutes = Blueprint('commentRoutes', __name__)

# CREATE A COMMENT #
@commentRoutes.route('/comment/<string:chapter_id>', methods = ['POST'])
@jwt_required()
def uploadComment(chapter_id):
    user_id = get_jwt_identity()
    data = request.json
    
    # VALIDATION TO CHECK IF THE USER FILLED ALL THE REQUIRED INFORMATION #
    if not data:    return jsonify(message = "The information was not given. Please fill all the spaces up.", status = "400"), 400
    
    # RECEPTION OF DATA #
    text = data['commentText']
    parent = data['parentOf_id']
        
    # VALIDATION TO CHECK IF THE COMMENTS IS A CHILD OR HAS CHILDREN AND CREATION OF THE COMMENT #
    if parent:
        
        newComment = CommentModel(text = text, owner = user_id, chapter = chapter_id, parent = parent)
        newComment.save()
        parentObject = CommentModel.objects(id = parent).first()
            
        poster_user = {
            'id': str(newComment.owner.id),
            'first_name': newComment.owner.first_name,
            'last_name': newComment.owner.last_name,
            'role': newComment.owner.role
        }
        
        parent_user = {
            'id': str(parentObject.owner.id),
            'first_name': parentObject.owner.first_name,
            'last_name': parentObject.owner.last_name,
            'role': parentObject.owner.role
        }
            
        return jsonify(
            message = "Comment created successfully.",
            status = "201",
            commentId = str(newComment.id),
            text = newComment.text,
            user = poster_user,
            parent = parent_user,
            date = newComment.posting_date,
            chapter = newComment.chapter,
            
            ), 201
    
    else:
        
        newComment = CommentModel(text = text, owner = user_id, chapter = chapter_id)
        newComment.save()
        
        poster_user = {
            'id': str(newComment.owner.id),
            'first_name': newComment.owner.first_name,
            'last_name': newComment.owner.last_name,
            'role': newComment.owner.role
        }
        
        return jsonify(
            message = "Comment created successfully.",
            status = "201",
            commentId = str(newComment.id),
            text = newComment.text,
            user = poster_user,
            date = newComment.posting_date,
            chapter = newComment.chapter
            ), 201
        
    
# FUNCTION TO GET A THE CHILDREN OF A COMMENT #
def getComment_children(parent):
    
    commentChildren = CommentModel.objects(parent = parent).all().order_by('date')
    commentParent = CommentModel.objects(id = parent).first()
    
    childs = []
    
    for comment in commentChildren:
        commentParent = comment.id
        
        childs.append({
            'id': comment.id,
            'postingDate': comment.posting_date,
            'text': comment.text,
            'parentId': str(comment.parent.id),
            'user': str(comment.owner.id),
            'chapter': comment.chapter,
            'parentOwner': str(parent.owner.id),
            'parentText': parent.text,
            'children': getComment_children(commentParent)
            })    
    
    return childs
