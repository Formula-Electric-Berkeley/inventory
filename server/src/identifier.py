import re
import secrets
import string
from typing import Optional
from typing import Union

import flask
# Increase the probability of getting a digit (otherwise few digits appear)

_alphabet = string.ascii_lowercase + (string.digits * 2)


class IdInitializerError(ValueError):
    def __init__(self, msg: str):
        if flask.has_request_context():
            flask.abort(500, msg)
        else:
            super().__init__(msg)


class Identifier(str):
    def __new__(cls, length: int = 32, id_: Optional[Union[str, 'Identifier']] = None):
        formed_id = ''.join(secrets.choice(_alphabet) for _ in range(length)) if id_ is None else id_
        inst = super(Identifier, cls).__new__(cls, formed_id)

        if length <= 0:
            raise IdInitializerError(f'ID length {length} was not > 0')
        if len(inst) != length:
            raise IdInitializerError(f'ID {inst} has length {len(inst)}, expected {length}')
        match = re.fullmatch(fr'[A-Za-z0-9]{{{length}}}', inst)
        if match is None:
            raise IdInitializerError(f'ID {inst} contains invalid characters')

        return inst
