#!/usr/bin/env python3

"""CHAIN CONTROLLER CLASS"""

# TO DO: enforce word size.
# TO DO: add indexing operations. including insert at index,
#        replace at index, etc.

# ==============================================================================

from chain_1_class_PE import *
import copy

# ==============================================================================

def baseCheck(base):
    if base not in [2,4,8,16,10]:
        print("Warning: report(... base=%s ...) is not valid. " % base +
               "Only 2, 4, 8, 16, 10 are allowed.\n" + 
               "Using base 10 for now.")
        base = 10
    if base != 10:
        log2ofBase = [1,2,4,8,16].index(base)
        if WORD_SIZE % log2ofBase != 0: 
             print("In base %s one cannot show all digits of words of size %s." %
                    (base, WORD_SIZE) +
                    "\nlog_2(base) must divide word size.\n"  +
                    "Using base 10 for now, to show the value.")
             base = 10
        #fieldWidth = WORD_SIZE // log2ofBase # for future use.
    return base

# ==============================================================================
    
class ChainController():

    def __init__(self, *columns):
        if len(columns)==0:
            self.chain = CPE()
            self.connectorLower = self.chain.connectorUpper # NEW
            self.chain.start()
            for channel in range(CHANNELS):
                self.clear(channel)
        else:
            self.chain = ChainController._setupChain(*columns)
            self.connectorLower = self.chain.connectorUpper # NEW
        
    def _setupChain(*columns):
        """Returns self.chain with the specified content.
           Usage: setupChain() or setupChain(list0)
           or setupChain(list1, list2), etc.
           list0 will be loaded into word[1] channel,
           list1 will be loaded into word[2] channel, etc.
           The lists can contain only non-negative integers.
           For debugging only, not a part of the model.
        """
        columnsAux = copy.deepcopy(columns)
        chain = pe = CPE()
        width = CHANNELS
        if len(columnsAux) > width:
            raise ValueError(
                "setupChain: self.chain CPE cannot store more than $s words." % width)
        #columns += ([],)*(width-len(columns)) # bad code - aliasing
        for i in range(width-len(columnsAux)):
            columnsAux += ([],)
        for c in columnsAux:
            c.append(None)
        depth = max(len(c) for c in columnsAux) # max length of a column
        for c in columnsAux:
            c.extend((Any,)*(depth-len(c))) # make sure all columns same length
        for d in range(depth):
            for w in range(width):
                item = columnsAux[w][d]
                if item is None:
                    pe.word[w] = Any
                    pe.bit[w] = True
                elif item is Any:
                    pe.word[w] = Any
                    pe.bit[w] = Any
                else:
                    pe.word[w] = item
                    pe.bit[w] = False
            #pe.aux0 = pe.bit0 = pe.aux1 = pe.bit1 = pe.aux2 = pe.bit2 = Any
            pe.start()
            if d < depth - 1:
                lowerPE = CPE(pe.chainName) # cf. CPE.extend method
                lowerPE.peId = pe.peId+1
                lowerPE.name = pe.chainName + "." + str(lowerPE.peId)
                pe.connectorLower = lowerPE.connectorUpper
                pe = lowerPE
        return chain

    def stop(self):
        """Terminate all the threads/CPE objects in the self.chain. Each one terminates
           after completing all previously requested operations.
           *Not* a part of the self.chain controller interface."""
        self.connectorLower.send_o("stop")
        for t in threading.enumerate():
            if isinstance(t, CPE) and t.chainName==self.chain.chainName:
                t.join()

    def report(self, base=10, detailed=True):
        """For debugging only. Not a part of the model."""
        base = baseCheck(base)
        printOperation = "printRepr" + str(base)
        baseInfo = " Base " + str(base) + "."
        if detailed:
            header = "{:9}".format(baseInfo)
            i = 0
            for channel in range(CHANNELS):
                header += "    word" + str(i) + " empt" + str(i)
                i += 1
            i = 0
            for temp in range(TEMP_SPACE):
                header += "    temp" + str(i) + " empt" + str(i)
                i += 1
            print(header)
            self.connectorLower.send_o(printOperation)
            self.connectorLower.receive_b() # synchronization
            # main thread will not proceed until all threads have printed.
        else:
            header = "{:9}".format(baseInfo)
            i = 0
            for channel in range(CHANNELS):
                header += "    word" + str(i)
                i += 1
            i = 0
            for temp in range(TEMP_SPACE):
                header += "    temp" + str(i)
                i += 1
            print(header)
            self.connectorLower.send_o("printStr")
            self.connectorLower.receive_b() # synchronization
            # main thread will not proceed until all threads have printed.
        #time.sleep(delay)

    def chain2list(self, channel, base=10):
        """For debugging only. Not a part of the model.
           Returns a list equivalent to the specified channel,
           or None if the channel is not properly terminated."""
        global global_chain2list # global object (not global variable)
        global_chain2list.clear() # do not use global_chain2list = []
        self.connectorLower.send_o("chain2list", channel)
        badEnding = self.connectorLower.receive_b() # synchronization
        # main thread will not proceed until all threads updated global_chain2list.
        if badEnding:
            return None
        else:
            return global_chain2list

    def chain2lists(self, base=10):
        """For debugging only. Not a part of the model.
           Returns a list of 3 items.
           Each item is the list sotred in a channel of the chain
           or None if the channel is not properly terminated."""
        lists = []
        for channel in range(CHANNELS):
            lists.append(self.chain2list(channel, base=base).copy())
        return lists

    def register2list(self, channel, base=10):
        """For debugging only. Not a part of the model.
           Returns a list of words representing an integer in the channel,
           or None if the integer is not properly terminated.
           The least significant word is first in the list.
           If base==10, the list items are integers;
           ohterwise they are strings of digits."""
        global global_chain2list # global object (not global variable)
        global_chain2list.clear() # do not use global_chain2list = []
        self.connectorLower.send_o("register2list", channel)
        badEnding = self.connectorLower.receive_b() # synchronization
        # main thread will not proceed until all threads updated global_chain2list.
        if badEnding:
            return None
        base = baseCheck(base)
        if base == 10:
            return global_chain2list.copy()
        else:
            result = []
            for v in global_chain2list:
                result.append(number2string(v, base))
            return result

    def register2integer(self, channel, base=10):
        """For debugging only. Not a part of the model.
           Returns an integer represented by the words in the channel,
           or None if the integer is not properly terminated.
           The least significnt word is first in the list.
           If base==10, the returned value is an integer;
           ohterwise it is a string of digits."""
        wordList = self.register2list(channel)
        if wordList is None:
            return None
        wordList.reverse()
        result = 0
        for word in wordList:
            result = result * 2**WORD_SIZE + word
        base = baseCheck(base)
        if base == 10: 
            return result
        else:
            return number2string(result, base)
            
    # ==============================================================================
              
    # stack: isEmpty, clear, top, push, pop. 
    # queue: isEmpty, clear, first, enqueue, dequeue, rotate.
    # deque: isEmpty, clear, first, last, addFirst, addLast, 
    #        removeFirst, removeLast, removeGetFirst, removeGetLast,
    #        replaceFirst, replaceLast, replaceGetFirst, replaceGetLast,
    #        rotateDown, rotateUp.
    # list:  all the deque operations, member, reverse, sort, merge, ...

    # === LIST OPERATIONS, top CPE operations =========================================

    def isEmpty(self, channelA):
        """Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # none       -
        #            -
        #            b
        # isEmpty(A) ^ 
        self.connectorLower.send_o("isEmpty", channelA)
        empty = self.connectorLower.receive_b()
        return empty

    # ------------------------------------------------------------------------------
    def clear(self, channelA):
        """Makes the channel empty.
           Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # none
        #
        # 
        # clear(A)
        self.connectorLower.send_o("clear", channelA)
        
    def clear2(self, channelA, channelB):
        """Makes the two channels empty.
           Equivalent to: clear(channelA); clear(channelB).
           Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # none
        # 
        # 
        # clear2(A,B)
        self.connectorLower.send_o("clear2", channelA, channelB)

    # ------------------------------------------------------------------------------
    def first(self, channelA):
        """Returns the first/top word from the channel or raises EmptyError.
           Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # none     - 
        #          -
        #          W
        # first(A) ^ 
        self.connectorLower.send_o("first", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
                "first: Cannot peek at first item in empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word

    top = first 

    # === LIST OPERATIONS, whole chain operations =========================================

    def copy(self, channelA, resultChannel): 
        """Copies channelA to resultChannel.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none
        # 
        # 
        # copy(A,R)
        self.connectorLower.send_o("copy", channelA, resultChannel)

    # ------------------------------------------------------------------------------
    def move(self, channelA, resultChannel): 
        """Moves words from channelA to resultChannel. Leaves channelA empty.
           Equivalent to:
               copy(channelA, resultChannel); clear(channelA).
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none
        # 
        # 
        # move(A,R)
        self.connectorLower.send_o("move", channelA, resultChannel)

    # ------------------------------------------------------------------------------
    def swap(self, channelA, channelB):
        """Theta(1)xTheta(n), where n is the length of the longer channel,
           propagation |."""
        # Domino:
        # none
        # 
        # 
        # swap(A,B)
        self.connectorLower.send_o("swap", channelA, channelB)

    # ------------------------------------------------------------------------------
    def setAll(self, channelA, word):
        """Sets each word of the channel content to the given word.
           Does not affect the values below the channel content terminator.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none      -
        #           -
        #           w
        # setAll(A) v 
        self.connectorLower.send_o("setAll", channelA)
        self.connectorLower.send_w(word)
        
    # ------------------------------------------------------------------------------
    def member(self, channelA, word):
        """Returns True or False.
           O(n)xO(n), propagation |/."""
        # Domino:
        # none      --
        #           --
        #           wb
        # member(A) v^ 
        self.connectorLower.send_o("member", channelA)
        self.connectorLower.send_w(word)
        found = self.connectorLower.receive_b()
        return found

    # --- LIST OPERATIONS, top operations --------------------------------------------------
       
    def addFirst(self, channelA, word): # push
        """Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none    - 
        #         -
        #         w
        # push(A) v 
        self.connectorLower.send_o("push", channelA)
        self.connectorLower.send_w(word)

    push = addFirst

    def addFirstPoor(self, channelA, word):
        """For instructional purposes only.
           Poor complexity; compare with addFirst/push.
           Theta(n)xTheta(n), propagation |/."""
        # Domino:
        # none          - 
        #               -
        #               w
        # pushPoor(A) v 
        self.connectorLower.send_o("pushPoor", channelA)
        self.connectorLower.send_w(word)

    # ------------------------------------------------------------------------------
    def removeGetFirst(self, channelA): # pull
        """Removes and returns the first/top word, or raises EmptyError.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none    - 
        #         -
        #         W
        # pull(A) ^ 
        self.connectorLower.send_o("pull", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
            "pull: Cannot remove first from empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word
        
    removeFirst = removeGetFirst
    pop = removeGetFirst
    dequeue = removeGetFirst
    pull = removeGetFirst

    # ------------------------------------------------------------------------------
    def replaceGetFirst(self, channelA, word):
        """Returns the first/top word and replaces it, or raises EmptyError.
           Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # none               -- 
        #                    --
        #                    wW
        # replaceGetFirst(A) v^ 
        self.connectorLower.send_o("replaceGetFirst", channelA)
        self.connectorLower.send_w(word)
        oldData, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
            "replaceGetFirst: Cannot replace first in empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return oldData

    replaceFirst = replaceGetFirst

    # --- LIST OPERATIONS, bottom operations ---------------------------------------------------

    def last(self, channelA):
        """Returns last/bottom word in the channel or raises EmptyError.
           Theta(n)xTheta(n), propagation |/."""
        # Domino:
        # none    - 
        #         -
        #         W 
        # last(A) ^ 
        self.connectorLower.send_o("last", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
                "last: Cannot peek at last in empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word

    end = last
    bottom = last

    # ------------------------------------------------------------------------------
    def addLast(self, channelA, word):
        """Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none       - 
        #            -
        #            w 
        # addLast(A) v 
        self.connectorLower.send_o("addLast", channelA)
        self.connectorLower.send_w(word)

    enqueue = addLast

    # ------------------------------------------------------------------------------
    def removeLast(self, channelA):
        """Removes last/bottom word in the channel without returning it,
           or raises EmptyError.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none          -
        #               -
        #               b
        # removeLast(A) ^ 
        self.connectorLower.send_o("removeLast", channelA)
        empty = self.connectorLower.receive_b()
        if empty:
            raise EmptyError(
                "Cannot remove last from an empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            pass

    # ------------------------------------------------------------------------------
    def removeGetLast(self, channelA):
        """Removes and returns last/bottom word in the channel
           or raises EmptyError.
           Theta(n)xTheta(n), propagation |/."""
        # Domino:
        # none             - 
        #                  -
        #                  W
        # removeGetLast(A) ^ 
        self.connectorLower.send_o("removeGetLast", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
            "removeGetLast: Cannot remove last from empty channel %s, self.chain %s.s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word
            
    # ------------------------------------------------------------------------------
    def replaceLast(self, channelA, word):
        """Replaces last/bottom word in the channel without returning it,
           or raises EmptyError.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none           -- 
        #                --
        #                wb
        # replaceLast(A) v^ 
        self.connectorLower.send_o("replaceLast", channelA)
        self.connectorLower.send_w(word)
        empty = self.connectorLower.receive_b()
        if empty:
            raise EmptyError(
                "replaceLast: Cannot replace last in empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            pass
        
    # ------------------------------------------------------------------------------
    def replaceGetLast(self, channelA, word):
        """Returns last/bottom word in the channel and replaces it,
           or raises EmptyError.
           Theta(n)xTheta(n), propagation |/."""
        # Domino:
        # none              --
        #                   --
        #                   wW
        # replaceGetLast(A) v^ 
        self.connectorLower.send_o("replaceGetLast", channelA)
        self.connectorLower.send_w(word)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
                "replaceGetLast: Cannot replace last in empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word

    # ------------------------------------------------------------------------------
    def removeAll(self, channelA, word):
        """Exericise.
           Removes all occurences of the given word.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none         -
        #              -
        #              w
        # removeAll(A) v 
        raise NotImplemented("The implementation is left as an exercise.")

    def replaceAll(self, channelA, word1, word2):
        """Exericise.
           Replaces all occurences of word1 by word2.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none         -
        #              -
        #              w
        # replaceAll(A) v 
        raise NotImplemented("The implementation is left as an exercise.")    

    # --- LIST OPERATIONS, rotations ---------------------------------------------------------

    def rotateDown(self, channelA):
        """Return the top word in the channel and rotate it down to the bottom.
           Equivalent to:
           x = pull(channelA); addLast(channelA, x)
           returns x or raises EmptyError.
           Theta(1)xTheta(n), propagation |."""
        # Domino:
        # none          -
        #               -
        #               W 
        # rotateDown(A) ^ 
        self.connectorLower.send_o("rotateDown", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
                "rotateDown: Cannot rotate down empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word

    rotate = rotateDown
        
    # ------------------------------------------------------------------------------
    def rotateUp(self, channelA):
        """Return the bottom word in the channel and rotate it up to the top.
           Equivalent to:
           x=removeGetLast(channelA); addFirst(channelA, x)
           returns x or raises EmptyError.
           Theta(n)xTheta(n), propagation |/."""
        # Domino:
        # none        -
        #             -
        #             W 
        # rotateUp(A) ^ 
        self.connectorLower.send_o("rotateUp", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError("rotateUp: Cannot rotate up empty channel %s, self.chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word
            
    # --- LIST OPERATIONS, reverse -----------------------------------------------------------

    def reverseSimplest(self, channelA, resultChannel):
        """For instructional purposes.
           Reverses the contents of channelA.
           Theta(n)xTheta(n).""" # Propagation: \-|
        # Domino:
        # none              -         -           -
        #                   -         -           -
        #                   W         w           W                        
        # clear(R) (pull(A) ^ push(R) v)* pull(A) ^
        self.connectorLower.send_o("clear", resultChannel)
        while True:
            self.connectorLower.send_o("pull", channelA)
            word, empty = self.connectorLower.receive_W()
            if empty:
                break
            else:
                self.connectorLower.send_o("push", resultChannel)
                self.connectorLower.send_w(word)

    def reverseSimple(self, channelA, resultChannel): 
        """For instructional purposes.
           Reverses the contents of channelA.
           Theta(n)xTheta(n).""" # Propagation: \-|
        # Domino:
        # none             
        #                    
        #                    
        # reverseSimple(A,R) 
        self.connectorLower.send_o("reverseSimple", channelA, resultChannel)

    def reverse(self, channelA, resultChannel): 
        """Reverses the contents of channelA.
           Theta(n)xTheta(n).""" # Propagation: \-|
        # Domino:
        # none 
        # 
        # 
        # reverse(A,R)
        self.connectorLower.send_o("reverse", channelA, resultChannel)

    # === ORDER OPERATIONS =========================================================

    def minimum(self, channelA):
        """Returns the minimum element from the channel.
           Theta(n)xTheta(n), propagation: |/."""
        # Domino:
        # none   -
        #        -
        #        W
        # min(A) ^ 
        self.connectorLower.send_o("min", channelA)
        word, empty = self.connectorLower.receive_W()
        if empty:
            raise EmptyError(
                "min: there is no min value in an empty channel %s of chain %s."
                             % (channelA, self.chain.chainName))
        elif not empty:
            return word

    def removeGetLastMinimum(self, channelA):
        """Exercise.
           Returns the minimum element from the channel
           and removes its last occurence.
           Theta(n)xTheta(n).""" # Propagation |-\
        # Domino:
        # none                -
        #                     -
        #                     W
        # removeGetLastMin(A) ^ 
        raise NotImplemented("Implementation is left as an exercise.")

    def removeGetAllMinimum(self, channelA):
        """Exercise.
           Returns the minimum element from the channel
           and removes its all occurences.
           Theta(n)xTheta(n).""" # Propagation |-\
        # Domino:
        # none               -
        #                    -
        #                    W
        # removeGetAllMin(A) ^ 
        raise NotImplemented("Implementation is left as an exercise.")

    #-------------------------------------------------------------------------------
    def memberNonDecreasing(self, channelA, word):
        """Precondition: channel elements are in non-decreasing order.
           Post: Returns True or False.
           O(n)xO(n), propagation: |/.
        """
        # Domino:
        # none        -- 
        #             --
        #             wb
        # memberND(A) v^ 
        self.connectorLower.send_o("memberND", channelA)
        self.connectorLower.send_w(word)
        found = self.connectorLower.receive_b()
        return found

    memberSorted = memberNonDecreasing

    #-------------------------------------------------------------------------------
    def insertNonDecreasing(self, channelA, word):
        """Precondition: channel elements are in non-decreasing order.
           Inserts new element mantaining the order.
           Theta(1)xTheta(n), propagation: |."""
        # Domino:
        # none        -
        #             -
        #             w
        # insertND(A) v 
        self.connectorLower.send_o("insertND", channelA)
        self.connectorLower.send_w(word)

    insert = insertNonDecreasing

    #-------------------------------------------------------------------------------
    def insertUniqueIncreasing(self, channelA, word):
        """Precondition: channel elements are in increasing order.
           Inserts new elemet if it is not there yet; mantains the order.
           Theta(1)xO(n), propagation: |."""
        # Domino:
        # none             -
        #                  -
        #                  w
        # insertUniqueI(A) v 
        self.connectorLower.send_o("insertUniqueI", channelA)
        self.connectorLower.send_w(word)

    insertUnique = insertUniqueIncreasing

    #--- ORDER OPERATIONS, sorts ----------------------------------------------------

    def insertAllNonDecreasingSimple(self, channelA, channelB): 
        """Insert all items from channelA into channelB.
           Precondition: channelB is in non-decreaisng order, possibly empty;
           Post: channelB contains all items from both channels, sorted.
                 channelA becomes empty. 
           Theta(m)xTheta(m+n). 
           where m is the length of channelA, and n is the length of channelB."""
           # Propagation: |-\
        # Domino:
        # none     -             -           -
        #          -             -           -
        #          W             w           W
        # (pull(A) ^ unsertND(B) v)* pull(A) ^
        while True:
            self.connectorLower.send_o("pull", channelA)
            word, empty = self.connectorLower.receive_W()
            if empty:
                break
            else:
                self.connectorLower.send_o("insertND", channelB)
                self.connectorLower.send_w(word)
            
    def insertAllNonDecreasing(self, channelA, channelB): 
        """Insert all items from channelA into channelB.
           Precondition: channelB is in non-decreaisng order, possibly empty;
           Post: channelB contains all items from both channels, sorted.
                 channelA becomes empty. 
           Theta(m)xTheta(m+n).
           where m is the length of channelA, and n is the length of channelB."""
           # Propagation: |-\
        # Domino:
        # none
        #
        #
        # insertAllND(A,B) 
        self.connectorLower.send_o("insertAllND", channelA, channelB)
        
    #-------------------------------------------------------------------------------
    def iSort(self, channelA): 
        """Theta(n)xTheta(n).""" # Propagation: |-\
        # Domino:
        # none
        # 
        # 
        # iSort(A)
        self.connectorLower.send_o("iSort", channelA)

    insertionSort = insertionSortND = insertionSortNonDecreasing = iSort

    #-------------------------------------------------------------------------------
    def sSort(self, channelA): 
        """...""" # Propagation:
        # Domino:
        # none
        # 
        # 
        # sSort(A)
        self.connectorLower.send_o("sSort", channelA)

    selectionSort = selectionSortND = selectionSortNonDecreasing = sSort

    #-------------------------------------------------------------------------------
    def bSort(self, channelA): 
        """Theta(n)xTheta(n), propagation: ."""
        # Domino:
        # none
        #
        # 
        # bSort(A)
        self.connectorLower.send_o("bSort", channelA)

    bubbleSort = bubbleSortND = bubbleSortNonDecreasing = bSort

    # Selection sort can be implemented, but it is less efficient than bubble sort, 
    # because swapping two elements is linear in the bigger of the two indexes.
        
    #--- ORDER OPERATIONS, merge -----------------------------------------------------------

    def mergeNonDecreasingSimple(self, channelA, channelB, resultChannel): 
        """This version is for instructional purposes;
           a two-channel version follows.
           Precondition: channelA and channelB are each in non-decreaisng order;
           Post: resultChannel is the result of merging them.
                 channelA and channelB are modified.
           Theta(m)xTheta(n), propagation: 
           where m is the length of the shorter channel
           and n is the length of the longer channel.
        """
        # Domino:
        # none
        # 
        # 
        # mergeND(A,B,R)
        self.connectorLower.send_o("mergeNDsimple",
                                    channelA, channelB, resultChannel)

    def mergeNonDecreasing(self, channelA, channelB): 
        """Precondition: channelA and channelB are each in non-decreaisng order;
           Post: channelB is the result of merging them.
                 channelA is modified.
           ??? , propagation: .
           where m is the length of channelA, and n is the length of channelB.
        """
        # Domino:
        # none
        # 
        # 
        # mergeND(A,B)
        self.connectorLower.send_o("mergeND", channelA, channelB)
        
    mergeIntoNonDecreasing = mergeNonDecreasing
    mergeInto = mergeNonDecreasing
    merge = mergeNonDecreasing

    # === INDEXING OPERATIONS =================================================

    # Indexing operations violate the spirit of chan opertions,
    # because indexes can be arbitrrily big, but CPE sorage is limited.

    # ---------------------------------------------------------------------

    # length is an indexing operation, because it relies on colculating
    # indexes of all list items.

    def length(self, channelA):
        self.connectorLower.send_o("length", channelA)
        word = self.connectorLower.receive_w()
        return word

    # ---------------------------------------------------------------------

    def getItem(self, channelA, index):
        """If index is valid, returns the word at index
           otherwise raises exceptions.
        """
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("getItem", channelA)
        self.connectorLower.send_w(index)
        item, notFound = self.connectorLower.receive_W()
        if notFound:
            raise IndexError("No such index in the list.")
        return item

    # ---------------------------------------------------------------------

    def setItem0(self, channelA, index, item):
        """If index is valid, sets the word at index to item.
           If index is past the end of the list, does nothing.
           If index is not valid for other reasons, raises exceptions.
        """
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("setItem0", channelA)
        self.connectorLower.send_w(index)
        self.connectorLower.send_w(item)
        
    def setItem(self, channelA, index, item):
        """If index is valid, sets the word at index to item.
           If index is not valid, raises exceptions.
        """
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("setItem", channelA)
        self.connectorLower.send_w(index)
        self.connectorLower.send_w(item)
        notFound = self.connectorLower.receive_b()
        if notFound:
            raise IndexError("No such index in the list.")

    # ---------------------------------------------------------------------

    def getSetItem(self, channelA, index, item):
        """If index is valid, sets the word at index to item,
           and returns the item that has been replaced.
           If index is not valid, raises exceptions.
        """
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("getSetItem", channelA)
        self.connectorLower.send_w(index)
        self.connectorLower.send_w(item)
        item, notFound = self.connectorLower.receive_W()
        if notFound:
            raise IndexError("No such index in the list.")
        return item

    replaceAtIndex = setGetItem = getSetItem

    # ------------------------------------------------------------------------

    def memberIndex(self, channelA, item):
        """Returns the first index where the item occurs,
           or raises ValueError."""
        # none        - -
        #             - -
        #             w W
        # memberIndex v ^
        self.connectorLower.send_o("memberIndex", channelA)
        self.connectorLower.send_w(item)
        index, notFound = self.connectorLower.receive_W()
        if notFound:
            raise ValueError("No such item in the list.")
        return index

    # ------------------------------------------------------------------------

    def insertAtIndex0(self, channelA, index, item):
        """If index is valid, shifts the list members starting at index,
           and inserts the item.
           If index is past the end of the list, does nothing.
           (It cannot be used to append item at the end.)
           If index is not valid in other ways, raises exceptions.
        """
        # none          - -
        #               - -
        #               w w
        # insetAtIndex0 v v
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("insertAtIndex0", channelA)
        self.connectorLower.send_w(index)
        self.connectorLower.send_w(item)

    def insertAtIndex(self, channelA, index, item):
        """If index is valid, shifts the list members starting at index,
           and inserts the item.
           If index is not valid, raises exceptions.
        """
        # none         - - -
        #              - - -
        #              w w b
        # insetAtIndex v v ^
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("insertAtIndex", channelA)
        self.connectorLower.send_w(index)
        self.connectorLower.send_w(item)
        badIndex = self.connectorLower.receive_b()
        if badIndex:
            raise IndexError("No such index in the list.")

    # -------------------------------------------------------------------------

    def deleteAtIndex(self, channelA, index):
        """If index is valid, shifts up the list members starting at index+1,
           effectively deleting item at index, return the original item at index
           If the index is past the end of the list, does nothing.
           If index is not valid in other ways, raises exceptions.
        """
        # none          -
        #               -
        #               w
        # deleteAtIndex v
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("deleteAtIndex", channelA)
        self.connectorLower.send_w(index)

    def deleteGetAtIndex(self, channelA, index):
        """If index is valid, shifts up the list members starting at index+1,
           effectively deleting item at index, return the original item at index
           If index is not valid, raises exceptions.
        """
        # none          - -
        #               - -
        #               w W
        # deleteAtIndex v ^
        if not isinstance(index, int):
            raise TypeError("index should be an integer.")
        if index < 0:
            raise IndexError("index should be non-negative")
        self.connectorLower.send_o("deleteGetAtIndex", channelA)
        self.connectorLower.send_w(index)
        item, badIndex = self.connectorLower.receive_W()
        if badIndex:
            raise IndexError("No such index in the list.")
        return item
    
    # === LOADERS AND UNLOADERS ===============================================

    def loadWordsSimple(self, channelA, iterable):
        """ """
        self.connectorLower.send_o("clear", channelA)
        for word in iterable:
            self.connectorLower.send_o("addLast", channelA)
            self.connectorLower.send_w(word)
            
    def loadWords(self, channelA, iterable):
        """Puts the contents of the iterable into the channel
           with the first item at the top.
           Each item from iterable is handled in Theta(1)xO(n),
           all items: Theta(n)xTheta(n)."""
           # One item propagation \
           # All items propagation \|
        # Domino:
        # none         -
        #              -
        #              W 
        # loadWords(A) v+ 
        self.connectorLower.send_o("loadWords", channelA)
        for word in iterable:
            self.connectorLower.send_W(word, False) # Empty=False
        self.connectorLower.send_W(Any, True)       # Empty=True

    #-----------------------------------------------------------------        

    def loadWordsReverseSimple(self, channelA, iterable):
        """Puts the contents of the iterable into the chain.
           Subsequently, you can use iterator(chain) to get
           the same items in the reverse order."""
        self.connectorLower.send_o("clear", channelA)
        for word in iterable:
            self.connectorLower.send_o("push", channelA)
            self.connectorLower.send_w(word)
            
    def loadWordsReverse(self, channelA, iterable):
        """Puts the contents of the iterable into the channel
           with the first item at the bottom.
           Equivalent to clear, followed by repeated addFirst/push.
           Each item from iterable is handled in Theta(1)xO(n).
           all items: Theta(n)xTheta(n).""" # Propagation \|
        # Domino:
        # none                - 
        #                     -
        #                     W
        # loadWordsReverse(A) v+ 
        self.connectorLower.send_o("loadWordsReverse", channelA)
        for word in iterable:
            self.connectorLower.send_W(word, False) # Empty=False
        self.connectorLower.send_W(Any, True)       # Empty=True

    reverseOnLine = loadWordsReverse

    #---LOADERS, ordered-------------------------------------------------------------------

    def loadWordsNonDecreasingSimple(self, channelA, iterable):
        """Puts the contents of the iterable into the chain.
           Subsequently, you can use iterator(chain) to get
           the same items in the sorted order."""
        self.connectorLower.send_o("clear", channelA)
        for word in iterable:
            self.connectorLower.send_o("insertND", channelA)
            self.connectorLower.send_w(word)

    def loadWordsNonDecreasing(self, channelA, iterable):
        """Puts the contents of the iterable into the chaannel in a sorted order.
           with the smallest item at the top.
           Equivelent to clear(A) and repeated insertNonDecreasing(A).
           Each item from iterable is handled in Theta(1)xO(n), propagation: ."""
        # Domino:
        # none           -
        #                -
        #                W
        # loadWordsND(A) v+
        self.connectorLower.send_o("loadWordsND", channelA)
        for word in iterable:
            self.connectorLower.send_W(word, False) # Empty=False
        self.connectorLower.send_W(Any, True)       # Empty=True

    loadWordsSorted = loadWordsNonDecreasing
    sortOnLine = loadWordsNonDecreasing

    #-------------------------------------------------------------------------------

    def loadWordsUniqueIncreasingSimple(self, channelA, iterable):
        """ """
        self.connectorLower.send_o("clear", channelA)
        for word in iterable:
            self.connectorLower.send_o("insertUniqueI", channelA)
            self.connectorLower.send_w(word)

    def loadWordsUniqueIncreasing(self, channelA, iterable):
        """Puts the contents of the iterable into the chaannel in a sorted order.
           with the smallest item at the top, eliminates duplicates.
           Equivelent to clear(A) and repeated insertUniqueIncreasing(A).
           Each item from iterable is handled in Theta(1)xO(n).
           All items: Theta(n)xO(n).""" # Propagation: \-\
        # Domino:
        # none                -
        #                     -
        #                     W
        # loadWordsUniqueI(A) v+
        self.connectorLower.send_o("loadWordsUniqueI", channelA)
        for word in iterable:
            self.connectorLower.send_W(word, False) # Empty=False
        self.connectorLower.send_W(Any, True)       # Empty=True

    #--- UNLOADERS ------------------------------------------------------------

    def unloadWords(self, channelA):
        """Returns an iterator that
           iterates over all the items on the stack, top to bottom,
           O(1) per item, propagation: . Leaves the stack empty.
           Every iteration is equivalent to removeGetFirst(self, channel);
           if the iterator is not exhausted, it will leave some items on the stack.
           Belongs to the self.chain controller interface.
        """
        # Domino:
        # none     -
        #          -
        #          W 
        # (pull(A) ^)+ 
        while True:
            self.connectorLower.send_o("pull", channelA)
            word, empty = self.connectorLower.receive_W()
            if empty:
                break
            else:
                yield word

    iterator = unloadWords

    def unloadAllWords(self, channelA):
        """Returns an uniterruptible iterator that
           iterates over all the items in the channel, top to bottom;
           destructs the content of the channel leaving it empty.
           This iterator is uniterruptible -- no other operation can be
           started on this self.chain until the iterator is exhausted.
           Every iteration is equivalent to pull(self, channelA)
           and kth iteration has complexity Theta(1)xO(n),
           all items Theta(n)xTheta(n)."""
           # One item  propagation \
           # All items propagation |/
        # Domino:
        # none              -
        #                   -
        #                   W
        # unloadAllWords(A) ^+ 
        self.connectorLower.send_o("unloadAllWords", channelA)
        while True:
            word, empty = self.connectorLower.receive_W()
            if empty:
                break
            else:
                yield word

   #--- unloadWordsReverse ------------------------------

    def unloadWordsReverseSimple(self, channelA, aux1):
        """ """
        self.connectorLower.send_o("moveLast", channelA, aux1)
        empty = self.connectorLower.receive_b()
        if not empty:
            yieldedValue = False
            while True:
                self.connectorLower.send_o("pullEnd", channelA, aux1)
                word, empty = self.connectorLower.receive_W()
                if not empty:
                    yield word
                    yieldedValue = True
                if yieldedValue and empty:
                    break
                    
    def moveLast(self, channelA, aux1):
        """Demonstration of a component of unloadWordsReverse.
           For instructional purposes only; not a part of controller interface."""
        # Domino:
        # none          -
        #               -
        #               b
        # moveLast(A,X) ^
        self.connectorLower.send_o("moveLast", channelA, aux1)
        empty = self.connectorLower.receive_b()
        return empty

    def pullEnd(self, channelA, aux1):
        """Demonstration of a component of unloadWordsReverse.
           For instructional purposes only; not a part of controller interface."""
        # Domino:
        # none         -
        #              -
        #              W
        # pullEnd(A,X) ^
        self.connectorLower.send_o("pullEnd", channelA, aux1)
        word, empty = self.connectorLower.receive_W()
        return word, empty

    def unloadWordsReverseBegin(self, channelA, aux1):
        """Demonstration of a component of unloadWordsReverse.
           For instructional purposes only; not a part of controller interface."""
        # Domino:
        # none                         -
        #                              -
        #                              W
        # unloadWordsReverseBegin(A,X) ^
        self.connectorLower.send_o("unloadWordsReverseBegin", channelA, aux1)
        word, empty = self.connectorLower.receive_W()
        return word, empty

    def unloadWordsReverse(self, channelA, aux1):
        """One can show that on an non-empty channelA
           aux1 becomes empty after a pullAux call;
           then pullAuxCopyLast returns empty=True;
           then one more call to pullAux is needed to restore ChannelA.
           So, the enitre procedure ends after a call to pullAux."""
        # Domino:
        # none                         -                              -
        #                              -                              -
        #                              W                              W
        # unloadWordsReverseBegin(A,X) ^ (unloadWordsReverseNext(A,X) ^)*
        self.connectorLower.send_o("unloadWordsReverseBegin", channelA, aux1)
        word, empty = self.connectorLower.receive_W()
        while not empty:
            yield word
            self.connectorLower.send_o("unloadWordsReverseNext", channelA, aux1)
            word, empty = self.connectorLower.receive_W()

    reverseIterator = unloadWordsReverse

    def unloadAllWordsReverse(self, channelA, aux1): 
        """Returns an uniterruptible iterator that
           iterates over channelA, bottom to top,
           Does not modify channelA.
           This iterator is uniterruptible -- no other operation can be
           started on this self.chain until the iterator is exhausted.
           Belongs to the self.chain controller interface.
           Theta(n)xTheta(n) to give the bottom item, propagation ?,
           then Theta(1)xO(n) per item. propagation |.
           All items given in Theta(n)xTheta(n), propagation: |/."""
        # Domino:
        # none                       -
        #                            -
        #                            W 
        # unloadAllWordsReverse(A,X) ^+ 
        self.connectorLower.send_o("unloadAllWordsReverse", channelA, aux1)
        while True:
            word, empty = self.connectorLower.receive_W()
            if empty:
                break
            else:
                yield word

    #### ARITHMETIC ############################################################

    # words2integer
    # integer2words
    # channel1 == channel2
    # channel1 < channel2 (each channel treated as an integer)
    # channel1 < channel2 (word-wise)
    # <=
    # channel/integer + 1 =
    # channel - 1 = ... (0 - 1 -> error, or 0 - 1 = 0 )
    # channel + 1 word-wise mod max

    # We consider only non-negative integers.
    # They are represented using standard binary notation.
    # The bits of an integer are divided into words.
    # The little end is the word that stires least significant bits.
    # In a chain, the little end is stored at the top.

    def loadInteger(self, channelA, wordIterator):
        """wordIterator needs to yield words starrting from the
           little end of a non-negative integer."""
        first = True
        for word in wordIterator:
            if first:
                self.connectorLower.send_o("loadFirstWord", channelA)
                self.connectorLower.send_w(word)
                first = False
            else:
                self.connectorLower.send_o("loadNextWord", channelA)
                self.connectorLower.send_w(word)
        if first:
            raise ValueError(
                "loadIterator(%s,wordIterator): wordIterator cannot be empty." %
                channelA)

    def equal(self, channelA, channelB):
        """Returns True if the two integers are equal; False otherwise."""
        # Domino:
        # none       -
        #            -
        #            b
        # equal(A,B) ^
        self.connectorLower.send_o("equal", channelA, channelB)
        equal = self.connectorLower.receive_b()
        return equal

    def lessOrEqual(self, channelA, channelB):
        """Returns True if the first integer is less than or equal to
           the second; False otherwise."""
        # Domino:
        # none    -
        #         -
        #         B
        # le(A,B) ^
        self.connectorLower.send_o("le", channelA, channelB)
        le, sure = self.connectorLower.receive_B()
        return le

    def less(self, channelA, channelB):
        """Returns True if the first integer is less than the second;
           False otherwise."""
        # Domino:
        # none      -
        #           -
        #           B
        # less(A,B) ^
        self.connectorLower.send_o("less", channelA, channelB)
        le, sure = self.connectorLower.receive_B()
        return le

    def copyInt(self, channelA, resultChannel):
        """ """
        # Domino:
        # none            
        #                 
        #                 
        # copyInt(A,R) 
        self.connectorLower.send_o("copyInt", channelA, resultChannel)

    def conjunction(self, channelA, channelB, resultChannel):
        """channelA becomes the bitwise 'and' of the two channels."""
        # Domino:
        # none            
        #                 
        #                 
        # conj(A,B,R) 
        self.connectorLower.send_o("conj", channelA, channelB, resultChannel)

    def disjunction(self, channelA, channelB, resultChannel):
        """channelA becomes the bitwise 'or' of the two channels."""
        # Domino:
        # none            
        #                 
        #                 
        # or(A,B,R) 
        self.connectorLower.send_o("or", channelA, channelB, resultChannel)

    def exclusiveDisjunction(self, channelA, channelB, resultChannel):
        """channelA becomes the bitwise 'xor' of the two channels."""
        # Domino:
        # none            
        #                 
        #                 
        # xor(A,B,R) 
        self.connectorLower.send_o("xor", channelA, channelB, resultChannel)    

    def double(self, channelA):
        """Multiplies the channelA integer by 2."""
        # Domino:
        # none      
        #           
        #             
        # double(A) 
        self.connectorLower.send_o("double", channelA)

    leftShift0 = double
    
    def complment(self, channelA):
        """channelA becomes the bitwise complement of itself."""
        # Domino:
        # none            
        #                 
        #                 
        # complement(A) 
        self.connectorLower.send_o("complement", channelA)
