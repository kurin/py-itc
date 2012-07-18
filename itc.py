#!/usr/bin/env python

class IntervalTreeClock(object):
    pass

ITC = IntervalTreeClock

class IDNode(object):
    def __init__(self, val=None):
        self.left = None
        self.right = None
        self.value = val
        self.leaf = val is not None

    def __repr__(self):
        return "ITC: %s"%self.enstring()

    def enstring(self):
        if self.leaf:
            return str(self.value)
        return "(%s, %s)"%(self.left.enstring(), self.right.enstring())

    def clone(self):
        rtn = IDNode(self.value)
        if self.left:
            rtn.left = self.left.clone()
        if self.right:
            rtn.right = self.right.clone()
        rtn.leaf = self.leaf
        return rtn

    def split(self):
        id1 = IDNode()
        id2 = IDNode()

        if self.leaf and self.value == 0: # s(0) -> (0, 0)
            # this isn't supposed to happen
            id1.leaf = True
            id1.value = 0

            id2.leaf = True
            id2.value = 0
        elif self.leaf and self.value == 1: # s(1) -> [(1, 0), (0, 1)]
            id1.left = IDNode(1)
            id1.right = IDNode(0)
            
            id2.left = IDNode(0)
            id2.right = IDNode(1)
        elif not self.leaf and self.left.leaf and self.left.value == 0 and \
                (not self.right.leaf or self.right.value == 1):
            # s(0, i) -> [(0, s1(i)), (0, s2(i))]
            childs = self.right.split()
            id1.left = IDNode(0)
            id1.right = childs[0]

            id2.left = IDNode(0)
            id2.right = childs[1]
        elif not self.leaf and (not self.left.leaf or self.left.value == 1) \
                and self.right.leaf and self.right.value == 0:
            # s(i, 0) -> [(s1(i), 0), (s2(i), 0)]
            childs = self.left.split()
            id1.left = childs[0]
            id1.right = IDNode(0)

            id2.left = childs[1]
            id2.right = IDNode(0)
        elif not self.leaf and (not self.left.leaf or self.left.value == 1) and \
                (not self.right.leaf or self.right.value == 1):
            # s(i1, i2) -> [(i1, 0), (0, i2)]
            id1.left = self.left.clone()
            id1.right = IDNode(0)

            id2.left = IDNode(0)
            id2.right = self.right.clone()

        return id1, id2

    def normalize(self):
        if self.left:
            self.left.normalize()
        if self.right:
            self.right.normalize()

        if not self.leaf and self.left.leaf and self.left.value == 0 and self.right.leaf and self.right.value == 0:
            # (0, 0) -> 0
            self.leaf = True
            self.value = 0
            self.left = self.right = None
        elif not self.leaf and self.left.leaf and self.left.value == 1 and self.right.leaf and self.right.value == 1:
            # (1, 1) -> 1
            self.leaf = True
            self.value = 1
            self.left = self.right = None

    def __add__(self, other): # aka join
        if self.leaf and self.value == 0:
            return other.clone()
        elif other.leaf and other.value == 0:
            return self.clone()
        rtn = IDNode()
        rtn.left = self.left + other.left
        rtn.right = self.right + other.right
        rtn.normalize()
        return rtn
