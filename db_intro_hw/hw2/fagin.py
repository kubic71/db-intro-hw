from typing import List, Any
from db_intro_hw.hw2 import Record
from db_intro_hw.hw1 import DATA_RECORDS


def LSB(n: int, k: int):
    """return first k least-significant bits"""
    return (2**k - 1) & n



class Page:
    PAGE_SIZE = 3

    def __init__(self, local_depth: int = 0):
        self.local_depth = local_depth
        self.data: List[Record] = []

    @property
    def full(self) -> bool:
        return len(self.data) == Page.PAGE_SIZE

    def insert(self, record: Record) -> None:
        assert not self.full
        self.data.append(record)

    def find(self, key: int) -> Record:
        # just linear-scan through the page, which would be loaded into primary memory, so it would be cheap
        # TODO: what about collisions?

        for rec in self.data:
            if key == rec.key:
                return rec
        raise Exception(f"No record with key={key} found in page with local_depth={self.local_depth}")


class Fagin:
    def __init__(self):
        # we start with only one pointer
        self.global_depth = 0

        # to an empty page
        self.pointers = [Page(0)]
    

    def split(self, index: int) -> None:
        old_page = self.pointers[index]
        new_depth = old_page.local_depth + 1
        p1, p2 = Page(new_depth), Page(new_depth)


        # update pointers that point to the old_page
        for i in range(len(self.pointers)):
            if id(self.pointers[i]) == id(old_page):
                if i & (2**old_page.local_depth) == 0:
                    self.pointers[i] = p1
                else:
                    self.pointers[i] = p2


        # re-insert the records back in the hashtable
        self.insert(old_page.data)


    def find(self, key: int) -> Record:
        page = self.pointers[self.get_hash(key)]
        return page.find(key)

    
    def insert(self, records: List[Record]) -> None:
        for rec in records:

            h = self.get_hash(rec.key)

            page = self.pointers[h]
            if page.full:
                if page.local_depth < self.global_depth:
                    # split the page
                    self.split(h)

                    # and try again
                    self.insert([rec])

                else:
                    # increase global depth and copy references
                    self.pointers = self.pointers + self.pointers
                    self.global_depth += 1

                    # try again
                    self.insert([rec])

            else:
                page.insert(rec)


    def get_hash(self, key: int) -> int:
        # first 'global_depth' least significant bits
        return LSB(key, self.global_depth)


if __name__ == "__main__":

    from db_intro_hw.hw1 import DATA_RECORDS, print_records
    print("Records to insert:\n", "\n".join(list(map(str, DATA_RECORDS))))
    print()


    fagin = Fagin()
    print("Inserting data records...")
    for rec in DATA_RECORDS:
        print("Inserting: ", rec)
        fagin.insert([Record(rec.age, rec)])

    print("\n\nRecords lookup:")
    for rec in DATA_RECORDS:
        print(f"Searching for age={rec.age}")
        print(fagin.find(rec.age).data)