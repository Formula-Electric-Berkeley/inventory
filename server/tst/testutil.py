import json
import secrets
import sqlite3
import unittest
from typing import Any
from typing import Optional

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
        wsgi.create_tables()
        self.superuser = create_user()

    def tearDown(self):
        self.ctx.pop()
        # Drop tables in setUp so output is preserved for analysis

    def call_route_assert_code(self, status_code: int, attrs: Optional[dict[str, Any]] = None):
        resp = self.call_route(attrs)
        self.assertEqual(status_code, resp.status_code, resp.data)
        resp_json = json.loads(resp.data)
        self.assertIsNotNone(resp_json)
        self.assertIn('code', resp_json)
        self.assertEqual(status_code, resp_json['code'])
        return resp_json

    def test_400_no_apikey(self):
        attrs = {}
        self.call_route_assert_code(400, attrs)

    def test_400_malformed_apikey(self):
        attrs = {
            'api_key': '*',
        }
        self.call_route_assert_code(400, attrs)

    def test_401_user_not_found(self):
        attrs = {
            'api_key': 'nonexistent-user',
        }
        self.call_route_assert_code(401, attrs)

    def test_403_user_unauthorized(self):
        all_scopes = auth.Scope._member_names_
        all_scopes.remove(self.scope.name)
        for scope_str in all_scopes:
            scope = auth.Scope[scope_str]
            attrs = {
                'api_key': create_user(scope).api_key,
            }
            self.call_route_assert_code(403, attrs)

    def call_route(self, attrs: dict[str, str]):
        raise NotImplementedError()

    @classmethod
    def scope(cls) -> auth.Scope:
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
