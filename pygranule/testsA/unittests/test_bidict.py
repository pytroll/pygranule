
import unittest

from pygranule.bidict import BiDict

class TestBiDict(unittest.TestCase):
    def setUp(self):
        self.d = {"pathA1":"pathB1",
             "pathA2":"pathB2",
             "pathA3":"pathB3"}
        self.bd = BiDict(self.d.copy())

        self.d2 = {"pathA1":"pathB1",
             "pathA4":"pathB4",
             "pathA3":"pathB3"}
        self.bd2 = BiDict(self.d2.copy())

    def test_setitem(self):
        # Run
        self.bd["pathA4"] = "pathB4"
        # Assert
        result = [ (x,self.bd.fwd[x]) for x in self.bd.fwd ]
        self.d["pathA4"] = "pathB4"
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)

    def test_delitem(self):
        # Run
        del self.bd["pathA2"]
        # Assert
        result = [ (x,self.bd.fwd[x]) for x in self.bd.fwd ]
        del self.d["pathA2"]
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)

    def test_inverse(self):
        # Run
        inv = (~self.bd)
        # Assert
        for key in self.d:
            self.assertEqual(inv[self.d[key]] , key)

    def test_remove(self):
        # Run
        self.bd.remove("pathA2")
        # Assert
        result = [ (x,self.bd.fwd[x]) for x in self.bd.fwd ]
        del self.d["pathA2"]
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)

    def test_difference(self):
        # Run
        diff = self.bd.difference(self.bd2)
        # Assert
        result = [ (x,diff.fwd[x]) for x in diff.fwd ]
        del self.d["pathA1"]
        del self.d["pathA3"]
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)

    def test_update(self):
        # Run
        self.bd.update(self.bd2)
        # Assert
        result = [ (x, self.bd.fwd[x]) for x in self.bd.fwd ]
        self.d["pathA4"] = "pathB4"
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)        
        
    def test_reduce(self):
        # Run
        self.bd.reduce(self.bd2)
        # Assert
        result = [ (x, self.bd.fwd[x]) for x in self.bd.fwd ]
        del self.d["pathA1"]
        del self.d["pathA3"]
        ref = [ (x, self.d[x]) for x in self.d ]
        self.assertItemsEqual(result, ref)
