#!/usr/bin/env python3

"""CHAIN CONTROLLER DEMOS."""

#===============================================================================

from chain_2_controller import *

#===============================================================================

# Channel numbering:

CHANNEL = 0
AUX = 1

CHANNEL0 = 0
CHANNEL1 = 1
CHANNEL2 = 2

# ==============================================================================

class SameType(object):
    """(Similar to NoneType.) There is only one object of this type: Some. 
       Some has no Boolean value.
       Same == Same --> True
       Same != Same --> False
       Same is Same --> True
       """
    
    def __new__(cls, *args, **kwargs):
        # singleton (only one such objects exists)
        try:
            obj = cls._obj
        except AttributeError:
            obj = object.__new__(cls, *args, **kwargs)
            cls._obj = obj
        return obj

    def __bool__(self):
        raise TypeError("The object Any is neither True nor False.")

    def __repr__(self):
        return "Same"

    def copy(self): 
        return self #There is only one object of this type in RAM. 

Same = SameType()
# ==============================================================================

def demo(chainListsInitial, *args):
    """chain(chainListsInitial,
             operationString1, returnValueOrException1, chainListsExpectedResult1,
             ...
             operationStringN, returnValueOrExceptionN, chainListsExpectedResultN,
             detailed
            )
       Every chainLists... argument needs to be a list of lists of integers.
       [[],[],[]] can be abbreviated [].
       [[...], [], []] can be abbreviated [[...]].
       [[...], [...], []] can be abbreviated [[...],[...]].
       The last argument, detailed, must be a Boolean value and is optional;
       if absent its default value is False. This controls whether the chain
       is diapyaed in a detailed way or not.
    """
    # Check and prepare function arguments.
    if len(args) % 3 == 2:
        raise SyntaxError("demo requires eihter 3n+1 or 3n+2 parameters, not "+
                          str(len(args)+1))
    if len(args) % 3 == 1:
        detailed = args[-1]
        if not isinstance(detailed, bool):
            raise TypeErorr("If there are n+1 parameters" +\
                            "the last one must be of type bool.")
    else:
        detailed = False
    
    # Create initial chain an report its state.
    chain = ChainController(*chainListsInitial)
    chain.report(detailed=detailed)
    print()

    # Initialize loop variables and process all the operations in a loop.
    chainListsInitialMy = chainListsInitial 
    argsMy = args 

    while len(argsMy)>=3:

        # Extract an operation, return value and resulting list.
        operationString, returnValueOrError, chainListsExpectedResult, argsMy = \
            argsMy[0], argsMy[1], argsMy[2].copy(), argsMy[3:] # slice is a copy
        
        # Execute the operation, print return value or exception
        operationString = "chain." + operationString
        if returnValueOrError is None:
            print(operationString)
            rv = eval(operationString)
            if rv is not None:
                raise ValueError(operationString + " should return no value, not " +\
                                 str(rv))
            else:
                print("(returned no value -- as expected!)")

        elif type(returnValueOrError) != type: # if it is not an exception
            print(operationString[6:], "= ", end="")
            rv = eval(operationString)
            if rv == returnValueOrError:
                print(rv, "-- as expected!")
            else:
                raise ValueError(operationString + " should return " + \
                                 str(returnValueOrError))
        else: # returnValueOrError is an exception
            try:
                eval(operationString)
            except returnValueOrError:
                print(operationString[6:], "raised",
                      str(returnValueOrError)[8:-2].split(".")[-1],
                      "-- as expected!")

        # If needed, report the resulting state of the chain.
        print()
        if chainListsExpectedResult is not Same:
            chain.report(detailed=detailed)

        # Check if the resulting chain is as expected.
            
        if chainListsExpectedResult is Same:
            chainListsExpectedResult = chainListsInitialMy
        # make sure empty chain list are shown explicitely:
        for _ in range(CHANNELS - len(chainListsExpectedResult)):
            chainListsExpectedResult.append([])

        if chain.chain2lists() != chainListsExpectedResult:
            raise ValueError("The resulting chain should store",
                             chainListsExpectedResult)
        else:
            
            if chainListsInitialMy == chainListsExpectedResult:
                print("The chain lists have not changed -- as expected!")
            else:
                print("The chain lists have changed as expected.")
        print()
        
        # prepare for the next iteration:
        chainListsInitialMy = chainListsExpectedResult
        
    chain.stop()
    print("-------------------------------------------------------------------")

# ==============================================================================

def chainDemo(): 
    print("============== SHowing chains ====================")
    
    print("demo([], True) -- this prints a chain with empty channels/lists,")
    print("where True forces a detailed view.")
    demo([], True)

    print("demo([]) -- the same with less dtails: ")
    demo([])
    
    print("-------------------------------------------------------------------")
    
    print("demo([[1], [11,22]], True) -- this prints a chain with")
    print("Channel0 containg the list [1],")
    print("Channel1 containg the list [11,22],")
    print("Channel2 containg the list [],")
    print("where True forces a detailed view.")
    demo([[1], [11,22]], True)
    
    print("demo([[1], [11,22]]) -- the same with less dtails: ")
    demo([[1], [11,22]])
    
    print("-------------------------------------------------------------------")
    
#chainDemo()

# === LIST OPERATIONS, stack, queue operations ===========================================

def stackDemo():
    print("============== stack operations ===================================")
    print()
    print("The top of the chain is the top of the stack.")
    print("All the stack operations below have top complexity O(1).")
    print()
    demo([[]],
         "push(CHANNEL, 0)", None,       [[0]],
         "push(CHANNEL, 1)", None,       [[1,0]],
         "push(CHANNEL, 2)", None,       [[2,1,0]],
         "pop(CHANNEL)",     2,          [[1,0]],
         "top(CHANNEL)",     1,          Same,
         "clear(CHANNEL)",   None,       [[]],
         "isEmpty(CHANNEL)", True,       Same,
         "top(CHANNEL)",     EmptyError, Same
        )
         
