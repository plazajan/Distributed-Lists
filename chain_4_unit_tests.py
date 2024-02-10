#!/usr/bin/env python3

"""CHAIN CONTROLLER UNIT TESTS.
   Auxiliary CPE methods are not tested here individually."""

#===============================================================================

import unittest
import sys
from chain_2_controller import *

#===============================================================================

# Channel numbering:

CHANNEL = 0
AUX = 1

CHANNEL0 = 0
CHANNEL1 = 1
CHANNEL2 = 2

#===============================================================================
class ChainTest(unittest.TestCase):

    def test_testing_tools(self):

        chain = ChainController()
        self.assertEqual(chain.chain2list(CHANNEL), [])
        self.assertEqual(chain.chain2list(AUX), [])
        chain.stop()

        chain = ChainController([])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        self.assertEqual(chain.chain2list(AUX), [])
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        self.assertEqual(chain.chain2list(AUX), [])
        chain.stop()
        

        chain = ChainController([0,1,2],[3,4])
        self.assertEqual(chain.chain2list(CHANNEL0), [0,1,2])
        self.assertEqual(chain.chain2list(CHANNEL1), [3,4])
        self.assertEqual(chain.chain2list(CHANNEL2), [])
        chain.stop()

    # === LIST OPERATIONS, top CPE operations ========================================

    def test_isEmpty(self):
             
        chain = ChainController([])
        self.assertIs(chain.isEmpty(CHANNEL), True)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()

        chain = ChainController([0])
        self.assertIs(chain.isEmpty(CHANNEL), False)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertIs(chain.isEmpty(CHANNEL), False)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,2])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_clear(self):
        
        chain = ChainController([])
        self.assertEqual(chain.clear(CHANNEL), None)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.clear(CHANNEL), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.clear(CHANNEL), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()
        
    def test_clear2(self):
        
        chain = ChainController()
        chain.clear2(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.clear2(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_first(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.first, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.first(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.first(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,2])
        chain.stop()

    # === LIST OPERATIONS, whole chain operations ========================================

    def test_copy(self):
        
        chain = ChainController([],[10,11,12,13],[100,101])
        chain.copy(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.copy(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.copy(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [10,11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL1) , [10,11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_move(self):
        
        chain = ChainController([],[10,11,12,13],[100,101])
        chain.move(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.move(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.move(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [10,11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_swap(self):
        
        chain = ChainController()
        chain.swap(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [])
        chain.stop()

        chain = ChainController([1,2,3],[],[100,101])
        chain.swap(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([],[11,12,13],[100,101])
        chain.swap(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[10,11,12,13],[100,101])
        chain.swap(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [10,11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3,4],[10,11,12],[100,101])
        chain.swap(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [10,11,12])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

        chain = ChainController([1,2,3],[11,12,13],[100,101])
        chain.swap(CHANNEL1 , CHANNEL0)
        self.assertEqual(chain.chain2list(CHANNEL0) , [11,12,13])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL2) , [100,101])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_setAll(self):
        
        chain = ChainController([])
        self.assertEqual(chain.setAll(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL), []) 
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.setAll(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL), [0])
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.setAll(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL), [0,0,0])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_member(self):
        
        chain = ChainController([])
        self.assertEqual(chain.member(CHANNEL,  0), False)
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.member(CHANNEL,  0), False)
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.member(CHANNEL,  1), True)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.member(CHANNEL,  0), False)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.member(CHANNEL,  1), True)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.member(CHANNEL,  2), True)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.member(CHANNEL,  3), True)
        chain.stop()

    #--- LIST OPERATIONS, top operations -----------------------------------------------
        
    def test_addFirst(self): # push
        
        chain = ChainController([])
        self.assertEqual(chain.addFirst(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.addFirst(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1])
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.addFirst(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,2,3])
        chain.stop()

    def test_addFirstPoor(self):
         
        chain = ChainController([])
        self.assertEqual(chain.addFirstPoor(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.addFirstPoor(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1])
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.addFirstPoor(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,2,3])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_removeGetFirst(self): # pull
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.removeGetFirst, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.removeGetFirst(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.removeGetFirst(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2])
        chain.stop()
        
    #---------------------------------------------------------------------------
    def test_replaceGetFirst(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.replaceGetFirst, CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.replaceGetFirst(CHANNEL,  0), 1)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.replaceGetFirst(CHANNEL,  0), 1)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,2,3])
        chain.stop()

    #--- LIST OPERATIONS, bottom operations ------------------------------------------------

    def test_last(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.last, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.last(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.last(CHANNEL), 2)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,2])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_addLast(self):
        
        chain = ChainController([])
        self.assertEqual(chain.addLast(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.addLast(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,0])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual(chain.addLast(CHANNEL, 0), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [3,2,1,0])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_removeLast(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.removeLast, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.removeLast(CHANNEL), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()
        
        chain = ChainController([0,1,2])
        self.assertEqual(chain.removeLast(CHANNEL), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_removeGetLast(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.removeGetLast, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.removeGetLast(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.removeGetLast(CHANNEL), 2)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_replaceLast(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.replaceLast, CHANNEL,  3)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.replaceLast(CHANNEL,  3), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [3])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.replaceLast(CHANNEL,  3), None)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,3])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_replaceGetLast(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.replaceGetLast, CHANNEL,  3)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.replaceGetLast(CHANNEL,  3), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [3])
        chain.stop()

        chain = ChainController([0,1])
        self.assertEqual(chain.replaceGetLast(CHANNEL,  3), 1)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,3])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.replaceGetLast(CHANNEL,  3), 2)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,3])
        chain.stop()

    #--- LIST OPERATIONS, rotations ------------------------------------------------------

    def test_rotateDown(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.rotateDown, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.rotateDown(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([0,1])
        self.assertEqual(chain.rotateDown(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,0])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.rotateDown(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,0])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_rotateUp(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.rotateUp, CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([0])
        self.assertEqual(chain.rotateUp(CHANNEL), 0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([0,1])
        self.assertEqual(chain.rotateUp(CHANNEL), 1)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,0])
        chain.stop()

        chain = ChainController([0,1,2])
        self.assertEqual(chain.rotateUp(CHANNEL), 2)
        self.assertEqual(chain.chain2list(CHANNEL) , [2,0,1])
        chain.stop()

    #--- LIST OPERATIONS, reverse --------------------------------------------------------

    def test_reverseSimplest(self):
        
        chain = ChainController([])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2]) 
        chain.stop()

        chain = ChainController([3,2,1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5])
        chain.stop()

        chain = ChainController([6,5,4,3,2,1])
        chain.reverseSimplest(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5,6])
        chain.stop() 

    #---------------------------------------------------------------------------

    def test_reverseSimple(self):
        
        chain = ChainController([])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2]) 
        chain.stop()

        chain = ChainController([3,2,1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5])
        chain.stop()

        chain = ChainController([6,5,4,3,2,1])
        chain.reverseSimple(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5,6])
        chain.stop() 

    #---------------------------------------------------------------------------
    def test_reverse(self):
        
        chain = ChainController([])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2]) 
        chain.stop()

        chain = ChainController([3,2,1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5])
        chain.stop()

        chain = ChainController([6,5,4,3,2,1])
        chain.reverse(CHANNEL0, CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5,6])
        chain.stop() 

    #============= ORDER OPERATIONS ============================================

    def test_min(self):
        
        chain = ChainController([])
        self.assertRaises(EmptyError, chain.minimum, CHANNEL)
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

        chain = ChainController([1,2])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

        chain = ChainController([3,1,2])
        self.assertEqual(chain.minimum(CHANNEL), 1)
        chain.stop()

    #---------------------------------------------------------------------------
    def test_memberND(self):

        chain = ChainController([])
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  0), False)
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  0), False)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  1), True)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  2), False)
        chain.stop()
        
        chain = ChainController([1,3,3,5])
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  0), False)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  1), True)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  2), False)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  3), True)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  4), False)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  5), True)
        self.assertEqual(chain.memberNonDecreasing(CHANNEL,  6), False)
        chain.stop()

    #---------------------------------------------------------------------------
    def test_insertNonDecreasing(self):
        
        chain = ChainController([])
        chain.insertNonDecreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1])
        chain.insertNonDecreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0, 1])
        chain.stop()

        chain = ChainController([1])
        chain.insertNonDecreasing(CHANNEL,  2)
        self.assertEqual(chain.chain2list(CHANNEL) , [1, 2])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertNonDecreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertNonDecreasing(CHANNEL,  1)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertNonDecreasing(CHANNEL,  2)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertNonDecreasing(CHANNEL,  3)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,3,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertNonDecreasing(CHANNEL,  4)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,3,4])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_insertUniqueIncreasing(self):
        
        chain = ChainController([])
        chain.insertUniqueIncreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0])
        chain.stop()

        chain = ChainController([1])
        chain.insertUniqueIncreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0, 1])
        chain.stop()

        chain = ChainController([1])
        chain.insertUniqueIncreasing(CHANNEL,  1)
        self.assertEqual(chain.chain2list(CHANNEL) , [1])
        chain.stop()

        chain = ChainController([1])
        chain.insertUniqueIncreasing(CHANNEL,  2)
        self.assertEqual(chain.chain2list(CHANNEL) , [1, 2])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertUniqueIncreasing(CHANNEL,  0)
        self.assertEqual(chain.chain2list(CHANNEL) , [0,1,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertUniqueIncreasing(CHANNEL,  1)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertUniqueIncreasing(CHANNEL,  3)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertUniqueIncreasing(CHANNEL,  2)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3])
        chain.stop()

        chain = ChainController([1,3])
        chain.insertUniqueIncreasing(CHANNEL,  4)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,3,4])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_insertAllNonDecreasingSimple(self):

        chain = ChainController([],[])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        chain.stop()

        chain = ChainController([],[1])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1])
        chain.stop()

        chain = ChainController([1],[])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1])
        chain.stop()

        chain = ChainController([2],[1])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2])
        chain.stop()

        chain = ChainController([1],[2])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2])
        chain.stop()

        chain = ChainController([5,1,3],[2,4])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5])
        chain.stop()

        chain = ChainController([5,1,3],[])
        chain.insertAllNonDecreasingSimple(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,3,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_insertAllNonDecreasing(self):

        chain = ChainController([],[])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        chain.stop()

        chain = ChainController([],[1])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1])
        chain.stop()

        chain = ChainController([1],[])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1])
        chain.stop()

        chain = ChainController([2],[1])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2])
        chain.stop()

        chain = ChainController([1],[2])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2])
        chain.stop()

        chain = ChainController([5,1,3],[2,4])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5])
        chain.stop()

        chain = ChainController([5,1,3],[])
        chain.insertAllNonDecreasing(CHANNEL0,  CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL0) , [])
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,3,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_iSort(self):
        
        chain = ChainController([])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1]) 
        chain.stop()

        chain = ChainController([1,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()
        
        chain = ChainController([1,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1]) 
        chain.stop()
        
        chain = ChainController([1,1,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([2,1,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,1,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,2,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([1,2,3])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([1,3,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,1,3])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,3,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,1,2])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,2,1])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,4,1,5,2,3])
        chain.iSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2,3,4,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_sSort(self):
        
        chain = ChainController([])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1]) 
        chain.stop()

        chain = ChainController([1,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()
        
        chain = ChainController([1,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1]) 
        chain.stop()
        
        chain = ChainController([1,1,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([2,1,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,1,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,2,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([1,2,3])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([1,3,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,1,3])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,3,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,1,2])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,2,1])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,4,1,5,2,3])
        chain.sSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2,3,4,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_bSort(self):
        
        chain = ChainController([])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , []) 
        chain.stop()

        chain = ChainController([1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1]) 
        chain.stop()

        chain = ChainController([1,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()

        chain = ChainController([2,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2]) 
        chain.stop()
        
        chain = ChainController([1,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1]) 
        chain.stop()
        
        chain = ChainController([1,1,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([2,1,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,1,2]) 
        chain.stop()
        
        chain = ChainController([1,2,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,1,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([2,2,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2]) 
        chain.stop()
        
        chain = ChainController([1,2,3])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([1,3,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,1,3])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,3,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,1,2])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([3,2,1])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3]) 
        chain.stop()
        
        chain = ChainController([2,4,1,5,2,3])
        chain.bSort(CHANNEL)
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2,3,4,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_mergeNonDecreasingSimple(self):

        chain = ChainController([],[],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [])
        chain.stop()

        chain = ChainController([1,2,3],[],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [1,2,3])
        chain.stop()

        chain = ChainController([],[1,2,3],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [1,2,3])
        chain.stop()

        chain = ChainController([1,3],[2,4,6],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [1,2,3,4,6])
        chain.stop()

        chain = ChainController([1,3,5],[2,4,6],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [1,2,3,4,5,6])
        chain.stop()

        chain = ChainController([1,3,5],[0,2,4],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [0,1,2,3,4,5])
        chain.stop()

        chain = ChainController([3,5,7],[0,2,4,6],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [0,2,3,4,5,6,7])
        chain.stop()

        chain = ChainController([1,3,5],[0,2,4,6],[100,101])
        chain.mergeNonDecreasingSimple(CHANNEL0 , CHANNEL1, CHANNEL2)
        self.assertEqual(chain.chain2list(CHANNEL2) , [0,1,2,3,4,5,6])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_mergeNonDecreasing(self):
        chain = ChainController([],[],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [])
        chain.stop()

        chain = ChainController([1,2,3],[],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        chain.stop()

        chain = ChainController([],[1,2,3],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3])
        chain.stop()

        chain = ChainController([1,3],[2,4,6],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,6])
        chain.stop()

        chain = ChainController([1,3,5],[2,4,6],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [1,2,3,4,5,6])
        chain.stop()

        chain = ChainController([1,3,5],[0,2,4],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [0,1,2,3,4,5])
        chain.stop()

        chain = ChainController([3,5,7],[0,2,4,6],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [0,2,3,4,5,6,7])
        chain.stop()

        chain = ChainController([1,3,5],[0,2,4,6],[100,101])
        chain.mergeNonDecreasing(CHANNEL0 , CHANNEL1)
        self.assertEqual(chain.chain2list(CHANNEL1) , [0,1,2,3,4,5,6])
        chain.stop()

    # === INDEXING OPERATIONS =================================================

    def test_length(self):
        
        chain = ChainController([])
        self.assertEqual(chain.length(CHANNEL), 0)
        chain.stop()

        chain = ChainController([1])
        self.assertEqual(chain.length(CHANNEL), 1)
        chain.stop()

        chain = ChainController([1,2])
        self.assertEqual(chain.length(CHANNEL), 2)
        chain.stop()

        chain = ChainController([1,2,3])
        self.assertEqual(chain.length(CHANNEL), 3)
        chain.stop()

    def test_getItem(self):
        chain = ChainController([10])
        self.assertEqual(chain.getItem(CHANNEL, 0), 10)
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.getItem(CHANNEL, 0), 10)
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.getItem(CHANNEL, 1), 11)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertEqual(chain.getItem(CHANNEL, 2), 12)
        chain.stop()

        chain = ChainController([])
        self.assertRaises(IndexError, chain.getItem, CHANNEL, 0)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.getItem, CHANNEL, 3)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.getItem, CHANNEL, 5)
        chain.stop()

    def test_setItem0(self):
        chain = ChainController([10])
        chain.setItem0(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100])
        chain.stop()

        chain = ChainController([10,11])
        chain.setItem0(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 11])
        chain.stop()

        chain = ChainController([10,11])
        chain.setItem0(CHANNEL, 1, 111)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 111])
        chain.stop()

        chain = ChainController([10,11,12])
        chain.setItem0(CHANNEL, 2, 112)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 11, 112])
        chain.stop()

        chain = ChainController([10,11,12])
        chain.setItem0(CHANNEL, 3, 113)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 11, 12])
        chain.stop()

        chain = ChainController([10,11,12])
        chain.setItem0(CHANNEL, 5, 115)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 11, 12])
        chain.stop()

    def test_setItem(self):
        chain = ChainController([10])
        chain.setItem(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100])
        chain.stop()

        chain = ChainController([10,11])
        chain.setItem(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 11])
        chain.stop()

        chain = ChainController([10,11])
        chain.setItem(CHANNEL, 1, 111)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 111])
        chain.stop()

        chain = ChainController([10,11,12])
        chain.setItem(CHANNEL, 2, 112)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 11, 112])
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.setItem, CHANNEL, 3, 113)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.setItem, CHANNEL, 5, 115)
        chain.stop()   

    def test_getSetItem(self):
        chain = ChainController([10])
        self.assertEqual(chain.getSetItem(CHANNEL, 0, 100), 10)
        self.assertEqual(chain.chain2list(CHANNEL), [100])
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.getSetItem(CHANNEL, 0, 100), 10)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 11])
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.getSetItem(CHANNEL, 1, 111), 11)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 111])
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertEqual(chain.getSetItem(CHANNEL, 2, 112), 12)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 11, 112])
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.getSetItem, CHANNEL, 3, 113)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(IndexError, chain.getSetItem, CHANNEL, 5, 115)
        chain.stop()

    def test_memberIndex(self):
        chain = ChainController([])
        self.assertRaises(ValueError, chain.memberIndex, CHANNEL, 3)
        chain.stop()

        chain = ChainController([10])
        self.assertEqual(chain.memberIndex(CHANNEL, 10), 0)
        chain.stop()

        chain = ChainController([10])
        self.assertRaises(ValueError, chain.memberIndex, CHANNEL, 11)
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.memberIndex(CHANNEL, 10), 0)
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.memberIndex(CHANNEL, 11), 1)
        chain.stop()

        chain = ChainController([10,11])
        self.assertRaises(ValueError, chain.memberIndex, CHANNEL, 12)
        chain.stop()

        chain = ChainController([10,10])
        self.assertEqual(chain.memberIndex(CHANNEL, 10), 0)
        chain.stop()
        
        chain = ChainController([10,11,12])
        self.assertEqual(chain.memberIndex(CHANNEL, 10), 0)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertEqual(chain.memberIndex(CHANNEL, 11), 1)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertEqual(chain.memberIndex(CHANNEL, 12), 2)
        chain.stop()

        chain = ChainController([10,11,12])
        self.assertRaises(ValueError, chain.memberIndex, CHANNEL, 13)
        chain.stop()

        chain = ChainController([10,10,12])
        self.assertEqual(chain.memberIndex(CHANNEL, 10), 0)
        chain.stop()

        chain = ChainController([10,11,11])
        self.assertEqual(chain.memberIndex(CHANNEL, 11), 1)
        chain.stop()

    def test_insertAtIndex0(self):
        chain = ChainController([])
        chain.insertAtIndex0(CHANNEL, 0, 13)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([])
        chain.insertAtIndex0(CHANNEL, 1, 13)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([10])
        chain.insertAtIndex0(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 10])
        chain.stop()

        chain = ChainController([10])
        chain.insertAtIndex0(CHANNEL, 1, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [10])
        chain.stop()

        chain = ChainController([10,11])
        chain.insertAtIndex0(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 10, 11])
        chain.stop()

        chain = ChainController([10,11])
        chain.insertAtIndex0(CHANNEL, 1, 110)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 110, 11])
        chain.stop()

        chain = ChainController([10,11])
        chain.insertAtIndex0(CHANNEL, 2, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [10,11])
        chain.stop()

    def test_insertAtIndex(self):
        chain = ChainController([])
        self.assertRaises(IndexError, chain.insertAtIndex, CHANNEL, 0, 13)
        chain.stop()

        chain = ChainController([])
        self.assertRaises(IndexError, chain.insertAtIndex, CHANNEL, 1, 13)
        chain.stop()

        chain = ChainController([10])
        chain.insertAtIndex(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 10])
        chain.stop()

        chain = ChainController([10])
        self.assertRaises(IndexError, chain.insertAtIndex, CHANNEL, 1, 100)
        chain.stop()

        chain = ChainController([10,11])
        chain.insertAtIndex(CHANNEL, 0, 100)
        self.assertEqual(chain.chain2list(CHANNEL), [100, 10, 11])
        chain.stop()

        chain = ChainController([10,11])
        chain.insertAtIndex(CHANNEL, 1, 110)
        self.assertEqual(chain.chain2list(CHANNEL), [10, 110, 11])
        chain.stop()

        chain = ChainController([10,11])
        self.assertRaises(IndexError, chain.insertAtIndex, CHANNEL, 2, 100)
        chain.stop()

    def test_deleteAtIndex(self):
        chain = ChainController([])
        chain.deleteAtIndex(CHANNEL, 0)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([])
        chain.deleteAtIndex(CHANNEL, 1)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([10])
        chain.deleteAtIndex(CHANNEL, 0)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([10])
        chain.deleteAtIndex(CHANNEL, 1)
        self.assertEqual(chain.chain2list(CHANNEL), [10])
        chain.stop()

        chain = ChainController([10,11])
        chain.deleteAtIndex(CHANNEL, 0)
        self.assertEqual(chain.chain2list(CHANNEL), [11])
        chain.stop()

        chain = ChainController([10,11])
        chain.deleteAtIndex(CHANNEL, 1)
        self.assertEqual(chain.chain2list(CHANNEL), [10])
        chain.stop()

        chain = ChainController([10,11])
        chain.deleteAtIndex(CHANNEL, 2)
        self.assertEqual(chain.chain2list(CHANNEL), [10,11])
        chain.stop()


    def test_deleteGetAtIndex(self):
        chain = ChainController([])
        self.assertRaises(IndexError, chain.deleteGetAtIndex, CHANNEL, 0)
        chain.stop()

        chain = ChainController([])
        self.assertRaises(IndexError, chain.deleteGetAtIndex, CHANNEL, 1)
        chain.stop()

        chain = ChainController([10])
        self.assertEqual(chain.deleteGetAtIndex(CHANNEL, 0),10)
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([10])
        self.assertRaises(IndexError, chain.deleteGetAtIndex, CHANNEL, 1)
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.deleteGetAtIndex(CHANNEL, 0), 10)
        self.assertEqual(chain.chain2list(CHANNEL), [11])
        chain.stop()

        chain = ChainController([10,11])
        self.assertEqual(chain.deleteGetAtIndex(CHANNEL, 1),11)
        self.assertEqual(chain.chain2list(CHANNEL), [10])
        chain.stop()

        chain = ChainController([10,11])
        self.assertRaises(IndexError, chain.deleteGetAtIndex, CHANNEL, 2)
        chain.stop()

    # ====== LOADERS AND UNLOADERS =============================================

    def test_loadWordsSimple(self):
        
        chain = ChainController([])
        
        chain.loadWordsSimple(CHANNEL,  [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL), [1,2,3])

        chain.loadWordsSimple(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        
        chain.stop()

    def test_loadWords(self):
        
        chain = ChainController([])
        
        chain.loadWords(CHANNEL,  [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL), [1,2,3])

        chain.loadWords(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        
        chain.stop()

    #---------------------------------------------------------------------------
    def test_loadWordsReverseSimple(self):
        
        chain = ChainController([])
        
        chain.loadWordsReverseSimple(CHANNEL,  [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL), [3,2,1])

        chain.loadWordsReverseSimple(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        
        chain.stop()

    def test_loadWordsReverse(self):
        
        chain = ChainController([])
        
        chain.loadWordsReverse(CHANNEL,  [1,2,3])
        self.assertEqual(chain.chain2list(CHANNEL), [3,2,1])

        chain.loadWordsReverse(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        
        chain.stop()

    #---------------------------------------------------------------------------
    def test_loadWordsNonDecreasingSimple(self):

        chain = ChainController([])
        
        chain.loadWordsNonDecreasingSimple(CHANNEL,  [2,4,1,5,2,3])
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2,3,4,5])

        chain.loadWordsNonDecreasingSimple(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL) , [])

        chain.stop()

    def test_loadWordsNonDecreasing(self):

        chain = ChainController([])
        
        chain.loadWordsNonDecreasing(CHANNEL,  [2,4,1,5,2,3])
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,2,3,4,5])

        chain.loadWordsNonDecreasing(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL) , [])

        chain.stop()

    #---------------------------------------------------------------------------
    def test_loadWordsUniqueIncreasingSimple(self):

        chain = ChainController([])
        
        chain.loadWordsUniqueIncreasingSimple(CHANNEL,  [2,4,1,3,5,2,3,1])
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3,4,5])

        chain.loadWordsUniqueIncreasingSimple(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL) , [])

        chain.stop()

    def test_loadWordsUniqueIncreasing(self):

        chain = ChainController([])
        
        chain.loadWordsUniqueIncreasing(CHANNEL,  [2,4,1,3,5,2,3,1])
        self.assertEqual(chain.chain2list(CHANNEL) , [1,2,3,4,5])

        chain.loadWordsUniqueIncreasing(CHANNEL,  [])
        self.assertEqual(chain.chain2list(CHANNEL) , [])

        chain.stop()

    #---------------------------------------------------------------------------

    def test_unloadWords(self):

        chain = ChainController([])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([4,3,2,1])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [4,3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        self.assertEqual([x for x in chain.unloadWords(CHANNEL)],
                         [5,4,3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_unloadAllWords(self):

        chain = ChainController([])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([4,3,2,1])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [4,3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        self.assertEqual([x for x in chain.unloadAllWords(CHANNEL)],
                         [5,4,3,2,1])
        self.assertEqual(chain.chain2list(CHANNEL), [])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_unloadWordsReverseSimple(self):

        chain = ChainController([])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)], [])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)], [1])
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)],
                         [1,2])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)],
                         [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)],
                         [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverseSimple(CHANNEL, AUX)],
                         [1,2,3,4,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_unloadWordsReverse(self):

        chain = ChainController([])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)], [])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)], [1])
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)],
                         [1,2])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)],
                         [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)],
                         [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        self.assertEqual([x for x in chain.unloadWordsReverse(CHANNEL, AUX)],
                         [1,2,3,4,5])
        chain.stop()

    #---------------------------------------------------------------------------
    def test_unloadAllWordsReverse(self):

        chain = ChainController([])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [])
        chain.stop()

        chain = ChainController([1])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [1])
        chain.stop()

        chain = ChainController([2,1])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [1,2])
        chain.stop()

        chain = ChainController([3,2,1])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [1,2,3])
        chain.stop()

        chain = ChainController([4,3,2,1])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [1,2,3,4])
        chain.stop()

        chain = ChainController([5,4,3,2,1])
        self.assertEqual([x for x in chain.unloadAllWordsReverse(CHANNEL, AUX)],
                         [1,2,3,4,5])
        chain.stop()

    #=== ARITHMETIC ============================================================

    def test_loadInteger(self):
        
        chain = ChainController([])

        chain.loadInteger(CHANNEL,  [0,1,2,3])
        self.assertEqual(chain.register2list(CHANNEL) , [0,1,2,3])
        
        chain.loadInteger(CHANNEL,  [0])
        self.assertEqual(chain.register2list(CHANNEL) , [0])

        chain.stop()

    #---------------------------------------------------------------------------
    def test_equal(self):
        
        chain = ChainController([])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0])
        chain.loadInteger(CHANNEL1,  [0])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,1,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,1,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,1])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,1])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [1,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [1,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.equal(CHANNEL0, CHANNEL1), False)

        chain.stop()

    #---------------------------------------------------------------------------
    def test_lessOrEqual(self):
        
        chain = ChainController([])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0])
        chain.loadInteger(CHANNEL1,  [0])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,1,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,1,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,1])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,1])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [1,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [1,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.lessOrEqual(CHANNEL0, CHANNEL1), False)

        chain.stop()

    #---------------------------------------------------------------------------
    def test_less(self):
        
        chain = ChainController([])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0])
        chain.loadInteger(CHANNEL1,  [0])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,1,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,1,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,1])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.loadInteger(CHANNEL0,  [0,1,2,1])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [1,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), True)

        chain.loadInteger(CHANNEL0,  [1,1,2,3])
        chain.loadInteger(CHANNEL1,  [0,1,2,3])
        self.assertEqual(chain.less(CHANNEL0, CHANNEL1), False)

        chain.stop()

    #---------------------------------------------------------------------------
    def test_copyInt(self):
        
        chain = ChainController([])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        self.assertEqual(chain.copyInt(CHANNEL0, CHANNEL1), None)
        self.assertEqual(chain.register2list(CHANNEL0), [0,1,2,3])
        self.assertEqual(chain.register2list(CHANNEL1), [0,1,2,3])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [4,5,6])
        self.assertEqual(chain.copyInt(CHANNEL0, CHANNEL1), None)
        self.assertEqual(chain.register2list(CHANNEL0), [0,1,2,3])
        self.assertEqual(chain.register2list(CHANNEL1), [0,1,2,3])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [4,5,6,7])
        self.assertEqual(chain.copyInt(CHANNEL0, CHANNEL1), None)
        self.assertEqual(chain.register2list(CHANNEL0), [0,1,2,3])
        self.assertEqual(chain.register2list(CHANNEL1), [0,1,2,3])

        chain.loadInteger(CHANNEL0,  [0,1,2,3])
        chain.loadInteger(CHANNEL1,  [4,5,6,7,8])
        self.assertEqual(chain.copyInt(CHANNEL0, CHANNEL1), None)
        self.assertEqual(chain.register2list(CHANNEL0), [0,1,2,3])
        self.assertEqual(chain.register2list(CHANNEL1), [0,1,2,3])

        chain.loadInteger(CHANNEL0,  [0])
        chain.loadInteger(CHANNEL1,  [4,5,6,7])
        self.assertEqual(chain.copyInt(CHANNEL0, CHANNEL1), None)
        self.assertEqual(chain.register2list(CHANNEL0), [0])
        self.assertEqual(chain.register2list(CHANNEL1), [0])

        chain.stop()

    #---------------------------------------------------------------------------
##    def test_conjunction(self):
##        
##        chain = ChainController()
##
##        chain.loadInteger(CHANNEL0,  [0b1010, 0b1100, 0b1])
##        chain.loadInteger(CHANNEL1,  [0b1100, 0b1010])
##        chain.conjunction(CHANNEL0, CHANNEL1, CHANNEL2)
##        self.assertEqual(chain.register2list(CHANNEL2), [0b1000, 0b1000, 0b0])
##
##        chain.stop()




    #-----------------------------------------------------------
##    def test_double(self): #TO DO
##        
##        chain = ChainController([])
##
##        chain.loadInteger(CHANNEL,  [0,1,2,3])
##        self.assertEqual(chain.register2list(CHANNEL) , [0,1,2,3])
##        
##        chain.loadInteger(CHANNEL,  [0])
##        self.assertEqual(chain.register2list(CHANNEL) , [0])
##
##        chain.stop()

#===============================================================================
        
def main(argv):
    unittest.main()
    
#===============================================================================

if __name__ == '__main__':
    main(sys.argv)

#===============================================================================


