#!/usr/bin/env python3

"""ASYNCHRONOUS CHAIN: CLASS CPE"""

# ==============================================================================

from myThreading import *
from connector import Connector

# ==============================================================================

# How many:
CHANNELS = 3   # valid indexes: 0, 1, 2 (non-negative integers)
TEMP_SPACE = 2 # valid indexes: 0, 1 (non-negative integers)

WORD_SIZE = 8 # in bits, excludes the continuation bit.

# ==============================================================================

global_chain2list = [] # a global object used by chain2list and register2list.

# ==============================================================================

def base4string(number):
    """Precondition: number is a non-negative integer.
       Returns a string representing number in base 4."""
    (q, r) = divmod(number, 4)
    return base4string(q) + str(r) if q > 0 else str(r)

##def letter2base(baseLetter):
##    if baseLetter == "b":
##        return 2
##    elif baseLetter == "q":
##        return 4
##    elif baseLetter == "o":
##        return 8
##    elif baseLetter.lower() == "x":
##        return 16
##    else:
##        return 10

def number2string(number, base):
    if base == 2:
        return format(number, 'b').zfill(WORD_SIZE)
    elif base == 4:
        return base4string(number).zfill(WORD_SIZE // 2)
    elif base == 8:
        return format(number, 'o').zfill(WORD_SIZE // 3)
    elif base == 16:
        return format(number, 'X').zfill(WORD_SIZE // 4)
    else: # base == 10:
        return str(number)
    
# ==============================================================================

class EmptyError(LookupError):
    pass 

# ==============================================================================

class CPE(threading.Thread):
    """Chain Processing Element.
       A CPE object models a single asynchronous sequential circuit,
       or equivalently a one-element free chain of such circuits.
       Apropriate methods automatically extend the chain.
       Each CPE object runs as a separate thread and can communicate with
       "neighbor" CPE objects via a 4-phase protocol
       but cannot access their data in any other way.

       The first CPE object is allocated by the main thread and it is our
       entry point to a free chain. If needed, that first CPE object
       will allocate a new CPE object, and the new object can allocate the next,
       etc. The chain will grow dynamically; it never shrinks.

       It is useful to think about a CPE object in two ways:
       1. as a single CPE object,
       2. as a free chain that starts at that CPE object.

       A CPE object's CONTENTS is self.word[channelA] provided that
       self.bit[channelA]==False.
       If self.bit[channelA]==True, we say that the CPE object is EMPTY.
       A free chain CONTENTS extends from the top 
       down to the first EMPTY CPE object;
       any CPE objects below do not contribute to the chain contents 
       irrespectiverly of whether they are empty or not.

       Every CPE object has additional auxiliary fields used in operations that
       do not modify the CPE content but require transmission of data through
       the CPE; they are also used by push."""

    chainId = 0

    def __init__(self, chainName=None): # deprecated: chainName
        """Theta(1). Create an empty CPE with an upper connector.
           A string can be provided for chainName (best up to 5 characters long)
           otherwise a distinct chainName will be an automatically generated."""
        super().__init__()
        # chainName and chainId, for debugging only, not a part of the model.
        self.peId = 1
        if chainName is None:
            CPE.chainId += 1
            self.chainName = "CH" + str(CPE.chainId)
        else:
            self.chainName = chainName
        self.name = self.chainName + "." + str(self.peId) # CPE obj./thread name
        # The following fields model a CPE circuit.
        self.connectorUpper = Connector()
        self.connectorLower = None
        self.operation = Any # a string naming the operation/method.
        self.channels = Any # a tuple of non-negative integers, possibly empty.
        self.word = [Any]*(CHANNELS) # words
        self.bit = [Any]*(CHANNELS) # bits
        # A standard use: self.bit[i]=False means self.word[i] is not empty.
        self.temp_w = [Any]*TEMP_SPACE # not preserved between activations
        self.temp_b = [Any]*TEMP_SPACE

    def extend(self):
        """Connect a new CPE object below self, conditionally,
           if there isn't any.
           In the infinite-memory-model of computation, one assumes
           either that the chain of CPE's is inifinie
           or that it can be instantly extended when needed.
           In our simulation we extend the chain by one CPE at a time,
           when needed, in Theta(1) time."""
        if self.connectorLower is None:
            lowerPE = CPE(self.chainName)
            lowerPE.peId = self.peId+1
            lowerPE.name = self.chainName + "." + str(lowerPE.peId)
            self.connectorLower = lowerPE.connectorUpper
            lowerPE.start()

    def stop(self):
        """Stop all threads in the chain.
           Not a part of the model."""
        if self.connectorLower is not None:
            self.connectorLower.send_o("stop")

    def __repr__(self):
        return self._repr(10)

    def _repr(self, base): 
        """Detailed view of the state of the CPE.
           For debugging only, not a part of the model.
           Do not call this method, and do not call print, in the main thread,
           to avoid racing. In the main thread it is safe to call printRepr."""
        result = "{:9}".format(self.name)
        for channel in range(CHANNELS): 
            if isinstance(self.word[channel], int):
                dat = number2string(self.word[channel], base)
            else:
                dat = str(self.word[channel]) # dat could be Any.
            result += " {:>8} {:5}".format(
                dat, str(self.bit[channel]))
        for temp in range(TEMP_SPACE):
            if isinstance(self.temp_w[temp], int):
                dat = number2string(self.temp_w[temp], base)
            else:
                dat = str(self.temp_w[temp]) # dat could be Any.
            result += " {:>8} {:5}".format(
                dat, str(self.temp_b[temp]))
        return result

    def __str__(self):
        """Simplified view of the state of the CPE, used in self.printStr.
           For debugging only, not a part of the model.
           Do not call this method, and do not call print, in the main thread,
           to avoid racing. In the main thread it is safe to call self.printStr.
           """
        def simplify(dat, empt):
            if empt is False:
                return str(dat)
            elif empt is True:
                return "-"
            else:
                return "?"
        result = "{:9}".format(self.name)
        for channel in range(CHANNELS):
            result += " {:>8}".format(
                simplify(self.word[channel], self.bit[channel]))
        for temp in range(TEMP_SPACE):
            result += " {:>8}".format(
                simplify(self.temp_w[temp], self.temp_b[temp]))
        return result

    def printRepr2(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unoad iterator completed all the iterations."""
        print(self._repr(2))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printRepr2")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

    def printRepr4(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unoad iterator completed all the iterations."""
        print(self._repr(4))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printRepr4")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

    def printRepr8(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unoad iterator completed all the iterations."""
        print(self._repr(8))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printRepr8")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

    def printRepr16(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unoad iterator completed all the iterations."""
        print(self._repr(16))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printRepr16")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

    def printRepr10(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unoad iterator completed all the iterations."""
        print(self._repr(10))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printRepr10")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

            
    def printStr(self):
        """For debugging only, not a part of the model.
           Cannot be used until the previous chain operation is completed,
           for instance until an unload iterator completed all the iterations."""
        print(str(self))
        if self.connectorLower is not None:
            self.connectorLower.send_o("printStr")
            self.connectorLower.receive_b() # synchronization
            self.connectorUpper.send_b(Any)
        elif self.connectorLower is None:
            self.connectorUpper.send_b(Any)

    def chain2list(self, channel):
        """For debugging only, not a part of the model."""
        global global_chain2list
        if not self.bit[channel]: # if not empty:
            global_chain2list.append(self.word[channel])
            if self.connectorLower is not None:
                self.connectorLower.send_o("chain2list", channel)
                badEnding = self.connectorLower.receive_b() # synchronization
                self.connectorUpper.send_b(badEnding)
            elif self.connectorLower is None:
                self.connectorUpper.send_b(True) # badEnding=True
        elif self.bit[channel]: # if empty
            self.connectorUpper.send_b(False) # badEnding=False
            
    def register2list(self, channel):
        """For debugging only, not a part of the model."""
        global global_chain2list
        global_chain2list.append(self.word[channel])
        if self.bit[channel]: # if continued:
            if self.connectorLower is not None:
                self.connectorLower.send_o("register2list", channel)
                badEnding = self.connectorLower.receive_b() # synchronization
                self.connectorUpper.send_b(badEnding)
            elif self.connectorLower is None:
                self.connectorUpper.send_b(True) # badEnding=True
        elif not self.bit[channel]: # if not continued (last word):
            self.connectorUpper.send_b(False) # badEnding=False

    # ==========================================================================
    
    def run(self):
        """When a CPE thread is started, this method is automatically invoked. It
           models the operation of a CPE - an asynchronous sequential circuit."""
        # The local variable t and calls to threadTime, threadLog
        # are not parts of the model; they are used to time the operations.
        # A call to self.stop is not a part of the model;
        # it is used to terminate all threads in the chain.
        while True:
            t = threadTime() # timing not a part of the model
            self.operation, self.channels = self.connectorUpper.receive_o()
            for ch in self.channels:
                if ch >= 0:
                    if ch >= CHANNELS:
                        raise ValueError(
                        "send_o%s: data channel index %s should be < %s." %
                        ((self.operation,)+self.channels, ch, CHANNELS))
                elif ch < 0:
                    raise ValueError(
                        "send_o%s: channel index %s should be >= 0." %
                        ((self.operation,)+self.channels, ch))
            for ch in self.channels:
                if self.channels.count(ch) > 1:
                    raise ValueError("send_o%s: channels should not repeat." %
                                     str((self.operation,)+self.channels))
            if self.operation != "printRepr" and self.operation != "printStr":
                self.temp_w = [Any]*TEMP_SPACE
                self.temp_b = [Any]*TEMP_SPACE
            if self.operation == "stop":
                self.stop()
                break
            else:
                # call self.operation with channels as arguments:
                eval("self.%s(*%s)" % (self.operation, self.channels)) 
            self.operation = Any
            self.channels = Any
            #threadLog("Have", self.word[channel], t) # timing

    # === LIST OPERATIONS, top CPE operations ========================================

    def isEmpty(self, channelA):
        """Sends up True if the channel below is empty.
           (self.bit[channelA]==True iff it is empty.)
           Theta(1)xTheta(1), non-propagating."""
        # isEmpty(A) ^ 
        #            b
        #            -
        # none       -
        pass

    # --------------------------------------------------------------------------
    def clear(self, channelA):
        """Makes the channel below empty.
           (Sets self.bit[channelA]=True.)
           Theta(1)xTheta(1), non-propagating."""
        # clear(A)
        #
        #
        # none
        self.bit[channelA] = True
        
    def clear2(self, channelA, channelB):
        """Implements clear(A) x clear(B).
           Theta(1)xTheta(1), non-propagating."""
        # clear2(A,B)
        # 
        # 
        # none
        pass

    #---------------------------------------------------------------------------
    def first(self, channelA):
        """Sends up the Word from the current CPE'. 
           Theta(1)xTheta(1), non-propagating."""
        # first(A) ^ 
        #          W
        #          -
        # none     - 
        pass
    
    # === LIST OPERATIONS, whole chain operations ========================================

    def copy(self, channelA, resultChannel):
        """Theta(1)xTheta(n), propagation |."""
        pass

    #---------------------------------------------------------------------------
    def move(self, channelA, resultChannel):
        """Implements copy(A,R) x clear(A).
           Theta(1)xTheta(n), propagation |."""
        pass
            
    #---------------------------------------------------------------------------
    def swap(self, channelA, channelB):
        """Theta(1)xTheta(n), where n is the length of the longer channel,
           propagation |."""
        pass
        
    # --------------------------------------------------------------------------
    def setAll(self, channelA):
        """Sets each word of the channel content to the given word.
           Does not affect the values below the channel content terminator.
           Theta(1)xTheta(n), propagation |."""
        pass

    # --------------------------------------------------------------------------
    def member(self, channelA): 
        """O(n)xO(n), propagation |/.""" 
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w()
            if self.word[channelA] == self.temp_w[0]: # found here
                # Domino: (item found in the current P)
                # member(A) v^ 
                #           wb
                #           --
                # none      -- 
                self.connectorUpper.send_b(True)
            else: # keep looking below
                # Domino: (keep looking down the list)
                # member(A) v--^ 
                #           w--b
                #           -wb-
                # member(A) -v^- 
                self.connectorLower.send_o("member", channelA)
                self.connectorLower.send_w(self.temp_w[0])
                self.temp_w[0] = self.connectorLower.receive_b()
                self.connectorUpper.send_b(self.temp_w[0])
        elif self.bit[channelA]: # if current CPE terminates the list
            # Domino: (end reached, item not found)
            # member(A) v^ 
            #           wb
            #           --
            # none      -- 
            _ = self.connectorUpper.receive_w()
            self.connectorUpper.send_b(False) # not found anywhere
    
    # --- LIST OPERATIONS, top operations ----------------------------------------------

    def push(self, channelA): # addFirst
        """Shifts all words in the contents of the channel one level down,
           and stores the received word in the current CPE.
           Theta(1)xTheta(n), propagation |."""
        pass
            
    def pushPoor(self, channelA): #addFirstLinear
        """For instructional purposes only.
           Poor top complexity; compare with push.
           Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # pushPoor(A) -v 
            #             -w
            #              w-
            # pushPoor(A)  v- 
            self.connectorLower.send_o("pushPoor", channelA)
            self.connectorLower.send_w(self.word[channelA])
            self.word[channelA] = self.connectorUpper.receive_w()
        elif self.bit[channelA]:
            # Domino:
            # pushPoor(A) v 
            #             w
            #             -
            #    clear(A) - 
            self.word[channelA] = self.connectorUpper.receive_w()
            self.bit[channelA] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelA)

    #---------------------------------------------------------------------------
    def pull(self, channelA): # removeGetFirst
        """Sends up the Word from the current CPE's channel 
           and pulls all Words in the channel contents one level up.
           Theta(1)xTheta(n), propagation |."""
        pass
    
    #---------------------------------------------------------------------------
    def replaceGetFirst(self, channelA):
        """Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # replaceGetFirst(A) v^
        #                    wW
        #                    --
        # none               --
        pass
    
    # --- LIST OPERATIONS, bottom operations -----------------------------------------------

    def last(self, channelA):
        """Theta(n)xTheta(n), propagation |/."""
        pass
    
    #---------------------------------------------------------------------------
    def addLast(self, channelA):
        """Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # Domino:
            # addLast(A) v- 
            #            w-
            #            -w
            # addLast(A) -v 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("addLast", channelA)
            self.connectorLower.send_w(self.temp_w[0])
        elif self.bit[channelA]:
            # Domino:
            # addLast(A) v 
            #            w
            #            -
            #   clear(A) -
            self.word[channelA] = self.connectorUpper.receive_w()
            self.bit[channelA] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelA)
    
    #---------------------------------------------------------------------------
    def removeLast(self, channelA):
        """Implementation: Pulls up the bit portion of the channel.
           Theta(1)xTheta(n), propagation |."""
        pass

    #---------------------------------------------------------------------------
    def removeGetLast(self, channelA):
        """Remove and send up the last item in the chain.
           Theta(n)xTheta(n), propagation |/."""
        pass
    
    #---------------------------------------------------------------------------
    def replaceLast(self, channelA):
        """Theta(1)xTheta(n), propagation |."""
        pass

    #---------------------------------------------------------------------------
    def replaceGetLast(self, channelA):
        """Theta(n)xTheta(n), propagation |/."""
        pass

    # --- LIST OPERATIONS, rotations -----------------------------------------------------

    def rotateDown(self, channelA):
        """Executed only by the top CPE in the chain.
           Implements a=pull(A) x addLast(A,a).
           Theta(1)xTheta(n), propagation |."""
        pass
    
    def pullXaddLast(self, channelA):
        """A helper for rotateDown, executed by non-top PEs in the chain.
           Implements pull(A) x addLast(A,a).
           Theta(1)xTheta(n), propagation |."""
        pass

    #---------------------------------------------------------------------------
    def rotateUp(self, channelA):
        """Executed only by the top CPE in the chain.
           Theta(n)xTheta(n), propagation |/."""
        pass

    def pushXremoveGetLast(self, channelA):
        """A helper for rotateUp, executed by non-top PEs in the chain.
           Theta(n)xTheta(n), propagation |/."""
        pass
            
    #--- LIST OPERATIONS, reverse -----------------------------------------------------

    def reverseSimple(self, channelA, resultChannel):
        """For instructional purposes.
           Theta(n)xTheta(n)""" # propagation: \-|.
        pass

    def reverse(self, channelA, resultChannel):
        """Theta(n)xTheta(n)""" # propagation: \-|.
        pass

    def pullXclear(self, channelA, channelB):
        """pull(A) x clear(B).
           Theta(1)xTheta(n), propagation: |."""
        pass

    def pushXpull(self, channelA, channelB):
        """push(channelB) x pull(channelA)
           Theta(1)xTheta(n), propagation: |."""
        pass

    # === ORDER OPERATIONS =====================================================

    def min(self, channelA):
        """Sends up the minimum element from the channel.
           Theta(n)xTheta(n), propagation: |/."""
        pass
    
    #---------------------------------------------------------------------------  
    def memberND(self, channelA):
        """Precondition: channel elements are in non-decreasing order.
           O(n)xO(n), propagation: |/."""
        pass

    #---------------------------------------------------------------------------  
    def insertND(self, channelA): 
        """Precondition: channel elements are in non-decreasing order.
           Theta(1)xTheta(n), propagation: |."""
        pass

    #---------------------------------------------------------------------------  
    def insertUniqueI(self, channelA): 
        """Precondition: channel elements are in increasing order.
           Theta(1)xO(n), propagation: |."""
        pass

    #--- ORDER OPERATIONS, sorts -----------------------------------------------
    
    def insertAllND(self, channelA, channelB):
        """Insert all items from channelA into channelB.
           Precondition: channelB is in non-decreaisng order, possibly empty;
           Post: channelB contains all items from both channels, sorted.
                 channelA becomes empty. 
           Theta(m)xTheta(m+n), 
           where m is the length of channelA, and n is the length of channelB."""
           # propagation: |-\
        pass

    #---------------------------------------------------------------------------
    def iSort(self, channelA): 
        """Theta(n)xTheta(n)""" # propagation: |-\.
        pass
        
    def workFromEnd(self, channelA): 
        """Theta(n)xTheta(n)""" # propagation: |-\.
        pass
    
    def pullXinsertND(self, channelA):
        """Precondition: the part of the chain below the top element is sorted
           (non-decreasing).
           Post: the chain is sorted.
           Pulls up items smaller than the top item and
           moves the top item into the gap.
           pull(A)XinsertND(A)
           Theta(1)xO(n)""" # propagation: \."""
        pass

    #---------------------------------------------------------------------------

    def sSort(self, channelA):
        if not self.bit[channelA]: # if CPE's channel A is non-empty
            # Domino:
            # sSort(A)            ---
            #                     ---
            #                     wwW
            #         minToTop(A) vv^ sSort(A)
            self.connectorLower.send_o("minToTop", channelA)
            # Send channel A word:
            self.connectorLower.send_w(self.word[channelA]) 
            # Send minSoFar:
            self.connectorLower.send_w(self.word[channelA]) 
            # Receive min and put in chA, discard the bit:
            self.word[channelA],_ = self.connectorLower.receive_W()
            self.connectorLower.send_o("sSort", channelA)
        else: # if current CPE terminates the list
            # Domino:
            # sSort(A)
            #
            #
            # 
            pass

    def minToTop(self, channelA):
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            # Domino:
            # minToTop(A) vv             ---^
            #             ww             ---W
            #             --             wwW-
            #             -- minToTop(A) vv^-
            # Preparation for shifting items down:
            # Receive channelA word from top neighbor:
            self.temp_w[0] = self.connectorUpper.receive_w() 
            # Receive minSoFar from top neighbor:
            self.temp_w[1] = self.connectorUpper.receive_w() 
            self.connectorLower.send_o("minToTop", channelA)
            # Preparation for shifting items down:
            # Send channelA word down:
            self.connectorLower.send_w(self.word[channelA]) 
            # Update minSoFar and send it down:
            if self.word[channelA] < self.temp_w[1]:
                self.connectorLower.send_w(self.word[channelA]) 
            else:
                self.connectorLower.send_w(self.temp_w[1]) 
            # Receive (min, found) pair:
            #     min - minimum value in the list under consideration.
            #     found - True, if the location of min has been found.
            self.temp_w[1],self.temp_b[1] = \
                self.connectorLower.receive_W()
            #print(self.name, self.temp_w[1], self.temp_b[1]) # debug.    
            # Possibly start shifting, and send up (min, found):
            if not self.temp_b[1] \
                   and self.word[channelA]!=self.temp_w[1]:
                self.connectorUpper.send_W(self.temp_w[1],False) 
            else:
                self.word[channelA] = self.temp_w[0] # shift down chA
                self.connectorUpper.send_W(self.temp_w[1],True) 
        elif self.bit[channelA]: # if current CPE terminates the list
            # Domino:
            # minToTop(A) vv^
            #             wwW
            #             ---
            #             ---
            self.connectorUpper.receive_w() # from chA, discard
            # Receive minSoFar:
            self.temp_w[1] = self.connectorUpper.receive_w() 
            # Send up (min, found) where found=False:
            self.connectorUpper.send_W(self.temp_w[1],False) 

    #---------------------------------------------------------------------------

    def bSort(self, channelA):
        """Theta(n)xTheta(n), propagation: ."""
        pass
            
    def bubbleDownBeginND(self, channelA):
        """Bubbles the biggest item to the bottom
           Marks the bottom bit = False. Marks all the bits above = True.
           At this point the sorted part consists of this single item.
           This is a non-standard use of the bits: True does not mean empty.
           Theta(1)xTheta(n), propagation: ."""
        pass

    def bubbleDownND(self, channelA):
        """Bubbles the biggest item to the lowest CPE whose bit == True.
           Changes that bit to False.
           In this way one item has been added to the sorted part.
           Theta(1)xO(n), propagation: ."""
        pass

    #--- ORDER OPERATIONS, merge -----------------------------------------------

    def mergeNDsimple(self, channelA, channelB, resultChannel): 
        """ """
        pass

    #---------------------------------------------------------------------------
    def mergeND(self, channelA, channelB): 
        pass

    # === INDEXING OPERATIONS =============================================

    def length(self, channelA):
        pass

    def lengthAux(self, channelA):
        pass

    # ---------------------------------------------------------------------

    def getItem(self, channelA):
        pass

    # ---------------------------------------------------------------------

    def setItem0(self, channelA):
        pass

    def setItem(self, channelA):
        pass
    
    # ---------------------------------------------------------------------

    def getSetItem(self, channelA):
        pass

    # ---------------------------------------------------------------------

    def memberIndex(self, channelA): 
        pass

    def memberIndexAux(self, channelA): 
        pass

    # ------------------------------------------------------------------------

    def insertAtIndex0(self, channelA):
        pass

    def insertAtIndex(self, channelA):
        pass

    # ------------------------------------------------------------------------

    def deleteAtIndex(self, channelA):
        pass


    def deleteGetAtIndex(self, channelA):
        pass


###############################################################################
