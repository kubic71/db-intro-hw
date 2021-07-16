# The problem statement

## 1. Define your data
- describe your data record
- generate +- 20 sample records

## 2. Build an index
- create primary file with your data record
- build build the following index tables for the attributes of choice
    - primary index
    - secondary direct index
    - secondary indirect index
- choose one categorical attribute and build a bitmap over it

## 3. Compute real file-sizes for bigger data
- **parameters**
    - block size = 4KiB
    - decide, how much space take standard data-types (bool, char, int)
    - number of records = 5M
- compute the size of primary file
- compute the size of all indeces built in 2) but with *this* bigger data
- how many blocks are there on every level?
- how many reads are necessary to find a data record?
- compute the size of the bitmap

