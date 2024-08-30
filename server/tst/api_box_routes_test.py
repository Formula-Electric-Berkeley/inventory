import unittest
from typing import Optional

import auth
import models
import testutil
from identifier import Identifier


class TestBoxCreate(testutil.TestBase):
    scope = auth.Scope.BOX_CREATE

    def test_200(self):
        attrs = {
            'name': 'test-box-name',
            'api_key': self.superuser.api_key,
        }
        resp_json = self.call_route_assert_code(200, attrs)

        self.assertIn('body', resp_json)
        self.assertIsNotNone(resp_json['body'])
        self.assertEqual(1, len(resp_json['body']))
        created_box = resp_json['body'][0]
        self.assertIsNotNone(created_box)
        self.assertIn('name', created_box)
        self.assertEqual(attrs['name'], created_box['name'])

        self.assertIsNotNone(Identifier(length=models.Box.id_length, id_=created_box[models.Box.id_name]))

    def test_400_no_name(self):
        attrs = {
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs)

    def test_400_malformed_name(self):
        attrs = {
            'name': '*',
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs)

    def test_400_duplicate_name(self):
        attrs = {
            'name': 'test-box-duplicate-name',
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(200, attrs)
        self.call_route_assert_code(400, attrs)

    def call_route(self, attrs: Optional[dict[str, str]] = None):
        return self.client.post('/api/box/create', data=attrs)


if __name__ == '__main__':
    unittest.main()
