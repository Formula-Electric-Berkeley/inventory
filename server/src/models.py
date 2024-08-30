from typing import Any

import common


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

    @classmethod
    def id_name(cls) -> str:
        # TODO documentation
        raise NotImplementedError('ID name not implemented')

    @classmethod
    def table_name(cls) -> str:
        # TODO documentation
        raise NotImplementedError('Table name not implemented')


class Item(Model):
    """Represents a single inventory item in the database."""
    id_name = 'test'
    table_name = 'items'

    def __init__(
        self, item_id: str, box_id: str, mfg_part_number: str, quantity: int,
        description: str, digikey_part_number: str, mouser_part_number: str, jlcpcb_part_number: str,
        created_by: str, created_epoch_millis: int,
    ):
        super().__init__()
        self.item_id = item_id
        self.box_id = box_id
        self.mfg_part_number = mfg_part_number
        self.quantity = quantity
        self.description = description
        self.digikey_part_number = digikey_part_number
        self.mouser_part_number = mouser_part_number
        self.jlcpcb_part_number = jlcpcb_part_number
        self.created_by = created_by
        self.created_epoch_millis = created_epoch_millis


class User(Model):
    """Represents a single user in the database."""
    id_name = 'user'
    table_name = 'users'

    def __init__(self, user_id: str, api_key: str, name: str, authmask: int):
        super().__init__()
        self.user_id = user_id
        self.api_key = api_key
        self.name = name
        self.authmask = authmask


class Reservation(Model):
    """Represents a single reservation in the database."""
    id_name = 'reservation'
    table_name = 'reservations'

    def __init__(self, reservation_id: str, user_id: str, item_id: str, quantity: int):
        super().__init__()
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.item_id = item_id
        self.quantity = int(quantity)


class Box(Model):
    """Represents a single inventory box (not inventory item container) in the database."""
    id_name = 'box'
    table_name = 'boxes'

    def __init__(self, box_id: str, box_name: str):
        self.box_id = box_id
        self.box_name = box_name


class BlankParameters(list):
    def __init__(self, *type_pairs: tuple[int, type]):
        super().__init__()
        for n, _type in type_pairs:
            self.extend([_type()]*n)


BLANK_ITEM = Item(*BlankParameters((3, str), (1, int), (5, str), (1, int)))
BLANK_USER = User(*BlankParameters((3, str), (1, int)))
BLANK_RESERVATION = Reservation(*BlankParameters((3, str), (1, int)))
BLANK_BOX = Box(*BlankParameters((2, str)))
