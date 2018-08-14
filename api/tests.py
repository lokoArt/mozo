import json

# Create your tests here.
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from api.models import User
from api.mongo_models import ServiceArea


class TestCases(APITestCase):
    user_payload = {'email': 'some-email@gmail.com', 'password': 'pass001', 'name': 'Provider 1', 'phone': '+661231312',
                    'language': 'EN', 'currency': 'USD'}
    user2_payload = {'email': 'some-email2@gmail.com', 'password': 'pass002', 'name': 'Provider 1',
                     'phone': '+661231312', 'language': 'EN', 'currency': 'USD'}

    @classmethod
    def __clean_db(cls):
        ServiceArea.objects.all().delete()

    @classmethod
    def __read_service_template(cls, template):
        str = open('api/test-resources/{}'.format(template)).read()
        return json.loads(str)

    def __create_service(self, template):
        payload = self.__read_service_template(template)
        return self.client.post('/service-areas/', payload, format='json')

    def __create_user(self, payload):
        api_client = APIClient()
        response = api_client.post('/providers/signup/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def __login(self, payload):
        # create
        token = Token.objects.create(user=User.objects.get(email=payload['email']))
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def __prepare_db_and_client(self):
        self.__clean_db()
        self.__create_user(self.user_payload)
        self.__login(self.user_payload)
        self.__create_service('service-area-1.json')

    def test_create_service_area_anonymous(self):
        payload = self.__read_service_template('service-area-1.json')

        api_client = APIClient()
        # create
        response = api_client.post('/service-areas/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crud_service_area(self):
        self.__prepare_db_and_client()

        # list
        response = self.client.get('/service-areas/')
        self.assertEqual(len(response.data), 1)
        service_id = response.data[0]['id']

        # read
        response = self.client.get('/service-areas/{}/'.format(service_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # update
        upd_service_area_data = json.loads(open('api/test-resources/service-area-2.json').read())
        response = self.client.put('/service-areas/{}/'.format(service_id), upd_service_area_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], upd_service_area_data['name'])

        # delete
        response = self.client.delete('/service-areas/{}/'.format(service_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # read
        response = self.client.get('/service-areas/{}/'.format(service_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_signup(self):
        api_client = APIClient()
        response = api_client.post('/providers/signup/', self.user_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email=self.user_payload['email']).count(), 1)

    def test_signin(self):
        self.__prepare_db_and_client()

        api_client = APIClient()
        response = api_client.post('/providers/signin/', self.user_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invalid_payload = {'email': 'some-email@gmail.com', 'password': 'pass001-wrong'}
        api_client = APIClient()
        response = api_client.post('/providers/signin/', invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_service_other_permissions(self):
        self.__prepare_db_and_client()

        self.__create_user(self.user2_payload)
        self.__login(self.user2_payload)

        # list
        response = self.client.get('/service-areas/')
        self.assertEqual(len(response.data), 1)
        service_id = response.data[0]['id']

        # read
        response = self.client.get('/service-areas/{}/'.format(service_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # update
        upd_service_area_data = json.loads(open('api/test-resources/service-area-2.json').read())
        response = self.client.put('/service-areas/{}/'.format(service_id), upd_service_area_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # delete
        response = self.client.delete('/service-areas/{}/'.format(service_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_service_payloads(self):
        self.__create_user(self.user_payload)
        self.__login(self.user_payload)

        # create
        response = self.__create_service('service-area-invalid.json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # update
        service_id = self.__create_service('service-area-1.json').data['id']
        upd_service_area_data = json.loads(open('api/test-resources/service-area-invalid.json').read())
        response = self.client.put('/service-areas/{}/'.format(service_id), upd_service_area_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_getting_services_by_coordinates(self):
        self.__prepare_db_and_client()

        response = APIClient().get('/service-areas/?lat=22.515&lng=57.631')
        self.assertEqual(len(response.data), 0)

        response = APIClient().get('/service-areas/?lat=42.515&lng=57.631')
        self.assertEqual(len(response.data), 1)

        self.__create_service('service-area-3-multi-geometry.json')
        response = APIClient().get('/service-areas/?lat=42.515&lng=57.631')
        self.assertEqual(len(response.data), 2)

        response = APIClient().get('/service-areas/?lat=11&lng=26')
        self.assertEqual(len(response.data), 1)

    def test_provider_api(self):
        self.__prepare_db_and_client()

        response = APIClient().get('/providers/')
        self.assertEqual(len(response.data), 1)

        response = APIClient().get('/providers/{}/'.format(response.data[0]['id']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # change name
        response = self.client.patch('/providers/{}/'.format(response.data['id']),
                                     {'name': 'new name', 'email': 'new@gmail.com'})
        self.assertEqual(response.data['name'], 'new name')
        self.assertNotEqual(response.data['email'], 'new@gmail.com')

        # full update
        modified_payload = self.user_payload
        modified_payload['email'] = 'new@gmail.com'
        modified_payload['name'] = 'new name'

        response = self.client.put('/providers/{}/'.format(response.data['id']), modified_payload)
        self.assertEqual(response.data['name'], modified_payload['name'])
        self.assertNotEqual(response.data['email'], 'new@gmail.com')

        # delete
        response = self.client.delete('/providers/{}/'.format(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_provider_other_permissions(self):
        self.__prepare_db_and_client()

        self.__create_user(self.user2_payload)
        self.__login(self.user2_payload)

        response = APIClient().get('/providers/')
        self.assertEqual(len(response.data), 2)
        provider_id = response.data[0]['id']
        # change name
        response = self.client.patch('/providers/{}/'.format(provider_id), {'name': 'new name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # delete
        response = self.client.delete('/providers/{}/'.format(provider_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
