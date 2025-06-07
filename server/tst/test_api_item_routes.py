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


class ItemGetTestBase(tstutil.IdTests):
    entity_type = models.Item

    def test_200(self):
        # TODO implement
        pass


class TestItemGetDynamicGET(ItemGetTestBase, tstutil.TestBase):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/item/get?{params}'
        return self.client.get(url)


class TestItemGetStaticGET(ItemGetTestBase, tstutil.TestBase):
    def test_400_no_id(self):
        # Static route requires an ID by definition
        pass

    def call_route(self, attrs: Dict[str, str]):
        url = f'/api/item/get/{attrs[models.Item.id_name]}'
        return self.client.get(url)


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
