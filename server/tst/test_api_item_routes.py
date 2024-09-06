from typing import Dict

import auth
import models
import tstutil


class TestItemCreate(tstutil.TestBase, tstutil.AuthorizedTests):
    scope = auth.Scope.ITEM_CREATE

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/item/create', data=attrs)

# TODO uncomment this when implemented; issue with GET method
# class TestItemGet(tstutil.TestBase, tstutil.IdTests):
#     entity_type = models.Item
#
#     def test_200(self):
#         pass
#
#     def call_route(self, attrs: Dict[str, str]):
#         return self.client.get(f'/api/item/get/{attrs.get("item_id", "")}')


class TestItemUpdate(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.ITEM_UPDATE
    entity_type = models.Item

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/item/update', data=attrs)


class TestItemDelete(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.ITEM_DELETE
    entity_type = models.Item

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/item/delete', data=attrs)


class TestItemsList(tstutil.TestBase):
    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/items/list', data=attrs)


class TestItemsListGET(TestItemsList):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/items/list?{params}'
        return self.client.get(url)