stackDemo()

def queueDemo():
    print("============== queue operations ===================================")
    print()
    print("The top of the chain is the front of the queue.")
    print("All the queue operations below have top complexity O(1).")
    print()
    demo([[]],
         "enqueue(CHANNEL, 0)", None,       [[0]],
         "enqueue(CHANNEL, 1)", None,       [[0,1]],
         "enqueue(CHANNEL, 2)", None,       [[0,1,2]],
         "dequeue(CHANNEL)",    0,          [[1,2]],
         "first(CHANNEL)",      1,          Same,
         "clear(CHANNEL)",      None,       [[]],
         "isEmpty(CHANNEL)",    True,       Same,
         "first(CHANNEL)",      EmptyError, Same
        )

#queueDemo()
    
# === LIST OPERATIONS, top CPE operations ============================================

def isEmptyDemo():
    print("============== isEmpty ============================================")
    demo([[]],      "isEmpty(CHANNEL)", True,  [[]])
    demo([[0]],     "isEmpty(CHANNEL)", False, Same)
    demo([[0,1,2]], "isEmpty(CHANNEL)", False, Same)

#isEmptyDemo()
    
def clearDemo(): 
    print("============== clear ==============================================")
    demo([[]],      "clear(CHANNEL)", None, Same)
    demo([[0]],     "clear(CHANNEL)", None, [[]])
    demo([[0,1,2]], "clear(CHANNEL)", None, [[]])
    
#clearDemo()

def clear2Demo(): 
    print("============== clear2 =============================================")
    demo([[],[]],                           "clear2(CHANNEL0,CHANNEL1)",
         None, Same)
    demo([[1,2,3],[10,11,12,13],[100,101]], "clear2(CHANNEL0,CHANNEL1)",
         None, [[],[],[100,101]])
     
#clear2Demo()

def firstDemo(): 
    print("============== first ==============================================")
    demo([],        "first(CHANNEL)", EmptyError, Same)
    demo([[0]],     "first(CHANNEL)", 0,          Same)
    demo([[0,1,2]], "first(CHANNEL)", 0,          Same)
    
#firstDemo()

# === LIST OPERATIONS, whole chain operations ============================================

def copyDemo():
    print("============== copy ===============================================")
    demo([], "copy(CHANNEL0, CHANNEL1)", None, Same)
    demo([[1,2,3],[10,11,12,13],[100,101]], "copy(CHANNEL0, CHANNEL1)", None,
         [[1,2,3],[1,2,3],[100,101]])
    demo([[1,2,3],[10,11,12,13],[100,101]], "copy(CHANNEL1, CHANNEL0)", None,
         [[10,11,12,13],[10,11,12,13],[100,101]])
    
#copyDemo()

def moveDemo():
    print("============== move ===============================================")
    demo([[],[10,11,12,13]],                "move(CHANNEL0, CHANNEL1)", None,
         [[],[]])
    demo([[1,2,3],[10,11,12,13],[101,102]], "move(CHANNEL0, CHANNEL1)", None,
         [[],[1,2,3],[101,102]])
    demo([[1,2,3],[10,11,12,13],[101,102]], "move(CHANNEL1, CHANNEL0)", None,
         [[10,11,12,13],[],[101,102]])

#moveDemo()

def swapDemo():
    print("============== swap ===============================================")
    demo([],                                "swap(CHANNEL0, CHANNEL1)", None,
         Same)
    demo([[1,2,3],[10,11,12,13],[100,101]], "swap(CHANNEL0, CHANNEL1)", None,
         [[10,11,12,13],[1,2,3],[100,101]])
    demo([[1,2,3],[10,11,12,13],[100,101]], "swap(CHANNEL1, CHANNEL0)", None,
         [[10,11,12,13],[1,2,3],[100,101]])
    demo([[1,2,3],[11,12,13],[100,101]],    "swap(CHANNEL1, CHANNEL0)", None,
         [[11,12,13],[1,2,3],[100,101]])

#swapDemo()

def setAllDemo(): 
    print("============== setAll =============================================")
    demo([],        "setAll(CHANNEL0, 0)", None, Same)
    demo([[1]],     "setAll(CHANNEL0, 0)", None, [[0]])
    demo([[1,2,3]], "setAll(CHANNEL0, 0)", None, [[0,0,0]])

#setAllDemo()

def memberDemo(): 
    print("============== member =============================================")
    demo([],        "member(CHANNEL0, 0)", False, Same)
    demo([[1]],
         "member(CHANNEL0, 0)", False, Same,
         "member(CHANNEL0, 1)", True,  Same
        )
    demo([[1,2,3]],
         "member(CHANNEL0, 0)", False, Same,
         "member(CHANNEL0, 1)", True,  Same,
         "member(CHANNEL0, 2)", True,  Same,
         "member(CHANNEL0, 3)", True,  Same
        )

#memberDemo()

# --- LIST OPERATIONS, top operations --------------------------------------------------

def addFirstDemo(): 
    print("============== addFirst/push ======================================")
    demo([],        "addFirst(CHANNEL0, 0)", None, [[0]])
    demo([[1]],     "addFirst(CHANNEL0, 0)", None, [[0,1]])
    demo([[1,2,3]], "addFirst(CHANNEL0, 0)", None, [[0,1,2,3]])
    
#addFirstDemo()

def addFirstPoorDemo(): 
    print("============== addFirstPoor ======================================")
    demo([],        "addFirstPoor(CHANNEL0, 0)", None, [[0]])
    demo([[1]],     "addFirstPoor(CHANNEL0, 0)", None, [[0,1]])
    demo([[1,2,3]], "addFirstPoor(CHANNEL0, 0)", None, [[0,1,2,3]])

#addFirstPoorDemo()

