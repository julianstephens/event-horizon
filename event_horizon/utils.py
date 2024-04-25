from uuid import UUID

from argon2 import PasswordHasher
from sqlalchemy.ext.mutable import Mutable


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


class PasswordHash(Mutable):
    def __init__(self, hash: str) -> None:
        self.ph = PasswordHasher()
        self.hash = hash

    def __eq__(self, value: str) -> bool:
        try:
            self.ph.verify(self.hash, value)
            if self.ph.check_needs_rehash(self.hash):
                self.changed()
            return True
        except Exception:
            pass

        return False

    @classmethod
    def new(cls, password: str):
        ph = PasswordHasher()
        return cls(ph.hash(password))


def generate_links(rel: str, hrefs: list[str]):
    links = []
    for h in hrefs:
        links.append({"rel": rel, "href": h})

    return links
