# DEFINITION OF THE MODEL OF A COMMENT #

import datetime
from app import DB
import mongoengine

class CommentModel(DB.Document):
    text = DB.StringField(required = True)
    owner = DB.ReferenceField('UserModel', required = True, reverse_delete_rule = mongoengine.CASCADE)
    chapter = DB.ReferenceField('ChapterModel', required = True, reverse_delete_rule = mongoengine.CASCADE)
    parent = DB.ReferenceField('self', reverse_delete_rule = mongoengine.CASCADE)
    posting_date = DB.DateTimeField(default = datetime.datetime.now())