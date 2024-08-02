import typing


class Model:
    def to_insert_str(self) -> str:
        model_values = [f"'{v}'" for v in vars(self).values()]
        return ", ".join(model_values)

    def to_dict(self) -> dict[str, str]:
        return vars(self)

    def __str__(self) -> str:
        return self.to_insert_str()


class Item(Model):
    def __init__(self, item_id: str, mfg_part_number: str, quantity: typing.Union[int, str],
                 description: str, digikey_part_number: str, mouser_part_number: str, jlcpcb_part_number,
                 created_by: str, created_epoch_millis: typing.Union[int, str]):
        super().__init__()
        self.item_id = item_id
        self.mfg_part_number = mfg_part_number
        self.quantity = int(quantity)
        self.description = description
        self.digikey_part_number = digikey_part_number
        self.mouser_part_number = mouser_part_number
        self.jlcpcb_part_number = jlcpcb_part_number
        self.created_by = created_by
        self.created_epoch_millis = int(created_epoch_millis)


class User(Model):
    def __init__(self, user_id: str, api_key: str, name: str, authmask: str):
        self.user_id = user_id
        self.api_key = api_key
        self.name = name
        self.authmask = int(authmask)


class Reservation(Model):
    def __init__(self, reservation_id: str, user_id: str, item_id: str, quantity: str):
        super().__init__()
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.item_id = item_id
        self.quantity = int(quantity)


BLANK_ITEM = Item(*[str('0')]*9)
BLANK_USER = User(*[str('0')]*4)
BLANK_RESERVATION = Reservation(*[str('0')]*4)
