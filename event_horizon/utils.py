from argon2 import PasswordHasher
from sqlalchemy.ext.mutable import Mutable


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
        except Exception as ex:
            print(ex)
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
