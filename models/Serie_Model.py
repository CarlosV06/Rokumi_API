# DEFINITION OF THE MODEL OF A SERIE #

from app import DB
import datetime
import mongoengine

class SerieModel(DB.Document):
    
    # ATTRIBUTES #
    
    name = DB.StringField(required = True, unique = True)
    description = DB.StringField(default = "")
    cover = DB.StringField(default = "")
    author = DB.StringField(default = "none")
    status = DB.StringField(default = "")
    posting_date = DB.DateTimeField(default = datetime.datetime.now())
    posted_by = DB.ReferenceField('UserModel', required = True, reverse_delete_rule = mongoengine.CASCADE)