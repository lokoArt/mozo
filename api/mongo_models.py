from pymodm import MongoModel, fields, connect
from pymongo import WriteConcern

from mozo import settings

connect(settings.MONGODB_SERVER, alias="mozo")


class ServiceArea(MongoModel):
    name = fields.CharField(required=True)
    price = fields.IntegerField(required=True)
    user_id = fields.IntegerField(required=True)
    geometry = fields.GeometryCollectionField(required=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'mozo'
