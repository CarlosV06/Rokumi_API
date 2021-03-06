# DEFINITION OF THE MODEL OF TRACKING #

from app import DB
import mongoengine
from models.User_Model import UserModel
from models.Serie_Model import SerieModel

class TrackingModel(DB.Document):
    
    user = DB.ReferenceField('UserModel', reverse_delete_rule = mongoengine.CASCADE)
    serie = DB.ReferenceField('SerieModel', reverse_delete_rule = mongoengine.CASCADE)