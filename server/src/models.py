import inspect
from typing import Any
from typing import Type

import common
from identifier import Identifier


class Model:
    def to_dict(self) -> dict[str, Any]:
        # TODO documentation
        return vars(self)

    def to_response(self) -> dict[str, Any]:
        # TODO documentation
        return common.create_response(200, self.to_dict())

    def to_insert_str(self) -> str:
        # TODO documentation
        model_values = [f"'{v}'" for v in self.to_dict().values()]
        return ', '.join(model_values)

    def __str__(self) -> str:
        # TODO documentation
        return self.to_insert_str()

    def __iter__(self):
        # TODO documentation
        for v in self.to_dict().values():
            yield v

    @classmethod
    def id_name(cls) -> str:
        # TODO documentation
        raise NotImplementedError('ID name not implemented')

    @classmethod
    def id_length(cls) -> int:
        # TODO documentation
        raise NotImplementedError('ID length not implemented')

    @classmethod
    def table_name(cls) -> str:
        # TODO documentation
        raise NotImplementedError('Table name not implemented')


class Item(Model):
    """Represents a single inventory item in the database."""
    id_name = 'item_id'
    id_length = 8
    table_name = 'items'

    def __init__(
        self, item_id: Identifier, box_id: Identifier, mfg_part_number: str, quantity: int,
        description: str, digikey_part_number: str, mouser_part_number: str, jlcpcb_part_number: str,
        created_by: Identifier, created_epoch_millis: int,
    ):
        super().__init__()
        self.item_id = Identifier(length=Item.id_length, id_=item_id)
        self.box_id = Identifier(length=Box.id_length, id_=box_id)
        self.mfg_part_number = mfg_part_number
        self.quantity = quantity
        self.description = description
        self.digikey_part_number = digikey_part_number
        self.mouser_part_number = mouser_part_number
        self.jlcpcb_part_number = jlcpcb_part_number
        self.created_by = Identifier(length=User.id_length, id_=created_by)
        self.created_epoch_millis = created_epoch_millis


class User(Model):
    """Represents a single user in the database."""
    id_name = 'user_id'
    id_length = 32
    table_name = 'users'

    def __init__(self, user_id: Identifier, api_key: str, name: str, authmask: int):
        super().__init__()
        self.user_id = Identifier(length=User.id_length, id_=user_id)
        self.api_key = api_key
        self.name = name
        self.authmask = authmask


class Reservation(Model):
    """Represents a single reservation in the database."""
    id_name = 'reservation_id'
    id_length = 32
    table_name = 'reservations'

    def __init__(self, reservation_id: Identifier, user_id: Identifier, item_id: Identifier, quantity: int):
        super().__init__()
        self.reservation_id = Identifier(length=Reservation.id_length, id_=reservation_id)
        self.user_id = Identifier(length=User.id_length, id_=user_id)
        self.item_id = Identifier(length=Item.id_length, id_=item_id)
        self.quantity = int(quantity)


class Box(Model):
    """Represents a single inventory box (not inventory item container) in the database."""
    id_name = 'box_id'
    id_length = 8
    table_name = 'boxes'

    def __init__(self, box_id: Identifier, name: str):
        self.box_id = Identifier(length=Box.id_length, id_=box_id)
        self.name = name


def get_entity_parameters(entity_type: Type[Model]) -> dict[str, Any]:
    raw_params = inspect.signature(entity_type.__init__).parameters
    dict_params = dict(raw_params)
    dict_params.pop('self')
    return dict_params
