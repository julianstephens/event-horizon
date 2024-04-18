import contextlib

import bcrypt
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.ext.mutable import Mutable


class PasswordHash(Mutable):
    def __init__(self, hash_, rounds=None):
        assert len(hash_) >= 60, "bcrypt hash should be at least 60 chars."
        if isinstance(hash_, bytes):
            assert (
                hash_.decode("utf-8").count("$") == 3
            ), 'bcrypt hash should have 3x "$".'
        else:
            assert hash_.count("$") == 3, 'bcrypt hash should have 3x "$".'
        self.hash = str(hash_)
        self.rounds = int(self.hash.split("$")[2])
        self.desired_rounds = rounds or self.rounds

    def __eq__(self, candidate):
        """Hashes the candidate string and compares it to the stored hash.

        If the current and desired number of rounds differ, the password is
        re-hashed with the desired number of rounds and updated with the results.
        This will also mark the object as having changed (and thus need updating).
        """
        with contextlib.suppress(Exception):
            candidate = candidate.encode("utf8")
            if isinstance(self.hash, bytes) and self.hash == bcrypt.hashpw(
                candidate, self.hash
            ):
                if self.rounds < self.desired_rounds:
                    self._rehash(candidate)
                return True
        return False

    def __repr__(self):
        """Simple object representation."""
        return "<{}>".format(type(self).__name__)

    @classmethod
    def coerce(cls, key, value):
        """Ensure that loaded values are PasswordHashes."""
        if isinstance(value, PasswordHash):
            return value
        return super(PasswordHash, cls).coerce(key, value)

    @classmethod
    def new(cls, password, rounds):
        """Returns a new PasswordHash object for the given password and rounds."""
        with contextlib.suppress(Exception):
            password = password.encode("utf8")
        return cls(cls._new(password, rounds))

    @staticmethod
    def _new(password, rounds):
        """Returns a new bcrypt hash for the given password and rounds."""
        return bcrypt.hashpw(password, bcrypt.gensalt(rounds))

    def _rehash(self, password):
        """Recreates the internal hash and marks the object as changed."""
        self.hash = self._new(password, self.desired_rounds)
        self.rounds = self.desired_rounds
        self.changed()


class Password(TypeDecorator):
    """Allows storing and retrieving password hashes using PasswordHash."""

    impl = Text

    def __init__(self, rounds=12, **kwds):
        self.rounds = rounds
        super(Password, self).__init__(**kwds)

    def process_bind_param(self, value, dialect):
        """Ensure the value is a PasswordHash and then return its hash."""
        return self._convert(value).hash  # type: ignore

    def process_result_value(self, value, dialect):
        """Convert the hash to a PasswordHash, if it's non-NULL."""
        if value is not None:
            return PasswordHash(value, rounds=self.rounds)

    def validator(self, password):
        """Provides a validator/converter for @validates usage."""
        if len(password) < 8 or len(password) > 24:
            raise ValueError("Password must be between 8 and 24 characters.")
        elif not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        elif not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        elif not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        elif not any(char in "!@#$%^&*()-+" for char in password):
            raise ValueError("Password must contain at least one special character.")

        return self._convert(password)

    def _convert(self, value):
        """Returns a PasswordHash from the given string.

        PasswordHash instances or None values will return unchanged.
        Strings will be hashed and the resulting PasswordHash returned.
        Any other input will result in a TypeError.
        """
        if isinstance(value, PasswordHash):
            return value
        elif isinstance(value, str):
            return PasswordHash.new(value, self.rounds)
        elif value is not None:
            raise TypeError("Cannot convert {} to a PasswordHash".format(type(value)))