def removeGetFirstDemo(): 
    print("============== removeGetFirst/pull ================================")
    demo([],        "removeGetFirst(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "removeGetFirst(CHANNEL0)", 0,          [[]])
    demo([[0,1,2]], "removeGetFirst(CHANNEL0)", 0,          [[1,2]])

#removeGetFirstDemo()
    
def replaceGetFirstDemo():
    print("============== replaceGetFirst ====================================")
    demo([],        "replaceGetFirst(CHANNEL0, 0)", EmptyError, Same)
    demo([[0]],     "replaceGetFirst(CHANNEL0, 1)", 0,          [[1]])
    demo([[1,2,3]], "replaceGetFirst(CHANNEL0, 0)", 1,          [[0,2,3]])

#replaceGetFirstDemo()

# --- LIST OPERATIONS, bottom operations ---------------------------------------------------

def lastDemo():
    print("============== last ===============================================")
    demo([],        "last(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "last(CHANNEL0)", 0,          Same)
    demo([[0,1,2]], "last(CHANNEL0)", 2,          Same)

#lastDemo()
    
def addLastDemo():
    print("============== addLast ============================================")
    demo([],        "addLast(CHANNEL0, 0)", None, [[0]])
    demo([[1]],     "addLast(CHANNEL0, 0)", None, [[1,0]])
    demo([[3,2,1]], "addLast(CHANNEL0, 0)", None, [[3,2,1,0]])
    
#addLastDemo()
    
def removeLastDemo():
    print("============== removeLast =========================================")
    demo([],        "removeLast(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "removeLast(CHANNEL0)", None,       [[]])
    demo([[0,1,2]], "removeLast(CHANNEL0)", None,       [[0,1]])

#removeLastDemo()
    
def removeGetLastDemo():
    print("============== removeGetLast ======================================")
    demo([],        "removeGetLast(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "removeGetLast(CHANNEL0)", 0,          [[]])
    demo([[0,1,2]], "removeGetLast(CHANNEL0)", 2,          [[0,1]])

#removeGetLastDemo()
    
def replaceLastDemo():
    print("============== replaceLast ========================================")
    demo([],        "replaceLast(CHANNEL0, 0)", EmptyError, [])
    demo([[0]],     "replaceLast(CHANNEL0, 1)", None,       [[1]])
    demo([[0,1,2]], "replaceLast(CHANNEL0, 3)", None,       [[0,1,3]])

#replaceLastDemo()
    
def replaceGetLastDemo():
    print("============== replaceGetLast =====================================")
    demo([],        "replaceGetLast(CHANNEL0, 0)", EmptyError, Same)
    demo([[0]],     "replaceGetLast(CHANNEL0, 1)", 0,          [[1]])
    demo([[0,1,2]], "replaceGetLast(CHANNEL0, 3)", 2,          [[0,1,3]])
    
#replaceGetLastDemo()

# --- LIST OPERATIONS, rotations ---------------------------------------------------------
    
def rotateDownDemo():
    print("============== rotateDown =========================================")
    demo([],        "rotateDown(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "rotateDown(CHANNEL0)", 0,          Same)
    demo([[0,1]],   "rotateDown(CHANNEL0)", 0,          [[1,0]])
    demo([[0,1,2]], "rotateDown(CHANNEL0)", 0,          [[1,2,0]])

#rotateDownDemo()
    
def rotateUpDemo():
    print("============== rotateUp ===========================================")
    demo([],        "rotateUp(CHANNEL0)", EmptyError, Same)
    demo([[0]],     "rotateUp(CHANNEL0)", 0,          Same)
    demo([[0,1]],   "rotateUp(CHANNEL0)", 1,          [[1,0]])
    demo([[0,1,2]], "rotateUp(CHANNEL0)", 2,          [[2,0,1]])

#rotateUpDemo()

# --- LIST OPERATIONS, reverse -----------------------------------------------------------

def reverseSimplestDemo(): 
    print("============== reverseSimplest ========================================")
    demo([[],[1,1,1]],    "reverseSimplest(CHANNEL0,CHANNEL1)", None, [[],[]])
    demo([[1],[]],        "reverseSimplest(CHANNEL0,CHANNEL1)", None, [[],[1]])
    demo([[2,1],[]],      "reverseSimplest(CHANNEL0,CHANNEL1)", None, [[],[1,2]])
    demo([[3,2,1],[0]],   "reverseSimplest(CHANNEL0,CHANNEL1)", None, [[],[1,2,3]])
    demo([[4,3,2,1],[0]], "reverseSimplest(CHANNEL0,CHANNEL1)", None, [[],[1,2,3,4]])

#reverseSimplestDemo()

def reverseSimpleDemo(): 
    print("============== reverseSimple ============================================")
    demo([[],[1,1,1]],    "reverseSimple(CHANNEL0,CHANNEL1)", None, [[],[]])
    demo([[1],[]],        "reverseSimple(CHANNEL0,CHANNEL1)", None, [[],[1]])
    demo([[2,1],[]],      "reverseSimple(CHANNEL0,CHANNEL1)", None, [[],[1,2]])
    demo([[3,2,1],[0]],   "reverseSimple(CHANNEL0,CHANNEL1)", None, [[],[1,2,3]])
    demo([[4,3,2,1],[0]], "reverseSimple(CHANNEL0,CHANNEL1)", None, [[],[1,2,3,4]])

#reverseSimpleDemo()

def reverseDemo(): 
    print("============== reverse ============================================")
    demo([[],[1,1,1]],    "reverse(CHANNEL0,CHANNEL1)", None, [[],[]])
    demo([[1],[]],        "reverse(CHANNEL0,CHANNEL1)", None, [[],[1]])
    demo([[2,1],[]],      "reverse(CHANNEL0,CHANNEL1)", None, [[],[1,2]])
    demo([[3,2,1],[0]],   "reverse(CHANNEL0,CHANNEL1)", None, [[],[1,2,3]])
    demo([[4,3,2,1],[0]], "reverse(CHANNEL0,CHANNEL1)", None, [[],[1,2,3,4]])

#reverseDemo()

    
# === ORDER OPERATIONS =========================================================

def minimumDemo():
    print("============== minimum ============================================")
    demo([],        "minimum(CHANNEL)", EmptyError, Same)
    demo([[1]],     "minimum(CHANNEL)", 1,          Same)
    demo([[1,2]],   "minimum(CHANNEL)", 1,          Same)
    demo([[2,1]],   "minimum(CHANNEL)", 1,          Same)
    demo([[1,2,3]], "minimum(CHANNEL)", 1,          Same)
    demo([[2,1,3]], "minimum(CHANNEL)", 1,          Same)
    demo([[3,2,1]], "minimum(CHANNEL)", 1,          Same)

#minimumDemo()

def memberNonDecreasingDemo():
    print("============== memberNonDecreasing ================================")
    demo([],          "memberNonDecreasing(CHANNEL, 0)", False, Same)
    demo([[1]],
         "memberNonDecreasing(CHANNEL, 0)", False, Same,
         "memberNonDecreasing(CHANNEL, 1)", True,  Same,
         "memberNonDecreasing(CHANNEL, 2)", False, Same
        )
    demo([[1,3,3,5]],
         "memberNonDecreasing(CHANNEL, 0)", False, Same,
         "memberNonDecreasing(CHANNEL, 1)", True,  Same,
         "memberNonDecreasing(CHANNEL, 2)", False, Same,
         "memberNonDecreasing(CHANNEL, 3)", True,  Same,
         "memberNonDecreasing(CHANNEL, 4)", False, Same,
         "memberNonDecreasing(CHANNEL, 5)", True,  Same,
         "memberNonDecreasing(CHANNEL, 6)", False, Same
        )

#memberNonDecreasingDemo()

def insertNonDecreasingDemo():
    DETAILED = False
    print("============== insertNonDecreasing ================================")
    chain = ChainController()
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 0):")
    chain.insertNonDecreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 0):")
    chain.insertNonDecreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 2):")
    chain.insertNonDecreasing(CHANNEL, 2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 0):")
    chain.insertNonDecreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 1):")
    chain.insertNonDecreasing(CHANNEL, 1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 2):")
    chain.insertNonDecreasing(CHANNEL, 2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3])
    chain.report(detailed=DETAILED)
    print("insertNonDecreasing(CHANNEL, 4):")
    chain.insertNonDecreasing(CHANNEL, 4)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#insertNonDecreasingDemo()

