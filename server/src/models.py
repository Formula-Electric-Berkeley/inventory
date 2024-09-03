import inspect
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import common
from identifier import Identifier


class Model:
    def to_dict(self) -> Dict[str, Any]:
        # TODO documentation
        return vars(self)

    def to_response(self) -> Dict[str, Any]:
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


class EntityCacheKey:
    def __init__(self, direction: str, sortby: Optional[str], entity_type: Type[Model], ttl_sec: int = 3600):
        self.direction = direction
        self.sortby = sortby
        self.entity_type = entity_type
        self.expiry_time = int(time.time()) + ttl_sec

    def __eq__(self, other):
        # Ignore expiry time in equality comparisons
        return isinstance(other, EntityCacheKey) \
            and (self.sortby is other.sortby) \
            and (self.entity_type is other.entity_type)

    def __hash__(self):
        return hash((self.sortby, self.entity_type))


class EntityCache:
    def __init__(self):
        self._map: Dict[EntityCacheKey, List[Model]] = {}

    def add(self, key: EntityCacheKey, entities: List[Model]) -> None:
        if len(entities) > 0:
            self._map[key] = entities

    def get(self, key: EntityCacheKey) -> Optional[List[Model]]:
        for k in self._map.copy():
            if k.expiry_time > time.time():
                self._map.pop(k)
                continue
            if key is k:
                return self._map[k]
        return None

    @staticmethod
    def cut(entities: List[Model], limit: int, offset: int):
        start_idx = max(min(offset, len(entities)), 0)
        end_idx = min(offset + limit, len(entities))
        return entities[start_idx:end_idx]


def get_entity_parameters(entity_type: Type[Model]) -> Dict[str, Any]:
    raw_params = inspect.signature(entity_type.__init__).parameters
    dict_params = dict(raw_params)
    dict_params.pop('self')
    return dict_params
