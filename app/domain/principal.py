"""Identitas dan role pengguna hasil autentikasi."""
from dataclasses import dataclass
from typing import Literal

Role = Literal["ADMIN", "STAFF"]

@dataclass(frozen=True, slots=True)
class Principal:
    role: Role
