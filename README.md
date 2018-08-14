## Description
This project is AWS serverless compatible Django application. The application stores and processes GeoJson data.

#### Tech used in this app
 1) Django
 2) Django REST Framework
 3) MongoDB
 4) Mysql
 5) Pymodm
 6) Pymodm_rest (https://github.com/lokoArt/pymodm_rest)
 7) Zappa for serverless deploying
 8) CoreAPI
 
#### Local start
Change/select mysql/mongodb in mozo/settings.py
```
pip instal -r requirements
./manage.py runserver
```

#### Deploying to AWS
Update zappa_setting.json setting correct credentials and AWS S3 bucket
```
zappa deploy dev
./manage.py collectstatic
```

#### Documentation
Documentation is available on {host}:{port}/docs . 

However, schemas of endpoints which depend on Mongodb are not displayed properly due to unfinished Pymodm_rest  package.

#### Temporally server
Documentation can be viewed here, also can play with API by this link.

https://b09zlcti7k.execute-api.ap-southeast-1.amazonaws.com/dev/docs/

#### A few more words
There are some slight "bugs/features" related to documentation, they should be fixed implementing more sophisticated 
Schema Generator. In the ideal worlds schema should always be generated automatically. Shouldn't be complicated.

#### Example of service-area's payload
As MongoDB schema generation is in process this payload might help
```json
{
  "name": "Test provider",
  "price": 999,
  "geometry": {
    "type": "GeometryCollection",
    "geometries": [
      {
        "type": "Polygon",
        "coordinates": [
          [
            [
              40.515,
              60.125
            ],
            [
              40.515,
              55.631
            ],
            [
              65.0390625,
              55.631
            ],
            [
              65.0390625,
              60.125
            ],
            [
              40.515,
              60.125
            ]
          ]
        ]
      }
    ]
  }
}

```
