#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_upgradator
----------------------------------

Tests for `upgradator` module.
"""

import unittest
import doctest

from upgradator import upgradator
from upgradator import upgrade_code

class TestUpgradator(unittest.TestCase):

    def setUp(self):
        pass

    def test_docs(self):
        print "this"
        doctest.testmod(upgrade_code)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
