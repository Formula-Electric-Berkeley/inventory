import json
import unittest
from typing import Optional

import auth
import models
import tstutil
from identifier import Identifier


class TestBoxCreate(tstutil.TestBase):
    scope = auth.Scope.BOX_CREATE

    def test_200(self):
        attrs = {
            'name': 'tst-box-name',
            'api_key': self.superuser.api_key,
        }
        resp_json = self.call_route_assert_code(200, attrs)
        entity_json = self.assert_single_entity(
            resp_json, {
                'name': attrs['name'],
            },
        )
        self.assertIsNotNone(Identifier(length=models.Box.id_length, id_=entity_json[models.Box.id_name]))

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
            'name': 'tst-box-duplicate-name',
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(200, attrs)
        self.call_route_assert_code(400, attrs)

    def call_route(self, attrs: Optional[dict[str, str]] = None):
        return self.client.post('/api/box/create', data=attrs)


class TestBoxGet(tstutil.TestBase):
    scope = auth.Scope.BOX_GET

    def setUp(self):
        super().setUp()
        attrs = {
            'name': 'tst-box-get',
            'api_key': self.superuser.api_key,
        }
        response = self.client.post('/api/box/create', data=attrs)
        self.box = models.Box(*json.loads(response.data)['body'][0].values())

    def test_200(self):
        attrs = {
            models.Box.id_name: self.box.box_id,
        }
        resp_json = self.call_route_assert_code(200, attrs)
        self.assert_single_entity(
            resp_json, {
                models.Box.id_name: self.box.box_id,
                'name': self.box.name,
            },
        )

    def test_400_malformed_id(self):
        attrs = {
            models.Box.id_name: '*',
        }
        self.call_route_assert_code(400, attrs)

    def test_400_no_id(self):
        attrs = {}
        self.call_route_assert_code(400, attrs)

    def test_404_nonexistent_box(self):
        attrs = {
            models.Box.id_name: 'tst-box-get-nonexistent-id',
        }
        self.call_route_assert_code(404, attrs)

    def test_400_no_apikey(self):
        # No authentication required
        pass

    def test_400_malformed_apikey(self):
        # No authentication required
        pass

    def test_401_user_not_found(self):
        # No authentication required
        pass

    def test_403_user_unauthorized(self):
        # No authentication required
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/get', data=attrs)


class TestBoxUpdate(tstutil.TestBase):
    scope = auth.Scope.BOX_UPDATE

    def test_200(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_400_malformed_id(self):
        pass

    def test_400_no_id(self):
        pass

    def test_404_nonexistent_box(self):
        pass

    def test_400_change_immutable_properties(self):
        pass

    def test_400_no_update_properties(self):
        pass

    def test_400_malformed_update_properties(self):
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/update', data=attrs)


class TestBoxRemove(tstutil.TestBase):
    scope = auth.Scope.BOX_REMOVE

    def test_200(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_400_malformed_id(self):
        pass

    def test_400_no_id(self):
        pass

    def test_404_nonexistent_box(self):
        pass

    def test_500_duplicate_id(self):
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/remove', data=attrs)


# TODO finish
class TestBoxesList(tstutil.TestBase):
    scope = auth.Scope.BOXES_LIST

    def test_200(self):
        pass

    def test_400_no_apikey(self):
        # No authentication required
        pass

    def test_400_malformed_apikey(self):
        # No authentication required
        pass

    def test_401_user_not_found(self):
        # No authentication required
        pass

    def test_403_user_unauthorized(self):
        # No authentication required
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/boxes/list', data=attrs)


if __name__ == '__main__':
    unittest.main()
