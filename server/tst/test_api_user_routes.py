from typing import Dict

import auth
import models
import tstutil
from identifier import Identifier


class TestUserCreate(tstutil.TestBase, tstutil.AuthorizedTests):
    scope = auth.Scope.USER_CREATE

    def test_200(self):
        attrs = {
            auth.API_KEY_NAME: self.superuser.api_key,
            'name': 'tst-user-create',
            'authmask': tstutil.max_authmask(),
        }
        resp_json = self.call_route_assert_code(200, attrs)
        entity_json = self.assert_single_entity(
            resp_json, {
                'name': attrs['name'],
            },
        )
        self.assertIsNotNone(Identifier(length=models.User.id_length, id_=entity_json[models.User.id_name]))

    def test_400_no_name(self):
        pass

    def test_400_malformed_name(self):
        pass

    def test_400_duplicate_name(self):
        pass

    def test_400_no_authmask(self):
        pass

    def test_400_malformed_authmask(self):
        pass

    def test_400_noninteger_authmask(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/create', data=attrs)


class TestUserGet(tstutil.TestBase, tstutil.IdTests):
    entity_type = models.User

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/get', data=attrs)


class TestUserUpdate(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.USER_UPDATE
    entity_type = models.User

    def test_200(self):
        pass

    def test_400_no_update_properties(self):
        pass

    def test_400_malformed_update_properties(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_500_duplicate_id(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/update', data=attrs)


class TestUserDelete(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.USER_DELETE
    entity_type = models.User

    def test_200(self):
        pass

    def test_200_without_verification(self):
        pass

    def test_500_duplicate_id(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/delete', data=attrs)
