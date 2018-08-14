from rest_framework import serializers

from api.models import User


class SignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256, allow_blank=False)
    phone = serializers.CharField(max_length=64, allow_blank=False)
    language = serializers.CharField(max_length=2, allow_blank=False)
    currency = serializers.CharField(max_length=3, allow_blank=False)

    class Meta:
        model = User
        fields = ('email',
                  'password',
                  'name',
                  'phone',
                  'language',
                  'currency')


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=256)


class ProviderSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    email = serializers.EmailField()
    name = serializers.CharField(source='provider.name')
    phone = serializers.CharField(source='provider.phone')
    language = serializers.CharField(source='provider.language')
    currency = serializers.CharField(source='provider.currency')

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'name',
                  'phone',
                  'language',
                  'currency')

    def update(self,  instance, validated_data):
        provider = instance.provider
        provider_data = validated_data.pop('provider', {})

        provider.name = provider_data.pop('name', provider.name)
        provider.phone = provider_data.pop('phone', provider.phone)
        provider.language = provider_data.pop('language', provider.language)
        provider.currency = provider_data.pop('currency', provider.currency)
        provider.save()

        # don't update use itself, email must be be updated through another endppoint
        return instance