from __future__ import annotations
from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Sequence


@dataclass
class PersonRecord:
    """Class for keeping track of an item in inventory."""
    id: int
    name: str
    age: int


    def __str__(self):
        return f"id: {self.id:<8}name: {self.name:<15}age:{self.age}"


DATA_RECORDS: Sequence[PersonRecord] = [
    PersonRecord(0, "Marie", 32),
    PersonRecord(1, "Jan", 11),
    PersonRecord(2, "Petr", 26),
    PersonRecord(3, "Pavel", 29),
    PersonRecord(4, "Filip", 36),
    PersonRecord(5, "Karel", 18),
    PersonRecord(6, "Lucie", 3),
    PersonRecord(7, "Jitka", 55),
    PersonRecord(8, "Roman", 78),
    PersonRecord(9, "Vlasta", 27),
    PersonRecord(10, "Marta", 37),
    PersonRecord(11, "Olga", 53),
    PersonRecord(12, "Ivan", 42),
    PersonRecord(13, "Adam", 46),
    PersonRecord(14, "Alice", 61),
    PersonRecord(15, "Igor", 13),
]


def print_records():
    for rec in DATA_RECORDS:
        print(rec)


if __name__ == "__main__":
    print_records()