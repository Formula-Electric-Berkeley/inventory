from typing import Dict

import auth
import models
import tstutil


class TestUserCreate(tstutil.TestBase, tstutil.AuthorizedTests):
    scope = auth.Scope.USER_CREATE

    def test_200(self):
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

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/update', data=attrs)


class TestUserDelete(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.USER_DELETE
    entity_type = models.User

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/user/delete', data=attrs)


class TestUsersList(tstutil.TestBase):
    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/users/list', data=attrs)


class TestUsersListGET(TestUsersList):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/users/list?{params}'
        return self.client.get(url)
