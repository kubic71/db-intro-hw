from typing import List, Any, Iterator
from dataclasses import dataclass
from db_intro_hw.hw2 import Record
from db_intro_hw.hw1 import DATA_RECORDS


class Page:
    PAGE_SIZE = 3

    def __init__(self):
        self.data: List[Record]  = []

    @property
    def full(self) -> bool:
        return len(self.data) == Page.PAGE_SIZE

    def __repr__(self):
        if self.data == []:
            return "--Empty Page--"

        s =  []
        for rec in self.data:
            s.append(str(rec.key))

        return "[ " + " | ".join(s) + "]"
    
    def __str__(self):
        return self.__repr__()


class Bucket:

    def __init__(self):
        self.page_chain: List[Page] = [Page()]


    def insert(self, record: Record) -> bool:
        """Inserts record into bucket and returns True when bucket overflows"""

        if self.page_chain[-1].full:
            # generate new overflow page
            self.page_chain.append(Page())
            self.page_chain[-1].data.append(record)
            return True
        else:
            self.page_chain[-1].data.append(record)
            return False
        

    def find(self, key: int) -> Record:
        for page in self.page_chain:
            for rec in page.data:
                if rec.key == key:
                    return rec

        raise Exception(f"No record with key {key} found!")

    def get_all(self) -> Iterator[Record]:
        for page in self.page_chain:
            for rec in page.data:
                yield rec

    
    def __repr__(self):
        s = []
        for i, page in enumerate(self.page_chain):
            s.append(f"\tPage {i}: {page}")
        
        return "\n" .join(s)

    def __str__(self):
        return self.__repr__()


class LinearHashing:

    def __init__(self):
        # defines domains of h1 and h2
        self.m = 1
        self.p = 0

        self.buckets = [Bucket()]

    def h1(self, key: int) -> int:
        return key % (2**self.m)

    def h2(self, key: int) -> int:
        return key % (2**(self.m + 1))

    def h(self, key: int) -> int:
        hash_val = self.h1(key)
        if hash_val < self.p:
            return self.h2(key)
        return hash_val

    def inc_p(self):
        self.p += 1
        if self.p % (2**self.m) == 0:
            self.p = 0
            self.m += 1

    def __repr__(self):
        s = [f"Hashtable state: p={self.p}, m={self.m}"]
        for i, buck in enumerate(self.buckets):
            s.append(f"Bucket {i}: {buck}")

        return "\n".join(s) + "\n"


    def split(self):
        records_to_reinsert = list(self.buckets[self.p].get_all())
        print("Reinserting following records:", records_to_reinsert)

        self.buckets[self.p] = Bucket()
        self.inc_p()

        for rec in records_to_reinsert:
            self.insert(rec)
    
    def insert(self, record: Record):
        print("State before insert:")
        print(str(self))

        bucket_idx = self.h(record.key)
        if len(self.buckets) <= bucket_idx:
            for i in range(bucket_idx - len(self.buckets) + 1):
                self.buckets.append(Bucket())
        
        overflow = self.buckets[bucket_idx].insert(record)

        # overflow triggers bucket splitting
        if overflow:
            print(f"Overflow of bucket {bucket_idx} triggerd split!")
            self.split()
        



    def find(self, key: int) -> Record:
        return self.buckets[self.h(key)].find(key)


if __name__ == "__main__":

    from db_intro_hw.hw1 import DATA_RECORDS, print_records
    print("Records to insert:\n", "\n".join(list(map(str, DATA_RECORDS))))
    print()


    lin_hashing = LinearHashing()
    print("Inserting data records...")

    for rec in DATA_RECORDS:
        print("Inserting: ", rec)
        lin_hashing.insert(Record(rec.age, rec))



    print("\n\nRecords lookup:")
    for rec in DATA_RECORDS:
        print(f"Searching for age={rec.age}")
        print(lin_hashing.find(rec.age).data)