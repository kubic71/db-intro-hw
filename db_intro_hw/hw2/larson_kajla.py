from db_intro_hw.hw2 import Record
from typing import Tuple, List, Optional



def is_prime(x: int) -> bool:
    for div in range(2, int(x ** 0.5) + 2):
        if x % div == 0:
            return False
    return True


SIGNATURE_PRIME = 7
def compute_signature(key: int, i: int) -> int:
    return (key >> i) % SIGNATURE_PRIME


class Page:
    PAGE_SIZE = 4
    def __init__(self) -> None:

        # page separator
        # this would be stored in our primary memory
        # but for simplicity we keep it in the same 'Page' class
        self.separator = 2**32

        # list of records and their signatures
        self.records: List[Tuple[Record, int]] = []
    
    def find(self, key: int) -> Optional[Record]:
        for r, _ in self.records:
            if r.key == key:
                return r

        return None
    

    @property
    def full(self) -> bool:
        return len(self.records) == Page.PAGE_SIZE


    def insert(self, record: Record, signature: int) -> None:
        assert not self.full
        assert signature < self.separator
        self.records.append((record, signature))



class LarsonKajla:

    def __init__(self, n_pages = 5):
        assert is_prime(n_pages)

        self.n_pages = n_pages
        self.pages: List[Page] = [Page() for i in range(n_pages)]


    def h(self, key: int, i: int) -> int:
        return (key + i) % self.n_pages

    def find(self, key: int) -> Record:
        # we don't know the value of i, so we must just try all of them in the worst case:
        for i in range(0, self.n_pages):
            page = self.pages[self.h(key, i)]
            r = page.find(key)
            if r is not None:
                return r
            print(f"Lookup of {key}, i={i} failed. Trying with {i+1}")
        raise Exception(f"Record with key {key} not found!")

    def insert(self, record: Record) -> None:

        # Insert list of records one by one
        # Each record is tied to parameter 'i', which is to be tried next for it's insertion"""
        records_with_iters: List[Tuple[Record, int]] = [(record, 0)]

        while len(records_with_iters) > 0:

            print("Records to insert:")
            print("\n".join([str(r.key)+ ", i=" + str(i) for r, i in records_with_iters]))


            current, i = records_with_iters.pop()
            assert i < self.n_pages

            page_idx = self.h(current.key, i)
            sig = compute_signature(current.key, i)

            print(f"Trying to insert {current.key} with i={i}, sig={sig} to page {page_idx}")

            page = self.pages[page_idx]
            # we first check the signature with the separator, and only then we fetch the record from secondary memory
            if sig < page.separator:
                print(f"signature fits - {sig} < {page.separator}")
                # Let's pretend that only now we're fetching the page 
                if page.full:
                    print(f"but the page is full. It's separator is {page.separator}")
                    # lower the page separator
                    page.separator = max([s for r, s in page.records])
                    print(f"Lowering in to {page.separator}")

                    # this is naive version of LarsonKajla, where we just take out all the records and re-insert them all again 
                    records_with_iters += [(r, 0) for r, _ in page.records] + [(current, i)]
                    page.records = []
                    
                else:
                    page.insert(current, sig)
            else:
                # let's increase the iteration
                records_with_iters.append((current, i+1))
                

if __name__ == "__main__":
    from db_intro_hw.hw1 import DATA_RECORDS, print_records
    print("Records to insert:\n", "\n".join(list(map(str, DATA_RECORDS))))
    print()
    
    lk = LarsonKajla()
    # Test inserting all records by "age" key

    print("Inserting data records...")
    for rec in DATA_RECORDS:
        lk.insert(Record(rec.age, rec))


    print("\n\nRecords lookup:")
    for rec in DATA_RECORDS:
        print(f"Searching for age={rec.age}")
        print(lk.find(rec.age).data)