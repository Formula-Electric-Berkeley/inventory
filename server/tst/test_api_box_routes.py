import json
import unittest
from typing import Optional

import auth
import models
import tstutil
from identifier import Identifier


class TestBoxCreate(tstutil.TestBase, tstutil.AuthorizedTests):
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


class TestBoxGet(tstutil.TestBase, tstutil.IdTests):
    entity_type = models.Box

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

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/get', data=attrs)


class TestBoxUpdate(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.BOX_UPDATE
    entity_type = models.Box

    def test_200(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_400_change_immutable_properties(self):
        pass

    def test_400_no_update_properties(self):
        pass

    def test_400_malformed_update_properties(self):
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/update', data=attrs)


class TestBoxRemove(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.BOX_REMOVE
    entity_type = models.Box

    def test_200(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_500_duplicate_id(self):
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/box/remove', data=attrs)


class TestBoxesList(tstutil.TestBase):
    def test_200(self):
        pass

    def test_400_limit_malformed(self):
        pass

    def test_400_limit_noninteger(self):
        pass

    def test_400_direction_malformed(self):
        pass

    def test_400_sortby_malformed(self):
        pass

    def test_400_invalid_sort_key(self):
        pass

    def call_route(self, attrs: dict[str, str]):
        return self.client.post('/api/boxes/list', data=attrs)


if __name__ == '__main__':
    unittest.main()
