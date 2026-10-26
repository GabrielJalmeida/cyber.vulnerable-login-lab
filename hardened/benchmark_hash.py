"""Optional local benchmark for the configured Argon2id password profile."""

from __future__ import annotations

import secrets
from statistics import mean
from time import perf_counter

from app.security.passwords import hash_password, verify_password


def timed_samples(operation, repetitions: int = 5) -> list[float]:
    samples = []
    for _ in range(repetitions):
        started = perf_counter()
        operation()
        samples.append((perf_counter() - started) * 1000)
    return samples


def main() -> None:
    synthetic_password = secrets.token_urlsafe(24)
    print("Benchmark local de Argon2id; senha e hashes não serão exibidos.")
    encoded_hash = hash_password(synthetic_password)
    hash_samples = timed_samples(lambda: hash_password(synthetic_password))
    verify_samples = timed_samples(
        lambda: verify_password(encoded_hash, synthetic_password)
    )
    print(f"Geração: mediana {sorted(hash_samples)[len(hash_samples) // 2]:.1f} ms; média {mean(hash_samples):.1f} ms")
    print(f"Verificação: mediana {sorted(verify_samples)[len(verify_samples) // 2]:.1f} ms; média {mean(verify_samples):.1f} ms")
    print("Amostras: 5 gerações e 5 verificações. Faça a medição no computador-alvo.")


if __name__ == "__main__":
    main()