def insertUniqueIncreasingDemo():
    DETAILED = False
    print("============== insertUniqueIncreasingDemo =========================")
    chain = ChainController()
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 0):")
    chain.insertUniqueIncreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 0):")
    chain.insertUniqueIncreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 1):")
    chain.insertUniqueIncreasing(CHANNEL, 1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 2):")
    chain.insertUniqueIncreasing(CHANNEL, 2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 0):")
    chain.insertUniqueIncreasing(CHANNEL, 0)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 1):")
    chain.insertUniqueIncreasing(CHANNEL, 1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 2):")
    chain.insertUniqueIncreasing(CHANNEL, 2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("insertUniqueIncreasing(CHANNEL, 3):")
    chain.insertUniqueIncreasing(CHANNEL, 3)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#insertUniqueIncreasingDemo()

def insertAllNonDecreasingSimpleDemo():
    DETAILED = False
    print("============== insertAllNonDecreasingSimpleDemo ============================")
    chain = ChainController([],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([],[1])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2],[1])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1],[2])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([5,1,3],[2,4])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([5,3,1],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasingSimple(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#insertAllNonDecreasingSimpleDemo()

def insertAllNonDecreasingDemo():
    DETAILED = False
    print("============== insertAllNonDecreasingDemo ============================")
    chain = ChainController([],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([],[1])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2],[1])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1],[2])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([5,1,3],[2,4])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([5,3,1],[])
    chain.report(detailed=DETAILED)
    print("insertAllNonDecreasing(CHANNEL0, CHANNEL1):")
    chain.insertAllNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#insertAllNonDecreasingDemo()

