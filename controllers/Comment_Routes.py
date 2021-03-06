# THIS FILE WILL DEFINE ALL THE ROUTES RELATED TO A USER'S COMMENT #

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
@commentRoutes.route('/comment/<string:idChapter>', methods = ['POST'])
@jwt_required()
def uploadComment(idChapter):
    idUser = get_jwt_identity()
    data = request.json
    
    # VALIDATION TO CHECK IF THE USER FILLED ALL THE REQUIRED INFORMATION #
    if not data:    return jsonify(message = "The information was not given. Please fill all the spaces up.", status = 400), 400
    
    # RECEPTION OF DATA #
    text = data['commentText']
    parent = data['parentOf_id']
        
    # VALIDATION TO CHECK IF THE COMMENTS IS A CHILD OR HAS CHILDREN AND CREATION OF THE COMMENT #
    if parent:
        
        newComment = CommentModel(text = text, owner = idUser, chapter = idChapter, parent = parent)
        newComment.save()
        parentObject = CommentModel.objects(id = parent).first()
            
        poster_user = {
            'idUser': str(newComment.owner.id),
            'first_name': newComment.owner.first_name,
            'last_name': newComment.owner.last_name,
            'role': newComment.owner.role
        }
        
        parent_user = {
            'idUser': str(parentObject.owner.id),
            'first_name': parentObject.owner.first_name,
            'last_name': parentObject.owner.last_name,
            'role': parentObject.owner.role
        }
            
        return jsonify(
            message = "Comment created successfully.",
            status = 201,
            idComment = str(newComment.id),
            text = newComment.text,
            user = poster_user,
            parent = parent_user,
            date = newComment.posting_date,
            chapter = str(newComment.chapter.id),
            
            ), 201
    
    else:
        
        newComment = CommentModel(text = text, owner = idUser, chapter = idChapter)
        newComment.save()
        
        poster_user = {
            'idUser': str(newComment.owner.id),
            'first_name': newComment.owner.first_name,
            'last_name': newComment.owner.last_name,
            'role': newComment.owner.role
        }
        
        return jsonify(
            message = "Comment created successfully.",
            status = 201,
            commentId = str(newComment.id),
            text = newComment.text,
            user = poster_user,
            date = newComment.posting_date,
            chapter = str(newComment.chapter.id)
            ), 201
        
    
# FUNCTION TO GET THE CHILDREN OF A COMMENT #
def getComment_children(parent):
    
    commentChildren = CommentModel.objects(parent = parent).order_by('posting_date')
    Parent = CommentModel.objects(id = parent).first()
    
    childs = []
    
    for comment in commentChildren:
        commentParent = comment.id
        
        childs.append({
            'idComment': str(comment.id),
            'postingDate': comment.posting_date,
            'text': comment.text,
            'parent': str(Parent.id),
            'user': str(comment.owner.id),
            'chapter': str(comment.chapter.id),
            'parentText': Parent.text,
            'children': getComment_children(commentParent)
            })    
    
    return childs


# GET ALL COMMENTS OF A SPECIFIC CHAPTER #
@commentRoutes.route('/comment/<string:idChapter>', methods = ['GET'])
#@jwt_required()
def getComments(idChapter):
    comments_objects = CommentModel.objects(chapter = idChapter).all()
    chapterComments = []
    
    
    if comments_objects:
        for comment in comments_objects:
        
            chapterComments.append({
            'idComment': str(comment.id),
            'text': comment.text,
            'owner': {
                'idUser':str(comment.owner.id),
                'first_name': comment.owner.first_name,
                'last_name': comment.owner.last_name
                },
            'posting_date': comment.posting_date,
            'parent': comment.parent,
            'children': getComment_children(comment.id)
        })
        
    
        return jsonify(
            message = "Comments received successfully.",
            status = 200,
            comments = chapterComments
        ), 200
        
    else: return jsonify(message = "This chapter has no comments.", comments = chapterComments, status = 200), 200
    

# EDIT A COMMENT #
@commentRoutes.route('/comment/<string:idComment>', methods = ['PUT'])
@jwt_required()
def editComment(idComment):
    comment = CommentModel.objects(id = idComment).first()
    user = UserModel.objects(id = get_jwt_identity()).first()
    data = request.json
    
    if not data: return jsonify(message = "No data provided or a parameter is missing.", status = 409), 409
    
    else:
        text = data['commentText']
        
        # VALIDATION TO CHECK IF THE USER IS THE OWNER OF THE COMMENT OR IT IS AN ADMIN #
        if str(comment.owner.id) == str(user.id):
            comment.update(text = text)
            comment.reload()
            
            return jsonify(message = "Changes saved successfully.", status = 200)
        
        if user.role == "administrator":
            comment.update(text = text)
            comment.reload()
            
            return jsonify(message = "Changes saved successfully.", status = 200)
        
        
        return jsonify(message = "You are not allowed to edit this comment. You are neither an administrator nor the owner of the comment.",
                       status = 400), 400


# DELETE A COMMENT #
@commentRoutes.route('/comment/<string:idComment>', methods = ['DELETE'])
@jwt_required()
def deleteComment(idComment):
    comment = CommentModel.objects(id = idComment).first()
    user = UserModel.objects(id = get_jwt_identity()).first()
    
    if not comment: return jsonify(message = "comment does not exist.", status = 409), 409
    
    else:
        
        if str(comment.owner.id) == str(user.id):
            
            comment.delete()
        
            return jsonify(message = "Comment deleted successfully.", status = 200), 200
        
        if user.role == "administrator":
            
            comment.delete()
        
            return jsonify(message = "Comment deleted successfully.", status = 200), 200
        
        
    return jsonify(message = "You are not allowed to delete this comment. You are neither an administrator nor the owner of the comment.",
                   status = 400), 400
            