# DEFINITION OF THE MODEL OF A CHAPTER #

from app import DB
import datetime
import mongoengine
from models.Serie_Model import SerieModel

# CHAPTER #
class ChapterModel(DB.Document):
    
    # ATTRIBUTES #
    name = DB.StringField(required = True)
    released = DB.DateTimeField(default = datetime.datetime.now())
    chapter_number = DB.StringField(default = "0", unique = True)
    pages = DB.ListField(DB.StringField(), default = [])
    serie = DB.ReferenceField('SerieModel', required = True, reverse_delete_rule = mongoengine.CASCADE)