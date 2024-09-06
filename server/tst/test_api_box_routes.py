import json
import sqlite3
import unittest
from typing import Dict
from typing import List
from typing import Optional

import auth
import common
import models
import tstutil
from identifier import Identifier


class TestBoxCreate(tstutil.TestBase, tstutil.AuthorizedTests):
    scope = auth.Scope.BOX_CREATE

    def test_200(self):
        attrs = {
            'name': 'tst-box-name',
            auth.API_KEY_NAME: self.superuser.api_key,
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
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'name was not found in request')

    def test_400_malformed_name(self):
        attrs = {
            'name': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'name was malformed')

    def test_400_duplicate_name(self):
        attrs = {
            'name': 'tst-box-duplicate-name',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(200, attrs)
        self.call_route_assert_code(400, attrs, f'Box with name {attrs["name"]} already exists')

    def call_route(self, attrs: Optional[Dict[str, str]] = None):
        return self.client.post('/api/box/create', data=attrs)


class TestBoxGet(tstutil.TestBase, tstutil.IdTests):
    entity_type = models.Box

    def setUp(self):
        super().setUp()
        attrs = {
            'name': 'tst-box-get',
            auth.API_KEY_NAME: self.superuser.api_key,
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

    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/box/get?{params}'
        return self.client.get(url)


class TestBoxGetDynamicGET(TestBoxGet):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/box/get?{params}'
        return self.client.get(url)


class TestBoxGetStaticGET(TestBoxGet):
    def test_400_no_id(self):
        # Static route requires an ID by definition
        pass

    def call_route(self, attrs: Dict[str, str]):
        url = f'/api/box/get/{attrs[models.Box.id_name]}'
        return self.client.get(url)


class TestBoxUpdate(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.BOX_UPDATE
    entity_type = models.Box

    def setUp(self):
        super().setUp()
        attrs = {
            'name': 'tst-box-update',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        response = self.client.post('/api/box/create', data=attrs)
        self.box = models.Box(*json.loads(response.data)['body'][0].values())

    def test_200(self):
        attrs = {
            'box_id': self.box.box_id,
            'name': 'tst-box-update-new-name',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        resp_json = self.call_route_assert_code(200, attrs)
        self.assert_single_entity(
            resp_json, {
                models.Box.id_name: self.box.box_id,
                'name': attrs['name'],
            },
        )

    def test_400_no_update_properties(self):
        attrs = {
            'box_id': self.box.box_id,
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'No attributes to be updated were provided')

    def test_400_malformed_update_properties(self):
        attrs = {
            'box_id': self.box.box_id,
            'name': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'name was malformed')

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/box/update', data=attrs)


class TestBoxDelete(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.BOX_DELETE
    entity_type = models.Box

    def setUp(self):
        super().setUp()
        attrs = {
            'name': 'tst-box-delete',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        response = self.client.post('/api/box/create', data=attrs)
        self.box = models.Box(*json.loads(response.data)['body'][0].values())
        self.attrs = {
            models.Box.id_name: self.box.box_id,
            auth.API_KEY_NAME: self.superuser.api_key,
        }

    def test_200(self):
        self.test_200_without_verification()
        verify_response = self.client.get(f'/api/box/get/{self.box.box_id}')
        self.assertEqual(verify_response.status_code, 404, 'Retrieved deleted item unexpectedly')

    def test_200_without_verification(self):
        resp_json = self.call_route_assert_code(200, self.attrs)
        self.assert_single_entity(
            resp_json, {
                models.Box.id_name: self.box.box_id,
                'name': self.box.name,
            },
        )

    def test_500_duplicate_id(self):
        self._insert_duplicate_box()
        self.call_route_assert_code(
            500, self.attrs,
            f'Expected 1 item with matching {models.Box.__name__.lower()} ID, got 2',
        )

    def _insert_duplicate_box(self):
        conn = sqlite3.connect(common.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {models.Box.table_name} VALUES ({self.box.to_insert_str()})')
        conn.commit()
        cursor.close()
        conn.close()

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/box/delete', data=attrs)


class TestBoxesList(tstutil.TestBase):
    def _create_n_boxes(self, n: int) -> List[models.Box]:
        boxes = []
        for k in range(n):
            create_attrs = {
                'name': f'tst-box-list-{str(k).zfill(6)}',
                auth.API_KEY_NAME: self.superuser.api_key,
            }
            create_response = self.client.post('/api/box/create', data=create_attrs)
            boxes.append(models.Box(*json.loads(create_response.data)['body'][0].values()))
        return boxes

    def _call_route_assert_limit_offset(self, n: int, limit: int, offset: int, min_: int, max_: int) -> None:
        boxes = self._create_n_boxes(n)
        attrs = {
            'limit': limit,
            'offset': offset,
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        resp_json = self.call_route_assert_code(200, attrs)
        self.assertIn('body', resp_json)
        self.assertIsNotNone(resp_json['body'])

        resp_entities = [models.Box(*entity_json.values()) for entity_json in resp_json['body']]
        self.assertListEqual(resp_entities, boxes[min_:max_])

    def test_200(self):
        limit = 20
        offset = 50
        self._call_route_assert_limit_offset(120, limit, offset, offset, limit + offset)

    def test_200_truncate_end(self):
        limit = 20
        offset = 50
        self._call_route_assert_limit_offset(60, limit, offset, offset, 60)

    def test_200_sortby_desc(self):
        boxes = self._create_n_boxes(20)
        attrs = {
            'sortby': 'name',
            'direction': 'DESC',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        resp_json = self.call_route_assert_code(200, attrs)
        self.assertIn('body', resp_json)
        self.assertIsNotNone(resp_json['body'])

        resp_entities = [models.Box(*entity_json.values()) for entity_json in resp_json['body']]
        desc_sorted_boxes = sorted(boxes, key=lambda box: box.name, reverse=True)
        self.assertListEqual(resp_entities, desc_sorted_boxes)

    def test_400_limit_malformed(self):
        attrs = {
            'limit': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'limit is malformed')

    def test_400_limit_nonpositive(self):
        attrs = {
            'limit': '-1',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, '-1 is not a valid integer limit')

    def test_400_offset_malformed(self):
        attrs = {
            'offset': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'offset is malformed')

    def test_400_offset_nonpositive(self):
        attrs = {
            'offset': '-1',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, '-1 is not a valid integer offset')

    def test_400_direction_malformed(self):
        attrs = {
            'sortby': 'name',
            'direction': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'direction is malformed, should be DESC or ASC')

    def test_400_sortby_malformed(self):
        attrs = {
            'sortby': '*',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'sortby is malformed')

    def test_400_invalid_sort_key(self):
        attrs = {
            'sortby': 'eggplants',
            auth.API_KEY_NAME: self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, 'eggplants is not a valid sort key')

    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/boxes/list?{params}'
        return self.client.get(url)


if __name__ == '__main__':
    unittest.main()
