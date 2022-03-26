# DEFINITION OF THE MODEL OF TRACKING #

from app import DB
import mongoengine

class TrackingModel(DB.Document):
    
    user = DB.ReferenceField('UserModel', reverse_delete_rule = mongoengine.CASCADE)
    serie = DB.ReferenceField('SerieModel', reverse_delete_rule = mongoengine.CASCADE)