def iSortDemo(): 
    DETAILED = False
    print("============== iSort ======================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,2])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,2])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,3])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,3,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,1,2])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,2,1])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,4,1,5,2,3])
    chain.report(detailed=DETAILED)
    print("iSort")
    chain.iSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#iSortDemo()


def sSortDemo():
    DETAILED = False
    print("============== selection sort - sSort ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("sSortg")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,2])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,2])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,3])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,3,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,1,2])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,2,1])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,4,1,5,2,3])
    chain.report(detailed=DETAILED)
    print("sSort")
    chain.sSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#sSortDemo()


def bSortDemo():
    DETAILED = True
    print("============== bSort ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,1,2])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,2])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,1,3])
    chain.report(detailed=DETAILED)
    print(" bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,3,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,1,2])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,2,1])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([2,4,1,5,2,3])
    chain.report(detailed=DETAILED)
    print("bSort")
    chain.bSort(CHANNEL)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#bSortDemo()


def mergeNonDecreasingSimpleDemo():
    DETAILED = False
    print("============== mergeNonDecreasingSimple ===========================")
    chain = ChainController([],[],[100, 101])
    chain.report(detailed=True)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3],[],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([],[1,2,3],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[0,2,4],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5,7],[2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5,7],[4,6,8],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,5,7],[0,2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[0,2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasingSimple")
    chain.mergeNonDecreasingSimple(CHANNEL0, CHANNEL1, CHANNEL2)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    
#mergeNonDecreasingSimpleDemo()

def mergeNonDecreasingDemo():
    DETAILED = False
    print("============== mergeNonDecreasing =============================")
    chain = ChainController([],[],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3],[],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([],[1,2,3],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[0,2,4],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5,7],[2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5,7],[4,6,8],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([3,5,7],[0,2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,3,5],[0,2,4,6],[100, 101])
    chain.report(detailed=DETAILED)
    print("mergeNonDecreasing")
    chain.mergeNonDecreasing(CHANNEL0, CHANNEL1)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#mergeNonDecreasingDemo()

# === INDEXING OPERATIONS =================================================

def lengthDemo():
    print("========= length ====================================================")
    demo([[]],      "length(CHANNEL)", 0, Same)
    demo([[1]],     "length(CHANNEL)", 1, Same)
    demo([[1,2]],   "length(CHANNEL)", 2, Same)
    demo([[1,2,3]], "length(CHANNEL)", 3, Same)
    
#lengthDemo()

def getItemDemo():
    print("========= getItem ====================================================")
    demo([[1]],        "getItem(CHANNEL,0)", 1,          Same)
    demo([[10,11]],    "getItem(CHANNEL,0)", 10,         Same)
    demo([[10,11]],    "getItem(CHANNEL,1)", 11,         Same)
    demo([[10,11,12]], "getItem(CHANNEL,2)", 12,         Same)
    demo([[]],         "getItem(CHANNEL,0)", IndexError, Same)
    demo([[10,11,12]], "getItem(CHANNEL,3)", IndexError, Same)
    demo([[10,11,12]], "getItem(CHANNEL,5)", IndexError, Same)

#getItemDemo()

def setItem0Demo():
    print("========= setItem0 ====================================================")
    demo([[10]],       "setItem0(CHANNEL,0,100)", None, [[100]])
    demo([[10,11]],    "setItem0(CHANNEL,0,100)", None, [[100,11]])
    demo([[10]],       "setItem0(CHANNEL,1,111)", None, [[10]])
    demo([[10,11,12]], "setItem0(CHANNEL,2,112)", None, [[10,11,112]])
    demo([[10,11,12]], "setItem0(CHANNEL,3,113)", None, [[10,11,12]])
    demo([[10,11,12]], "setItem0(CHANNEL,5,115)", None, [[10,11,12]])

#setItem0Demo()

def setItemDemo():
    print("========= setItem ====================================================")
    demo([[10]],       "setItem(CHANNEL, 0, 100)", None,       [[100]])
    demo([[10,11]],    "setItem(CHANNEL, 0, 100)", None,       [[100,11]])
    demo([[10]],       "setItem(CHANNEL, 1, 111)", IndexError, [[10]])
    demo([[10,11,12]], "setItem(CHANNEL, 2, 112)", None,       [[10,11,112]])
    demo([[10,11,12]], "setItem(CHANNEL, 3, 113)", IndexError, [[10,11,12]])
    demo([[10,11,12]], "setItem(CHANNEL, 5, 115)", IndexError, [[10,11,12]])

#setItemDemo()

def getSetItemDemo():
    print("========= getSetItem ====================================================")
    demo([[10]],       "getSetItem(CHANNEL, 0, 100)", 10,         [[100]])
    demo([[10,11]],    "getSetItem(CHANNEL, 1, 111)", 11,         [[10,111]])
    demo([[10,11]],    "getSetItem(CHANNEL, 1, 111)", 11,         [[10,111]])
    demo([[10,11,12]], "getSetItem(CHANNEL, 2, 112)", 12,         [[10,11,112]])
    demo([[10,11,12]], "getSetItem(CHANNEL, 3, 113)", IndexError, [[10,11,12]])
    demo([[10,11,12]], "getSetItem(CHANNEL, 5, 115)", IndexError, [[10,11,12]])

#getSetItemDemo()

def memberIndexDemo():
    print("========= memberIndex ====================================================")
    demo([[]],         "memberIndex(CHANNEL,  3)", ValueError, Same)
    demo([[10]],       "memberIndex(CHANNEL, 10)", 0,          Same)
    demo([[10]],       "memberIndex(CHANNEL, 11)", ValueError, Same)
    demo([[10,11]],    "memberIndex(CHANNEL, 10)", 0,          Same)
    demo([[10,11]],    "memberIndex(CHANNEL, 11)", 1,          Same)
    demo([[10,11]],    "memberIndex(CHANNEL, 12)", ValueError, Same)
    demo([[10,10]],    "memberIndex(CHANNEL, 10)", 0,          Same)
    demo([[10,11,12]], "memberIndex(CHANNEL, 10)", 0,          Same)
    demo([[10,11,12]], "memberIndex(CHANNEL, 11)", 1,          Same)
    demo([[10,11,12]], "memberIndex(CHANNEL, 12)", 2,          Same)
    demo([[10,11,12]], "memberIndex(CHANNEL, 13)", ValueError, Same)
    demo([[10,10,11]], "memberIndex(CHANNEL, 10)", 0,          Same)
    demo([[10,11,11]], "memberIndex(CHANNEL, 11)", 1,          Same)

#memberIndexDemo()
    
def insertAtIndex0Demo():
    print("========= inserAtIndex0 ====================================================")
    demo([[]],      "insertAtIndex0(CHANNEL, 0,  13)", None, Same)
    demo([[]],      "insertAtIndex0(CHANNEL, 1,  13)", None, Same)
    demo([[10]],    "insertAtIndex0(CHANNEL, 0, 100)", None, [[100,10]])
    demo([[10]],    "insertAtIndex0(CHANNEL, 1, 100)", None, Same)
    demo([[10,11]], "insertAtIndex0(CHANNEL, 0, 100)", None, [[100,10,11]])
    demo([[10,11]], "insertAtIndex0(CHANNEL, 1, 110)", None, [[10,110,11]])
    demo([[10,11]], "insertAtIndex0(CHANNEL, 2, 120)", None, Same)

#insertAtIndex0Demo()

def insertAtIndexDemo():
    print("========= insertAtIndex ====================================================")
    demo([[]],      "insertAtIndex(CHANNEL, 0,  13)", IndexError, Same)
    demo([[]],      "insertAtIndex(CHANNEL, 1,  13)", IndexError, Same)
    demo([[10]],    "insertAtIndex(CHANNEL, 0, 100)", None,       [[100,10]])
    demo([[10]],    "insertAtIndex(CHANNEL, 1, 100)", IndexError, [[10]])
    demo([[10,11]], "insertAtIndex(CHANNEL, 0, 100)", None,       [[100,10,11]])
    demo([[10,11]], "insertAtIndex(CHANNEL, 1, 110)", None,       [[10,110,11]])
    demo([[10,11]], "insertAtIndex(CHANNEL, 2, 120)", IndexError, [[10,11]])

#insertAtIndexDemo()
    
def deleteAtIndexDemo():
    print("========= deleteAtIndex ====================================================")
    demo([[]],      "deleteAtIndex(CHANNEL, 0)", None, Same)
    demo([[]],      "deleteAtIndex(CHANNEL, 1)", None, Same)
    demo([[10]],    "deleteAtIndex(CHANNEL, 0)", None, [[]])
    demo([[10]],    "deleteAtIndex(CHANNEL, 1)", None, Same)
    demo([[10,11]], "deleteAtIndex(CHANNEL, 0)", None, [[11]])
    demo([[10,11]], "deleteAtIndex(CHANNEL, 1)", None, [[10]])
    demo([[10,11]], "deleteAtIndex(CHANNEL, 2)", None, [[10,11]])

#deleteAtIndexDemo()

def deleteGetAtIndexDemo():
    print("========= deleteGetAtIndex ====================================================")
    demo([[]],      "deleteGetAtIndex(CHANNEL, 0)", IndexError, Same)
    demo([[]],      "deleteGetAtIndex(CHANNEL, 1)", IndexError, Same)
    demo([[10]],    "deleteGetAtIndex(CHANNEL, 0)", 10,         [[]])
    demo([[10]],    "deleteGetAtIndex(CHANNEL, 1)", IndexError, Same)
    demo([[10,11]], "deleteGetAtIndex(CHANNEL, 0)", 10,         [[11]])
    demo([[10,11]], "deleteGetAtIndex(CHANNEL, 1)", 11,         [[10]])
    demo([[10,11]], "deleteGetAtIndex(CHANNEL, 2)", IndexError, [[10,11]])

#deleteGetAtIndexDemo()

# ==== LOADERS AND UNLOADERS ===================================================

def loadWordsSimpleDemo():
    DETAILED = False
    print("========= loadWordsSimple ====================================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsSimple(CHANNEL, [1,2,3]):")
    chain.loadWordsSimple(CHANNEL, [1,2,3])
    chain.report(detailed=DETAILED)
    print()

    print("loadWordsSimple(CHANNEL, []):")
    chain.loadWordsSimple(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsSimpleDemo()

def loadWordsDemo():
    DETAILED = False
    print("========= loadWords ====================================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWords(CHANNEL, [1,2,3]):")
    chain.loadWords(CHANNEL, [1,2,3])
    chain.report(detailed=DETAILED)
    print()

    print("loadWords(CHANNEL, []):")
    chain.loadWords(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsDemo()

def loadWordsReverseSimpleDemo():
    DETAILED = False
    print("========= loadWordsReverseSimple =============================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverseSimple(CHANNEL, []):")
    chain.loadWordsReverseSimple(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverseSimple(CHANNEL, [1]):")
    chain.loadWordsReverseSimple(CHANNEL, [1])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverseSimple(CHANNEL, [1,2]):")
    chain.loadWordsReverseSimple(CHANNEL, [1,2])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverseSimple(CHANNEL, [1,2,3,4,5]):")
    chain.loadWordsReverseSimple(CHANNEL, [1,2,3,4,5])
    chain.report(detailed=DETAILED)
    print("loadWordsReverseSimple(CHANNEL, [1,2]):")
    chain.loadWordsReverseSimple(CHANNEL, [1,2])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    
#loadWordsReverseSimpleDemo()
    
def loadWordsReverseDemo():
    DETAILED = False
    print("========= loadWordsReverse =============================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverse(CHANNEL, []):")
    chain.loadWordsReverse(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverse(CHANNEL, [1]):")
    chain.loadWordsReverse(CHANNEL, [1])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverse(CHANNEL, [1,2]):")
    chain.loadWordsReverse(CHANNEL, [1,2])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("loadWordsReverse(CHANNEL, [1,2,3,4,5]):")
    chain.loadWordsReverse(CHANNEL, [1,2,3,4,5])
    chain.report(detailed=DETAILED)
    print("loadWordsReverse(CHANNEL, [1,2]):")
    chain.loadWordsReverse(CHANNEL, [1,2])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    
#loadWordsReverseDemo()

def loadWordsNonDecreasingSimpleDemo():
    DETAILED = False
    print("============== loadWordsNonDecreasingSimpleDemo ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsNonDecreasingSimple(CHANNEL, [2,4,1,5,2,3]):")
    chain.loadWordsNonDecreasingSimple(CHANNEL, [2,4,1,5,2,3])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsNonDecreasingeSimple(CHANNEL, []):")
    chain.loadWordsNonDecreasingSimple(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsNonDecreasingSimpleDemo()

def loadWordsNonDecreasingDemo():
    DETAILED = False
    print("============== loadWordsNonDecreasingDemo ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsNonDecreasing(CHANNEL, [2,4,1,5,2,3]):")
    chain.loadWordsNonDecreasing(CHANNEL, [2,4,1,5,2,3])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsNonDecreasinge(CHANNEL, []):")
    chain.loadWordsNonDecreasing(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsNonDecreasingDemo()

def loadWordsUniqueIncreasingSimpleDemo():
    DETAILED = False
    print("============== loadWordsUniqueIncreasingSimpleDemo ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsUniqueIncreasingSimple(CHANNEL, [2,4,1,3,5,2,3,1]):")
    chain.loadWordsUniqueIncreasingSimple(CHANNEL, [2,4,1,3,5,2,3,1])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsUniqueIncreasingSimple(CHANNEL, []):")
    chain.loadWordsUniqueIncreasingSimple(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsUniqueIncreasingSimpleDemo()

def loadWordsUniqueIncreasingDemo():
    DETAILED = False
    print("============== loadWordsUniqueIncreasingDemo ============================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsUniqueIncreasing(CHANNEL, [2,4,1,3,5,2,3,1]):")
    chain.loadWordsUniqueIncreasing(CHANNEL, [2,4,1,3,5,2,3,1])
    chain.report(detailed=DETAILED)
    print()
    print("loadWordsUniqueIncreasing(CHANNEL, []):")
    chain.loadWordsUniqueIncreasing(CHANNEL, [])
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#loadWordsUniqueIncreasingDemo()

def unloadWordsDemo(): 
    DETAILED = False
    print("========= unloadWords ==================================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("unloadWords:")
    for item in chain.unloadWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("unloadWords:")
    for item in chain.unloadWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED); print()
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("unloadWords:")
    for item in chain.unloadWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED); print()
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3])
    chain.report(detailed=DETAILED)
    print("unloadWords:")
    for item in chain.unloadWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED); print()
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadWordsDemo()

def unloadAllWordsDemo(): 
    DETAILED = False
    print("========= unloadAllWords =======================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("unloadAllWords:")
    for item in chain.unloadAllWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3])
    chain.report(detailed=DETAILED)
    print("unloadAllWords:")
    for item in chain.unloadAllWords(CHANNEL):
        print(item)
    chain.report(detailed=DETAILED); print()
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadAllWordsDemo()  

def unloadWordsReverseComponentsDemo():
    DETAILED = False
    print("============== unloadWordsReverse components =========================")
    chain = ChainController([1,2,3,4,5])
    print("chain:")
    chain.report(detailed=DETAILED); print()

    empty = chain.moveLast(CHANNEL, AUX)
    print("copyLast =", empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()
    
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5])
    print("chain:")
    chain.report(detailed=DETAILED); print()

    data, empty = chain.unloadWordsReverseBegin(CHANNEL, AUX)
    print("unloadWordsReverseBegin =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()

    data, empty = chain.pullEnd(CHANNEL, AUX)
    print("pullEnd =", data, empty)
    chain.report(detailed=DETAILED); print()
    
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadWordsReverseComponentsDemo()

def unloadWordsReverseSimpleDemo(): 
    DETAILED = False
    print("============== unloadWordsReverseSimple ====================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("iterating over []:")
    for item in chain.unloadWordsReverseSimple(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("iterating over [1]:")
    for item in chain.unloadWordsReverseSimple(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5])
    chain.report(detailed=DETAILED)
    print("iterating over [1,2,3,4,5]:")
    for item in chain.unloadWordsReverseSimple(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5,6])
    chain.report(detailed=DETAILED)
    print("iterating over [1,2,3,4,5,6]:")
    for item in chain.unloadWordsReverseSimple(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadWordsReverseSimpleDemo()

def unloadWordsReverseDemo(): 
    DETAILED = False
    print("============== unloadWordsReverse ====================================")
    chain = ChainController([])
    chain.report(detailed=DETAILED)
    print("iterating over []:")
    for item in chain.unloadWordsReverse(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("iterating over [1]:")
    for item in chain.unloadWordsReverse(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5])
    chain.report(detailed=DETAILED)
    print("iterating over [1,2,3,4,5]:")
    for item in chain.unloadWordsReverse(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5,6])
    chain.report(detailed=DETAILED)
    print("iterating over [1,2,3,4,5,6]:")
    for item in chain.unloadWordsReverse(CHANNEL, AUX):
        print(item)
        chain.report(detailed=DETAILED)
    print("Done")
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadWordsReverseDemo()
    
def unloadAllWordsReverseDemo(): 
    DETAILED = False
    print("============== unloadAllWordsReverse ======================================")

    chain = ChainController([])
    print("iterating:")
    for item in chain.unloadAllWordsReverse(CHANNEL, AUX):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1])
    chain.report(detailed=DETAILED)
    print("iterating:")
    for item in chain.unloadAllWordsReverse(CHANNEL, AUX):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2])
    chain.report(detailed=DETAILED)
    print("iterating:")
    for item in chain.unloadAllWordsReverse(CHANNEL, AUX):
        print(item)
    chain.report(detailed=DETAILED)
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5])
    chain.report(detailed=DETAILED)
    print("iterating:")
    for item in chain.unloadAllWordsReverse(CHANNEL, AUX):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")
    chain = ChainController([1,2,3,4,5,6])
    chain.report(detailed=DETAILED)
    print("iterating:")
    for item in chain.unloadAllWordsReverse(CHANNEL, AUX):
        print(item)
    chain.report(detailed=DETAILED)
    chain.stop()
    print("-------------------------------------------------------------------")

