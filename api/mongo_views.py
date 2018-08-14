import coreschema
from pymodm_rest import viewsets
from pymodm_rest.schemas import MongoSchema, MethodField
from rest_framework import permissions
from api.mongo_models import ServiceArea


class ServiceAreaPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in ['GET']

    def has_object_permission(self, request, view, obj):
        return request.method in ['GET'] or request.user.pk == obj.user_id


class ServiceAreaViewSet(viewsets.ModelViewSet):
    permission_classes = (ServiceAreaPermissions,)
    queryset = ServiceArea.objects
    instance_class = ServiceArea
    lookup_field = '_id'

    schema = MongoSchema(manual_fields=[
        MethodField(
            "body",
            required=True,
            location="body",
            schema=coreschema.Object(),
            methods=['POST', 'PUT', 'PATCH'],
        ),
        MethodField(
            "lat",
            required=False,
            location="query",
            schema=coreschema.Number(),
            methods=['GET'],
        ),
        MethodField(
            "lng",
            required=False,
            location="query",
            schema=coreschema.Number(),
            methods=['GET'],
        ),
    ])

    def filter_queryset(self, queryset):
        if 'lat' in self.request.query_params and 'lng' in self.request.query_params:
            lat = float(self.request.query_params['lat'])
            lng = float(self.request.query_params['lng'])

            return queryset.raw({'geometry': {'$geoIntersects': {'$geometry': {
                'type': 'Point',
                'coordinates': [lat, lng]
            }}}})
        else:
            return queryset

    def perform_create(self, instance):
        instance.user_id = self.request.user.pk
        super(ServiceAreaViewSet, self).perform_create(instance)
