import os
os.environ['DATABASE_URL'] = 'sqlite:///../test.sqlite'

import unittest
from app_v1.__init__ import create_app, db, api
from app_v1.models import User
from test_client import TestClient

class TestAPI(unittest.TestCase):
    default_username = 'jakub'
    default_password = 'Freeman'

    def setUp(self):
        self.app = app
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username)
        u.set_password(self.default_password)
        db.session.add(u)
        db.session.commit()
        self.client = TestClient(self.app,'','Freeman')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_customers(self):
        # get list of customers
        rv, json = self.client.get('/modules/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['modules'] == [])

        # add a customer
        module_data = {'UserId': 'aaac', 'CourseSoftwareId':'aaaaa', 'CourseMaterialId':'bbbbb', 'N2K':.25,
                        'DAK':.32, 'Included':1, 'FilteredOut':0, 'CreatedDate':'22 Jan 2013', 'ModifiedDate':'23 Jun 2013'}
        rv, json = self.client.post('/modules/', data=module_data)
        self.assertTrue(rv.status_code == 201)
        location = rv.headers['Location']
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['UserId'] == 'aaac')
        rv, json = self.client.get('/modules/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['modules'] == [location])

        '''
        # edit the customer
        rv, json = self.client.put(location, data={'name': 'John Smith'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'John Smith')
        '''

if __name__ == '__main__':
    unittest.main()