
import unittest

print ""
print "UNITTESTS"
print "==================================="
a = unittest.TestLoader().discover("pygranule/tests/unittests")
testsuite = unittest.TestSuite(a)
unittest.TextTestRunner(verbosity=2).run(testsuite)
print ""
print "UNITTESTS"
print "==================================="
a = unittest.TestLoader().discover("pygranule/tests/integrationtests")
testsuite = unittest.TestSuite(a)
unittest.TextTestRunner(verbosity=2).run(testsuite)
