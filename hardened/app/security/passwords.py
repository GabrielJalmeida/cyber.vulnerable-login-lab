"""Password hashing and verification for the synthetic local lab account."""

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError, VerifyMismatchError

# OWASP's recommended minimum Argon2id profile: 19 MiB memory, 2 iterations,
# and one lane. Benchmark on the machine that will run the lab before adapting.
PASSWORD_HASHER = PasswordHasher(
    time_cost=2,
    memory_cost=19_456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


class PasswordHashConfigurationError(Exception):
    """Raised when the configured stored password hash cannot be verified."""


def hash_password(password: str) -> str:
    """Return an Argon2id hash. The plaintext is never persisted by this helper."""
    if not isinstance(password, str) or not password:
        raise ValueError("A non-empty password is required.")
    return PASSWORD_HASHER.hash(password)


def verify_password(encoded_hash: str, password: str) -> bool:
    """Verify a password, separating mismatch from a malformed hash setting."""
    try:
        return PASSWORD_HASHER.verify(encoded_hash, password)
    except VerifyMismatchError:
        return False
    except (VerificationError, ValueError) as exc:
        raise PasswordHashConfigurationError from exc
