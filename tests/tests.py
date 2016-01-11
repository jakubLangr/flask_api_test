import unittest
from werkzeug.exceptions import NotFound
from app_v1 import create_app, db
from app_v1.models import User, ValidationError
from .test_client import TestClient


class TestAPI(unittest.TestCase):
    default_username = 'john'
    default_password = 'horsenosebattery'

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username)
        u.set_password(self.default_password)
        db.session.add(u)
        db.session.commit()
        self.client = TestClient(self.app, u.generate_auth_token(), '') # u.generate_auth_token()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_modules(self):

        # get list of customers
        rv, json = self.client.get('/modules/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['module ids'] == [] )

        # add a module data 
        module_data = { 'UserId' : 'aaaaa',
                                    'CourseMaterialId' : 'bbbbb',
                                    'CourseSoftwareId' : 'ExcelYYY',
                                    'N2K' : .25,
                                    'DAK' : .32,
                                    'Included' : 1,
                                    'FilteredOut': 0,
                                    'CreatedDate' : '22 Jan 2013',
                                    'ModifiedDate' : '23 Jun 2013' } 
        rv, json = self.client.post('/modules/',
                                    data=module_data)

        self.assertTrue(rv.status_code == 201)
        location = rv.headers['Location']
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['UserId'] == 'aaaaa')
        rv, json = self.client.get('/modules/')
        self.assertTrue(rv.status_code == 200)
        
        # gets location = '/modules/1' to int(1) 
        # is this the best way to do this?
        self.assertTrue(json['module ids'] == [ int(location.split('/')[2])  ])

        # edit the customer
        rv, json = self.client.patch(location, data={'UserId': 'zzzz'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['UserId'] == 'zzzz')


        # testing module (unique) id functionality, then delete
        url = '/module-id/' + str(module_data['CourseSoftwareId']) + '/' + str(module_data['CourseMaterialId'])
        url += '/' + 'zzzz'
        rv, json = self.client.get(url)
        
        location = json['ids'][0]
        location = '/modules/' + str(location)

        rv, json = self.client.delete(location)

    def test_filter_replies(self):
        # get list of replies
        rv, json = self.client.get('/filterReplies/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(type(json['filterReplies']) == type([]))

        # add a set of replies
        posted_data = {'UserId': 'aaaa',
                        'CourseSoftwareId' : 'bbbbb',
                        'Answer' : 5.0, 
                        'MaxAnswer': 12,
                        'CreatedDate': '22 Jan 2013',
                        'ModifiedDate': '22 Jun 2013'}

        with self.assertRaises(ValidationError):
            self.client.post('/filterReplies/',
                                data=posted_data)

        posted_data['Type'] = 'AOI'
        rv, json = self.client.post('/filterReplies/',
                                    data=posted_data)


        location = '/filterReplies/' + rv.headers['Location']
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['UserId'] == 'aaaa')
        rv, json = self.client.get('/filterReplies/')
        self.assertTrue(rv.status_code == 200)
        response = json['filterReplies']
        del response[0]['id']
        posted_data['CreatedDate'] = response[0]['CreatedDate']
        posted_data['ModifiedDate'] = response[0]['ModifiedDate']
        self.assertTrue(response == [posted_data])

        # get the ids of a filterReply by CSI and UserId
        self.client.post('/filterReplies/',data=posted_data)
        rv, json = self.client.get('/filterReplies/bbbbb/aaaa')
        self.assertTrue(len(json['ids']) == 2) 

        # edit the list of replies
        rv, json = self.client.patch(location, data={'UserId': 'Jakub Langr'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['UserId'] == 'Jakub Langr')

        # delete both objects, obtain the unique id for the second
        self.client.delete(location)
        rv, json = self.client.get('/filterReplies/')

        location = '/filterReplies/' + str(json['filterReplies'][0]['id'])
        self.client.delete(location)

'''

    def test_orders_and_items(self):
        # define a customer
        rv, json = self.client.post('/api/v1/customers/',
                                    data={'name': 'john'})
        self.assertTrue(rv.status_code == 201)
        customer = rv.headers['Location']
        rv, json = self.client.get(customer)
        orders_url = json['orders_url']
        rv, json = self.client.get(orders_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['orders'] == [])

        # define two products
        rv, json = self.client.post('/api/v1/products/',
                                    data={'name': 'prod1'})
        self.assertTrue(rv.status_code == 201)
        prod1 = rv.headers['Location']
        rv, json = self.client.post('/api/v1/products/',
                                    data={'name': 'prod2'})
        self.assertTrue(rv.status_code == 201)
        prod2 = rv.headers['Location']

        # create an order
        rv, json = self.client.post(orders_url,
                                    data={'date': '2014-01-01T00:00:00Z'})
        self.assertTrue(rv.status_code == 201)
        order = rv.headers['Location']
        rv, json = self.client.get(order)
        items_url = json['items_url']
        rv, json = self.client.get(items_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['items'] == [])
        rv, json = self.client.get('/api/v1/orders/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['orders']) == 1)
        self.assertTrue(order in json['orders'])

        # edit the order
        rv, json = self.client.put(order,
                                   data={'date': '2014-02-02T00:00:00Z'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(order)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['date'] == '2014-02-02T00:00:00Z')

        # add two items to order
        rv, json = self.client.post(items_url, data={'product_url': prod1,
                                                     'quantity': 2})
        self.assertTrue(rv.status_code == 201)
        item1 = rv.headers['Location']
        rv, json = self.client.post(items_url, data={'product_url': prod2,
                                                     'quantity': 1})
        self.assertTrue(rv.status_code == 201)
        item2 = rv.headers['Location']
        rv, json = self.client.get(items_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['items']) == 2)
        self.assertTrue(item1 in json['items'])
        self.assertTrue(item2 in json['items'])
        rv, json = self.client.get(item1)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['product_url'] == prod1)
        self.assertTrue(json['quantity'] == 2)
        self.assertTrue(json['order_url'] == order)
        rv, json = self.client.get(item2)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['product_url'] == prod2)
        self.assertTrue(json['quantity'] == 1)
        self.assertTrue(json['order_url'] == order)

        # edit the second item
        rv, json = self.client.put(item2, data={'product_url': prod2,
                                                'quantity': 3})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(item2)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['product_url'] == prod2)
        self.assertTrue(json['quantity'] == 3)
        self.assertTrue(json['order_url'] == order)

        # delete first item
        rv, json = self.client.delete(item1)
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(items_url)
        self.assertFalse(item1 in json['items'])
        self.assertTrue(item2 in json['items'])

        # delete order
        rv, json = self.client.delete(order)
        self.assertTrue(rv.status_code == 200)
        with self.assertRaises(NotFound):
            rv, json = self.client.get(item2)
        rv, json = self.client.get('/api/v1/orders/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['orders']) == 0)


'''