#unloadAllWordsReverseDemo()

# ==== ARITHMETIC ==============================================================
    
def loadIntegerDemo():
    DETAILED = True
    print("========== loadInteger, report, register2... ======================")
    chain = ChainController([])
    
    chain.loadInteger(CHANNEL, [0b00,0b01,0b10,0b11])
    print("loadInteger(CHANNEL, [0b00,0b01,0b10,0b11])")
    
    print()
    chain.report(base=5, detailed=DETAILED)
    print()
    chain.report(base=2, detailed=DETAILED)
    print()
    chain.report(base=4, detailed=DETAILED)
    print()
    chain.report(base=8, detailed=DETAILED)
    print()
    chain.report(base=16, detailed=DETAILED)
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL, [0b00,0b00,0b01])
    print("loadInteger(CHANNEL, [0b00,0b00,0b01]")
    chain.report(base=4, detailed=DETAILED)
    
    print()
    print("register2list base=10:", chain.register2list(CHANNEL))
    print("register2list base=2:", chain.register2list(CHANNEL, base=2))
    print("register2list base=4:", chain.register2list(CHANNEL, base=4))
    print("register2list base=8:", chain.register2list(CHANNEL, base=8))
    print("register2list base=16:", chain.register2list(CHANNEL, base=16))
    print()
    print("register2integer base=10", chain.register2integer(CHANNEL, base=10))
    print("register2integer base=2", chain.register2integer(CHANNEL, base=2))
    print("register2integer base=4", chain.register2integer(CHANNEL, base=4))
    print("register2integer base=8", chain.register2integer(CHANNEL, base=8))
    print("register2integer base=16", chain.register2integer(CHANNEL, base=16))
    
    chain.stop()

