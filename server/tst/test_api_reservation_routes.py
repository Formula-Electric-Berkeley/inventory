from typing import Dict

import auth
import models
import tstutil


class TestReservationCreate(tstutil.TestBase, tstutil.AuthorizedTests):
    scope = auth.Scope.RESERVATION_CREATE

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/reservation/create', data=attrs)


class ReservationGetTestBase(tstutil.IdTests):
    entity_type = models.Reservation

    def test_200(self):
        # TODO implement
        pass


class TestReservationGetDynamicGET(ReservationGetTestBase, tstutil.TestBase):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/reservation/get?{params}'
        return self.client.get(url)


class TestReservationGetStaticGET(ReservationGetTestBase, tstutil.TestBase):
    def test_400_no_id(self):
        # Static route requires an ID by definition
        pass

    def call_route(self, attrs: Dict[str, str]):
        url = f'/api/reservation/get/{attrs[models.Reservation.id_name]}'
        return self.client.get(url)


class TestReservationUpdate(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.RESERVATION_UPDATE
    entity_type = models.Reservation

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/reservation/update', data=attrs)


class TestReservationDelete(tstutil.TestBase, tstutil.AuthorizedTests, tstutil.IdTests):
    scope = auth.Scope.RESERVATION_DELETE
    entity_type = models.Reservation

    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/reservation/delete', data=attrs)


class TestReservationsList(tstutil.TestBase):
    def test_200(self):
        pass

    def call_route(self, attrs: Dict[str, str]):
        return self.client.post('/api/reservations/list', data=attrs)


class TestReservationsListGET(TestReservationsList):
    def call_route(self, attrs: Dict[str, str]):
        params = tstutil.attrs_to_params(attrs)
        url = f'/api/reservations/list?{params}'
        return self.client.get(url)
