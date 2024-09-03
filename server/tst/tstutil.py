import json
import secrets
import sqlite3
import unittest
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

import auth
import common
import db
import models
import wsgi
from identifier import Identifier


class TestBase(unittest.TestCase):
    def setUp(self):
        self.ctx = wsgi.app.app_context()
        self.ctx.push()
        self.client = wsgi.app.test_client()
        drop_all_tables()
        wsgi._create_tables()
        self.superuser = create_user()

    def tearDown(self):
        self.ctx.pop()
        # Drop tables in setUp so output is preserved for analysis

    def call_route_assert_code(self, status_code: int, attrs: Optional[Dict[str, Any]] = None, err_msg: str = None):
        resp = self.call_route(attrs)
        self.assertEqual(status_code, resp.status_code, resp.data)
        resp_json = json.loads(resp.data)
        self.assertIsNotNone(resp_json)
        self.assertIn('code', resp_json)
        self.assertEqual(status_code, resp_json['code'])
        if status_code != 200 and err_msg is not None:
            self.assertIn('body', resp_json)
            self.assertEqual(1, len(resp_json['body']))
            err_json = resp_json['body'][0]
            self.assertIn('description', err_json)
            self.assertEqual(err_msg, err_json['description'])
        return resp_json

    def assert_single_entity(self, resp_json, expected: Dict[str, str]):
        self.assertIn('body', resp_json)
        self.assertIsNotNone(resp_json['body'])
        self.assertEqual(1, len(resp_json['body']))
        entity_json = resp_json['body'][0]
        self.assertIsNotNone(entity_json)
        for key in expected.keys():
            self.assertIn(key, entity_json)
            self.assertEqual(expected[key], entity_json[key])
        return entity_json

    def test_200(self):
        raise NotImplementedError()

    def call_route(self, attrs: Dict[str, str]):
        raise NotImplementedError()


class AuthorizedTests:
    def test_400_no_apikey(self):
        attrs = {}
        self.call_route_assert_code(400, attrs, 'API key was not present')

    def test_400_malformed_apikey(self):
        attrs = {
            'api_key': '*',
        }
        self.call_route_assert_code(400, attrs, 'API key was malformed')

    def test_401_user_not_found(self):
        attrs = {
            'api_key': 'nonexistent-user',
        }
        self.call_route_assert_code(401, attrs, 'User was not found')

    def test_403_user_unauthorized(self):
        all_scopes = list(auth.Scope.__members__.keys())
        all_scopes.remove(self.scope.name)
        for scope_str in all_scopes:
            scope = auth.Scope[scope_str]
            attrs = {
                'api_key': create_user(scope).api_key,
            }
            self.call_route_assert_code(403, attrs, 'User was not authorized to access this resource')

    @classmethod
    def scope(cls) -> auth.Scope:
        raise NotImplementedError()


class IdTests:
    def test_400_malformed_id(self):
        attrs = {
            self.entity_type.id_name: '*',
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, f'{self.entity_type.id_name} was malformed')

    def test_400_no_id(self):
        attrs = {
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(400, attrs, f'{self.entity_type.id_name} was not found in request')

    def test_404_nonexistent_entity(self):
        entity_name = self.entity_type.__name__
        attrs = {
            self.entity_type.id_name: Identifier(length=self.entity_type.id_length),
            'api_key': self.superuser.api_key,
        }
        self.call_route_assert_code(404, attrs, f'{entity_name} does not exist')

    @classmethod
    def entity_type(cls) -> Type[models.Model]:
        raise NotImplementedError()


def drop_all_tables() -> None:
    conn = sqlite3.connect(common.DATABASE_PATH)
    cursor = conn.cursor()
    for entity_type in (models.Item, models.User, models.Reservation, models.Box):
        cursor.execute(f'DROP TABLE IF EXISTS {entity_type.table_name}')
    conn.commit()
    cursor.close()
    conn.close()


def create_user(scope: Optional[auth.Scope] = None) -> models.User:
    authmask = ((0b1 << len(auth.Scope)) - 1) if scope is None else scope.value
    scope_name = 'superuser' if scope is None else scope.name
    user = models.User(
        user_id=Identifier(length=models.User.id_length),
        api_key=secrets.token_hex(),
        name=f'testing-user-{scope_name}',
        authmask=authmask,
    )
    conn, cursor = common.get_db_connection()
    db.create_entity(conn, cursor, user)
    return user