#loadIntegerDemo()

#NEEDS WORK
    
def equalDemo():
    DETAILED = True
    print("============== equal ======================================")
    chain = ChainController([])
    
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("equal =", chain.equal(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("equal =", chain.equal(CHANNEL0, CHANNEL1), "(False)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10])
    chain.report(detailed=DETAILED)
    print("equal =", chain.equal(CHANNEL0, CHANNEL1), "(False)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b11,0b11])
    chain.report(detailed=DETAILED)
    print("equal =", chain.equal(CHANNEL0, CHANNEL1), "(False)")
    
    chain.stop()

# equalDemo()

    
def lessOrEqualDemo():
    DETAILED = True
    print("============== lessOrEqual ======================================")
    chain = ChainController([])
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("lessOrEqual =", chain.lessOrEqual(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("lessOrEqual =", chain.lessOrEqual(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10])
    chain.report(detailed=DETAILED)
    print("lessOrEqual =", chain.lessOrEqual(CHANNEL0, CHANNEL1), "(False)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b11,0b11])
    chain.report(detailed=DETAILED)
    print("lessOrEqual =", chain.lessOrEqual(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b11,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("lessOrEqual =", chain.lessOrEqual(CHANNEL0, CHANNEL1), "(False)")

    chain.stop()

#lessOrEqualDemo()

def lessDemo():
    DETAILED = True
    print("============== less ======================================")
    chain = ChainController([])
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("less =", chain.less(CHANNEL0, CHANNEL1), "(False)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("less =", chain.less(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10])
    chain.report(detailed=DETAILED)
    print("less =", chain.less(CHANNEL0, CHANNEL1), "(False)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b10,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b11,0b11])
    chain.report(detailed=DETAILED)
    print("less =", chain.less(CHANNEL0, CHANNEL1), "(True)")
    print("------------------------------------------------------")
    chain.loadInteger(CHANNEL0, [0b00,0b01,0b11,0b11])
    chain.loadInteger(CHANNEL1, [0b00,0b01,0b10,0b11])
    chain.report(detailed=DETAILED)
    print("less =", chain.less(CHANNEL0, CHANNEL1), "(False)")
    
    chain.stop()

#lessDemo()

#===============================================================================

def main():
    pass

    #setupChainDemo()

    # --- LIST OPERATIONS
    
    #stackDemo()
    #queueDemo()
    
    #isEmptyDemo()
    #clearDemo()
    #clear2Demo()
    #firstDemo()
    
    #copyDemo()
    #moveDemo()
    #swapDemo()
    #setAllDemo()
    #memberDemo() 
    
    #addFirstDemo()
    #addFirstLinearDemo()
    #removeGetFirstDemo()
    #replaceGetFirstDemo()
    
    #lastDemo()
    #addLastDemo()
    #removeLastDemo()
    #removeGetLastDemo()
    #replaceLastDemo()
    #replaceGetLastDemo()
    
    #rotateDownDemo()
    #rotateUpDemo()

    #reverseSimplestDemo()
    #reverseSimpleDemo()
    #reverseDemo()
        
    # --- ORDER OPERATIONS
    
    #minimumDemo()
    #memberNonDecreasingDemo()
    #insertNonDecreasingDemo()
    #insertUniqueIncreasingDemo()
    
    #insertAllNonDecreasingDemo()
    #insertAllNonDecreasingSimpleDemo()
    #iSortDemo()
    #sSortDemo()
    #bubbleSortDemo()

    #mergeNonDecreasingSimpleDemo()
    #mergeNonDecreasingDemo()

    # --- INDEXING OPERATIONS

    #lengthDemo()
    # Demo()
    # Demo()
    # Demo()
    # Demo()
    # Demo()
    # Demo()

    # --- LOADERS, UNLOADERS

    #loadWordsSimpleDemo()
    #loadWordsDemo()
    #loadWordsReverseSimpleDemo()
    #loadWordsReverseDemo()
    #loadWordsNonDecreasingSimpleDemo()
    #loadWordsNonDecreasingDemo()
    #loadWordsUniqueIncreasingSimpleDemo()
    #loadWordsUniqueIncreasingDemo()

    #unloadWordsDemo()
    #unloadAllWordsDemo()
    #unloadWordsReverseComponentsDemo()
    #unloadWordsReverseSimpleDemo()
    #unloadWordsReverseDemo()
    #unloadAllWordsReverseDemo()

def multiplication(a,b):
    c = 0
    while b != 0:
        if (b & 1) != 0:
            c = c + a
        a = a << 1
        b = b >> 1
    return c

def addition(a,b):
    while a != 0:
        c = b & a
        b = b ^ a
        c = c << 1
        a = c
    return b    

##for i in range(5):
##    for j in range(5):
##        print(i, j, addition(i,j), multiplication(i,j))

#===============================================================================

if __name__ == "__main__":
    main()

