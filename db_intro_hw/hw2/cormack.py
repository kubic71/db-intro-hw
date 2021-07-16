from typing import Any, Iterator, List, Tuple
from dataclasses import dataclass



DIRECTORY_SIZE = 7
PRIM_FILE_SIZE = 100



def h(k: int):
    k % DIRECTORY_SIZE


@dataclass
class PrimaryFileRecord:
    """Our data record saved in primary file"""

    # key, which is an output of some generic hash function
    # it may have collissions across our data, but Cormack handles that
    key: int

    # data payload
    data: Any

@dataclass
class Bucket:
    i: int
    r: int
    p: int

class Cormack:
    def __init__(self, directory_size=7, primary_file_size=100):
        self.directory_size = directory_size
        self.primary_file_size = primary_file_size
        
        self.directory: List[Bucket] = [None] * DIRECTORY_SIZE
        self.primary_file: List[PrimaryFileRecord] = [None] * PRIM_FILE_SIZE

        # Ptr to primary file, after which there is free space
        # we don't reuse space for simplicity
        self.free_space_ptr = 0

    def h(self, key: int) -> int:
        """Returns position of data record with key 'k' within the directory"""
        return key % self.directory_size

    def h_i(self, k: int, i: int, r: int) -> int:
        return (k >> i) % r

    def get_records_in_bucket(self, dir_pos: int) -> Iterator[PrimaryFileRecord]:
        bucket = self.directory[dir_pos]

        for r_i in range(bucket.r):
            ptr = r_i + bucket.p
            if self.primary_file[ptr] is not None:
                yield self.primary_file[ptr]
    
    
    # def insert_into_primary_file(self, records: List[PrimaryFileRecord], offset: int):
        # for i, rec in records:
            # self.primary_file[i + offset] = 
        
    def find_perfect_hashing_fn(self, records: List[PrimaryFileRecord]) -> Tuple[int, int]:
        """Finds (i,r), such that h_i(record.key, i, r) don't collide"""

        # always start with r == number of records to perfect-hash
        r = len(records)
        i = 0

        while True:
            hashes = [self.h_i(rec.key, i, r)  for rec in records]
            unique_vals = set(hashes)
            if len(unique_vals) == len(records):
                # we found the right i,r
                return (i, r)
            elif hashes.count(0) > 1:
                # no need to bit-shift further
                r += 1
                i = 0
            else:
                # collision, but we can try to bit-shift more
                i += 1
    
    def get_primary_file_ptr(self, key: int) -> int:
        bucket = self.directory[self.h(key)]
        return self.h_i(key, bucket.i, bucket.r) + bucket.p

    def lookup(self, key: int) -> PrimaryFileRecord:
        return self.primary_file[self.get_primary_file_ptr(key)]

    def insert(self, record: PrimaryFileRecord) -> None:
        """inserts data record into primary file based on it's hash key"""

        dir_pos = self.h(record.key)
        bucket = self.directory[dir_pos]

        # if the bucket is empty
        if bucket is None:
            # There is no collision and we can happily insert the datarecord
            print(f"inserting {record} into free bucket")
            self.directory[dir_pos] = Bucket(0, 1, self.free_space_ptr)
            self.primary_file[self.free_space_ptr] = record

            assert self.free_space_ptr == self.get_primary_file_ptr(record.key)

            self.free_space_ptr += 1


        elif self.get_primary_file_ptr(record.key) is None:
            # there is still free space we can use

            new_pos = self.get_primary_file_ptr(record.key)
            print(f"inserting {record.key} to free space in a bucket at {new_pos}")
            self.primary_file[new_pos] = record



        else:
            records_to_insert = [record] + list(self.get_records_in_bucket(dir_pos))
            print("Collision, reinserting records:", records_to_insert)

            bucket.i, bucket.r = self.find_perfect_hashing_fn(records_to_insert)
            bucket.p = self.free_space_ptr

            for rec in records_to_insert:
                new_pos = self.get_primary_file_ptr(rec.key)
                print(f"re-inserting key {rec.key} at {new_pos}")
                self.primary_file[new_pos] = rec
            
            self.free_space_ptr += bucket.r


if __name__ == "__main__":
    from db_intro_hw.hw1 import DATA_RECORDS, print_records
    print("Records to insert:\n", "\n".join(list(map(str, DATA_RECORDS))))
    
    cormack = Cormack()
    # Test inserting all records by "age" key

    print("Inserting data records...")
    for rec in DATA_RECORDS:
        cormack.insert(PrimaryFileRecord(rec.age, rec))


    print("\nRecords lookup:")
    for rec in DATA_RECORDS:
        print(f"Searching for age={rec.age}")
        print(cormack.lookup(rec.age).data)