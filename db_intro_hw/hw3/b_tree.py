from __future__ import annotations
from typing import List, Optional
from abc import ABC, abstractmethod


class Tree(ABC):

    @abstractmethod
    def insert(self, key: int) -> None:
        ...

class Node:
    def __init__(self, arity = 4, redundant = False):
        self.arity = arity
        self.parent: Optional[Node] = None
        self.keys: List[int] = [] 
        self.children: List[Optional[Node]] = [None]
        self.redundant = redundant

    def get_subnode(self, query_key: int) -> Optional[Node]:
        """Basically make one step of a find operation"""
        sanity_checks(self)
    
        if len(self.keys) == 0:
            return self.children[0]
    
        if not self.redundant:
            assert query_key not in self.keys

        for i, k in enumerate(self.keys):
            # if redundant, query_key isn't contained in self.keys, so that's why we can affort <= comparison even in the non-redundant case
            if query_key <= k:
                return self.children[i]

        return self.children[-1]

    def is_leaf_node(self) -> bool:
        return all(map(lambda c: c is None, self.children))

    def __repr__(self):
        return f"Node - keys: {self.keys}, is_leaf_node={self.is_leaf_node()}"
        

    @property
    def full(self):
        return len(self.keys) >= self.arity - 1

    @property
    def overfilled(self):
        return len(self.keys) >= self.arity


    def get_key_idx(self, key: int) -> int:
        """Return index into node's key array, where x belongs"""

        i = 0
        while i < len(self.keys):
            assert self.keys[i] != key
            if self.keys[i] > key:
                return i
            i += 1

        # key is the right-most key in node
        return i


def sanity_checks(node: Optional[Node]) -> None:
    if node is None:
        return
    assert len(node.keys) <= node.arity - 1
    assert len(node.children) <= node.arity
    assert len(node.children) == len(node.keys) + 1
    assert sorted(node.keys) == node.keys

    def check_child_values(key: int, node: Optional[Node], check_fn = lambda key, subkey: key > subkey) -> None:
        if node is None:
            return

        for subkey in node.keys:
            assert check_fn(key, subkey) 


    subkey_less_than_key = lambda key, subkey: key > subkey
    subkey_greater_than_key = lambda key, subkey: key < subkey

    for i, key in enumerate(node.keys):
        left_child = node.children[i] 

        check_child_values(key, left_child, subkey_less_than_key)

        # check parent pointer
        if left_child is not None:
            assert id(left_child.parent) == id(node)

        sanity_checks(left_child)
        

    # also don't forget the right_child checks
    if len(node.keys) > 0:
        check_child_values(node.keys[-1], node.children[-1], subkey_greater_than_key)
    
    sanity_checks(node.children[-1])
    



class NonRedundantBTree(Tree):
    def __init__(self, root=None):
        if root:
            self.root = root
        else:
            self.root: Node = Node()

    
    def find(self, key: int) -> Node:
        """If the tree contains the key, return the Node containing it,
            otherwise return leaf-node where the search ended"""
        sanity_checks(self.root)
        
        current = self.root 

        while True:
            if key in current.keys:
                return current

            # key not found yet
            child = current.get_subnode(key)
            if child is None:
                # key not found, returning leaf-node where search ended
                return current
            
            # recurse into subtree
            current = child



    def balance(self, node: Node) -> None:
        if not node.overfilled:
            return
        
        # we've got to split
        middle_idx = len(node.keys) // 2
        middle_key = node.keys[middle_idx]

        child1, child2 = Node(), Node()
        child1.keys = node.keys[:middle_idx]
        child1.children = node.children[:middle_idx + 1]

        child2.keys = node.keys[middle_idx + 1:]
        child2.children = node.children[middle_idx + 1:]

        # we must also fix node's children parent pointers from pointing to 'node' and point them to child1 and child2
        # because we have just splitted the 'node' and there is no 'node' anymore.
        for c in filter(lambda c: c is not None, child1.children):
            c.parent = child1

        for c in filter(lambda c: c is not None, child2.children):
            c.parent = child2

        if node.parent is None:
            assert id(node) == id(self.root)
            # we are splitting a root
            self.root = Node()
            self.root.keys = [middle_key]
            self.root.children = [child1, child2]
            child1.parent, child2.parent = self.root, self.root 
            return


        # We are not in a root
        child1.parent, child2.parent = node.parent, node.parent

        
        p = node.parent

        # index of the middle key in the parent node after pulling it up one level
        key_p_idx = p.get_key_idx(middle_key)

        p.keys = p.keys[:key_p_idx] + [middle_key] + p.keys[key_p_idx:]
        p.children = p.children[:key_p_idx] + [child1, child2] + p.children[key_p_idx+1:]   # notice we cut-out the pointer to the original unsplitted node

        self.balance(p)


    def insert(self, key: int) -> None:
        sanity_checks(self.root)

        leaf_node = self.find(key)
        assert key not in leaf_node.keys, f"Cannot insert {key}, it's already been inserted into the tree"

        # check that leaf_node is actually a leaf node
        assert leaf_node.is_leaf_node()

        key_idx = leaf_node.get_key_idx(key)

        leaf_node.keys = leaf_node.keys[:key_idx] + [key] + leaf_node.keys[key_idx:]

        # We've added new key, so we need to also add a new null pointer to children
        leaf_node.children.append(None)

        self.balance(leaf_node)

        sanity_checks(self.root)



if __name__ == "__main__":

    from db_intro_hw.hw1 import DATA_RECORDS, print_records
    print("Records to insert:\n", "\n".join(list(map(str, DATA_RECORDS))))
    print()


    non_red_btree = NonRedundantBTree()
    print("Inserting data records...")

    for rec in DATA_RECORDS:
        print("Inserting: ", rec)
        non_red_btree.insert(rec.age)

    print("\n\nRecords lookup:")
    for rec in DATA_RECORDS:
        print(f"Searching for age={rec.age}")
        found_or_not = non_red_btree.find(rec.age)

        if rec.age in found_or_not.keys:
            print(f"key {rec.age} found in {found_or_not}!")
