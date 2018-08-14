from django.contrib import auth
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import User
from api.serializers import SignUpSerializer, SignInSerializer, TokenSerializer, ProviderSerializer


class SignUpView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        get_user_model().objects.create_user(email=validated_data['email'], password=validated_data['password'],
                                             name=validated_data['name'], phone=validated_data['phone'],
                                             language=validated_data['language'], currency=validated_data['currency'])
        return Response({}, status=status.HTTP_201_CREATED)


class SignInView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignInSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = auth.authenticate(email=serializer.validated_data['email'],
                                 password=serializer.validated_data['password'])

        if user is None:
            raise AuthenticationFailed()

        if not Token.objects.filter(user=user).exists():
            token = Token.objects.create(user=user)
        else:
            token = Token.objects.get(user=user)

        token_serializer = TokenSerializer(data={'token': token.key})
        token_serializer.is_valid()

        return Response(data=token_serializer.data)


class ProviderPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in ['GET']

    def has_object_permission(self, request, view, obj):
        return request.method in ['GET'] or request.user.pk == obj.pk


class ProviderViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    permission_classes = (ProviderPermissions,)
    queryset = User.objects.all()
    serializer_class = ProviderSerializer
