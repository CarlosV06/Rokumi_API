# DEFINITION OF THE MODEL OF A COMMENT #

from email.policy import default
from app import DB
import datetime
import mongoengine

class CommentModel(DB.Document):
    text = DB.StringField(required = True)
    owner = DB.ReferenceField('UserModel', required = True, reverse_delete_rule = mongoengine.CASCADE)
    chapter = DB.ReferenceField('ChapterModel', required = True, reverse_delete_rule = mongoengine.CASCADE)
    parent = DB.ReferenceField('self', reverse_delete_rule = mongoengine.CASCADE)