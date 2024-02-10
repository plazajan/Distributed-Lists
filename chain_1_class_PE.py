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
        self.connectorUpper.send_b(self.bit[channelA])

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
        self.bit[channelA] = True
        self.bit[channelB] = True

    #---------------------------------------------------------------------------
    def first(self, channelA):
        """Sends up the Word from the current CPE'. 
           Theta(1)xTheta(1), non-propagating."""
        # first(A) ^ 
        #          W
        #          -
        # none     - 
        self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])

    # === LIST OPERATIONS, whole chain operations ========================================

    def copy(self, channelA, resultChannel):
        """Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # copy(A,R)
            # 
            # 
            # copy(A,R)
            self.connectorLower.send_o("copy", channelA, resultChannel)
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False
        elif self.bit[channelA]:
            # copy(A,R)
            # 
            # 
            # none
            self.bit[resultChannel] = True

    #---------------------------------------------------------------------------
    def move(self, channelA, resultChannel):
        """Implements copy(A,R) x clear(A).
           Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # move(A,R)
            # 
            # 
            # copy(A,R)
            self.connectorLower.send_o("copy", channelA, resultChannel)
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False
            self.bit[channelA] = True
        elif self.bit[channelA]:
            # move(A,R)
            # 
            # 
            # none
            self.bit[resultChannel] = True
            
    #---------------------------------------------------------------------------
    def swap(self, channelA, channelB):
        """Theta(1)xTheta(n), where n is the length of the longer channel,
           propagation |."""
        if not self.bit[channelA] and not self.bit[channelB]:
            # swap(A,B)
            # 
            # 
            # swap(A,B)
            self.connectorLower.send_o("swap", channelA, channelB)
            self.temp_w[0] = self.word[channelA]
            self.word[channelA] = self.word[channelB]
            self.word[channelB] = self.temp_w[0]
        elif not self.bit[channelA] and self.bit[channelB]:
            # swap(A,B)
            # 
            # 
            # copy(A,B)
            self.connectorLower.send_o("copy", channelA, channelB)
            self.word[channelB] = self.word[channelA]
            self.bit[channelB] = False
            self.bit[channelA] = True
        elif self.bit[channelA] and not self.bit[channelB]:
            # swap(A,B)
            # 
            # 
            # copy(A,B)
            self.connectorLower.send_o("copy", channelB, channelA)
            self.word[channelA] = self.word[channelB]
            self.bit[channelA] = False
            self.bit[channelB] = True
        elif self.bit[channelA] and self.bit[channelB]:
            # swap(A,B)
            # 
            # 
            # none
            pass
        
    # --------------------------------------------------------------------------
    def setAll(self, channelA):
        """Sets each word of the channel content to the given word.
           Does not affect the values below the channel content terminator.
           Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # setAll(A) v- 
            #           w-
            #           -w
            # setAll(A) -v 
            self.word[channelA] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("setAll", channelA)
            self.connectorLower.send_w(self.word[channelA])
        elif self.bit[channelA]:
            # setAll(A) v 
            #           w
            #           -
            # none      -
            self.word[channelA] = self.connectorUpper.receive_w()

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
        if not self.bit[channelA]:
            # push(A) v- 
            #         w-
            #         -w
            # push(A) -v 
            self.temp_w[0] = self.word[channelA]
            self.word[channelA] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("push", channelA)
            self.connectorLower.send_w(self.temp_w[0])
        elif self.bit[channelA]:
            # push(A)  v 
            #          w
            #          -
            # clear(A) - 
            self.word[channelA] = self.connectorUpper.receive_w()
            self.bit[channelA] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelA)
            
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
        if not self.bit[channelA]:
            # Domino:
            # pull(A) ^- 
            #         W-
            #         -W
            # pull(A) -^
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            self.connectorLower.send_o("pull", channelA)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
        elif self.bit[channelA]:
            # Domino:
            # pull(A) ^
            #         W
            #         -
            # none    - 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])

    #---------------------------------------------------------------------------
    def replaceGetFirst(self, channelA):
        """Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # replaceGetFirst(A) v^
        #                    wW
        #                    --
        # none               --
        self.temp_w[0] = self.connectorUpper.receive_w()
        self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
        self.word[channelA] = self.temp_w[0] # possibly modifies the empty word.
        
    # --- LIST OPERATIONS, bottom operations -----------------------------------------------

    def last(self, channelA):
        """Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # last(A) -^ 
            #         -W
            #         W-
            # last(A) ^-
            self.connectorLower.send_o("last", channelA)
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            if self.temp_b[0]:
                self.connectorUpper.send_W(self.word[channelA],
                                           self.bit[channelA])
            elif not self.temp_b[0]:
                self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])
        elif self.bit[channelA]:
            # Domino:
            # last(A) ^ 
            #         W
            #         -
            # none    - 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])

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
        if not self.bit[channelA]:
            # Domino:
            # removeLast(A) ^- 
            #               b-
            #               -b
            # removeLast(A) -^ 
            self.connectorUpper.send_b(False)
            self.connectorLower.send_o("removeLast", channelA)
            self.bit[channelA] = self.connectorLower.receive_b()
        elif self.bit[channelA]:
            # Domino:
            # removeLast(A) ^ 
            #               b
            #               -
            # none          - 
            self.connectorUpper.send_b(True)

    #---------------------------------------------------------------------------
    def removeGetLast(self, channelA):
        """Remove and send up the last item in the chain.
           Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # removeGetLast(A) -^ 
            #                  -W
            #                  W-
            # removeGetLast(A) ^- 
            self.connectorLower.send_o("removeGetLast", channelA)
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            if self.temp_b[0]:
                self.connectorUpper.send_W(self.word[channelA],
                                           self.bit[channelA])
                self.bit[channelA] = True
            elif not self.temp_b[0]:
                self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])
        elif self.bit[channelA]:
            # Domino:
            # removeGetLast(A) ^ 
            #                  W
            #                  -
            # none             -
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])

    #---------------------------------------------------------------------------
    def replaceLast(self, channelA):
        """Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # Domino:
            # replaceLast(A) v^-- 
            #                wb--
            #                --wb
            # replaceLast(A) --v^ 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_b(self.bit[channelA])
            self.connectorLower.send_o("replaceLast", channelA)
            self.connectorLower.send_w(self.temp_w[0])
            self.temp_b[0] = self.connectorLower.receive_b()
            if self.temp_b[0]:
                self.word[channelA] = self.temp_w[0]
            elif not self.temp_b[0]:
                pass
        elif self.bit[channelA]:
            # Domino:
            # replaceLast(A) v^ 
            #                wb
            #                --
            # none           --
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_b(self.bit[channelA])

    #---------------------------------------------------------------------------
    def replaceGetLast(self, channelA):
        """Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # replaceGetLast(A) v--^ 
            #                   w--W
            #                   -wW-
            # replaceGetLast(A) -v^- 
            self.temp_w[0] = self.connectorUpper.receive_w() # get replacement
            self.connectorLower.send_o("replaceGetLast", channelA)
            self.connectorLower.send_w(self.temp_w[0]) # send replacement down
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W() 
            if self.temp_b[0]:
                self.connectorUpper.send_W(self.word[channelA], False)
                self.word[channelA] = self.temp_w[0]
            elif not self.temp_b[0]:
                self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])
        elif self.bit[channelA]:
            # Domino:
            # replaceGetLast(A) v^ 
            #                   wW
            #                   --
            # none              -- 
            self.temp_w[0] = self.connectorUpper.receive_w() # get replacement
            self.connectorUpper.send_W(self.temp_w[0], True)

    # --- LIST OPERATIONS, rotations -----------------------------------------------------

    def rotateDown(self, channelA):
        """Executed only by the top CPE in the chain.
           Implements a=pull(A) x addLast(A,a).
           Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # rotateDown(A)       ^-- 
            #                     W--
            #                     -Ww
            # rotateDownNonTop(A) -^v 
            self.connectorUpper.send_W(self.word[channelA],
                                       self.bit[channelA]) #U^
            self.temp_w[0] = self.word[channelA]
            self.connectorLower.send_o("pullXaddLast", channelA)
            self.word[channelA], self.bit[channelA] = \
                               self.connectorLower.receive_W() #L^
            self.connectorLower.send_w(self.temp_w[0]) #Lv
            if self.bit[channelA]:
                self.bit[channelA] = False
                self.word[channelA] = self.temp_w[0]
            elif not self.bit[channelA]:
                pass
        elif self.bit[channelA]:
            # Domino:
            # rotateDown(A) ^ 
            #               W
            #               -
            # none          - 
            self.connectorUpper.send_W(self.word[channelA],
                                       self.bit[channelA])

    def pullXaddLast(self, channelA):
        """A helper for rotateDown, executed by non-top PEs in the chain.
           Implements pull(A) x addLast(A,a).
           Theta(1)xTheta(n), propagation |."""
        if not self.bit[channelA]:
            # Domino: 
            # pullXaddLast(A) ^v-- 
            #                 Ww--
            #                 --Ww
            # pullXaddLast(A) --^v 
            self.connectorUpper.send_W(self.word[channelA],
                                       self.bit[channelA]) #U^
            self.temp_w[0] = self.connectorUpper.receive_w() #Uv
            self.connectorLower.send_o("pullXaddLast", channelA)
            self.word[channelA], self.bit[channelA] = \
                        self.connectorLower.receive_W() #L^
            self.connectorLower.send_w(self.temp_w[0]) #Lv
            if self.bit[channelA]:
                self.bit[channelA] = False
                self.word[channelA] = self.temp_w[0]
            elif not self.bit[channelA]:
                pass
        elif self.bit[channelA]:
            # Domino:
            # pullXaddLast(A) ^v 
            #                 Ww
            #                 --
            # none            --
            self.connectorUpper.send_W(self.word[channelA],
                                       self.bit[channelA]) #U^
            self.temp_w[0] = self.connectorUpper.receive_w() #Uv

    #---------------------------------------------------------------------------
    def rotateUp(self, channelA):
        """Executed only by the top CPE in the chain.
           Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # rotateUp(A)           --^ 
            #                       --W
            #                       wW-
            # pushXremoveGetLast(A) v^- 
            self.connectorLower.send_o("pushXremoveGetLast", channelA)
            self.connectorLower.send_w(self.word[channelA])
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            if not self.temp_b[0]:
                self.word[channelA] = self.temp_w[0]
            elif self.temp_b[0]:
                pass
            self.connectorUpper.send_W(self.word[channelA], False)
        elif self.bit[channelA]:
            # Domino:
            # rotateUp(A) ^ 
            #             W
            #             -
            # none        -
            self.connectorUpper.send_W(Any, True)

    def pushXremoveGetLast(self, channelA):
        """A helper for rotateUp, executed by non-top PEs in the chain.
           Theta(n)xTheta(n), propagation |/."""
        if not self.bit[channelA]:
            # Domino:
            # pushXremoveGetLast(A) v--^ 
            #                       w--W
            #                       -wW-
            # pushXremoveGetLast(A) -v^- 
            self.temp_w[0] = self.word[channelA]
            self.word[channelA] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("pushXremoveGetLast", channelA)
            self.connectorLower.send_w(self.temp_w[0])
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            self.connectorUpper.send_W(self.temp_w[0], False)
        elif self.bit[channelA]:
            # Domino:
            # pushXremoveGetLast(A) v^ 
            #                       wW
            #                       --
            # none                  -- 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(self.temp_w[0], True)
            
    #--- LIST OPERATIONS, reverse -----------------------------------------------------

    def reverseSimple(self, channelA, resultChannel):
        """For instructional purposes.
           Theta(n)xTheta(n)""" # propagation: \-|.
        if not self.bit[channelA]:
            # Domino:
            # reverseSimple(A,R) -                   -         -
            #                    -                   -         -
            #                    W                   w         W
            #            pull(A) ^ clear(R) (push(R) v pull(A) ^)*
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False
            self.connectorLower.send_o("pull", channelA)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
            self.connectorLower.send_o("clear", resultChannel)
            while not self.bit[channelA]:
                self.connectorLower.send_o("push", resultChannel)
                self.connectorLower.send_w(self.word[resultChannel])
                self.word[resultChannel] = self.word[channelA]
                self.connectorLower.send_o("pull", channelA)
                self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
        elif self.bit[channelA]:
            # Domino:
            # reverseSimple(A,R) 
            #                    
            #
            # none
            self.bit[resultChannel] = True

    def reverse(self, channelA, resultChannel):
        """Theta(n)xTheta(n)""" # propagation: \-|.
        if not self.bit[channelA]:
            # Domino:
            # reverse(A,R)  -                 --
            #               -                 --
            #               W                 wW
            # pullXClear(A) ^ (pushXpull(A,R) v^)*
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False
            self.connectorLower.send_o("pullXclear",
                                       channelA, resultChannel)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
            while not self.bit[channelA]:
                self.connectorLower.send_o("pushXpull",
                                           channelA, resultChannel)
                self.connectorLower.send_w(self.word[resultChannel])
                self.word[resultChannel] = self.word[channelA]
                self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
        elif self.bit[channelA]:
            # Domino:
            # reverse(A,R)
            #
            #
            # none
            self.bit[resultChannel] = True

    def pullXclear(self, channelA, channelB):
        """pull(A) x clear(B).
           Theta(1)xTheta(n), propagation: |."""
        if not self.bit[channelA]:
            # Domino:
            # pullXclear(A,B) ^- 
            #                 W-
            #                 -W
            #         pull(A) -^ 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            self.connectorLower.send_o("pull", channelA)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
            self.bit[channelB] = True
        elif self.bit[channelA]:
            # Domino:
            # pullXclear(A,B) ^ 
            #                 W
            #                 -
            # none            - 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            self.bit[channelB] = True

    def pushXpull(self, channelA, channelB):
        """push(channelB) x pull(channelA)
           Theta(1)xTheta(n), propagation: |."""
        if not self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # pushXpull(A,B) v-^- 
            #                w-W-
            #                -w-W
            # pushXpull(A,B) -v-^ 
            self.temp_w[0] = self.word[channelB]
            self.word[channelB] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("pushXpull",
                                       channelA, channelB)
            self.connectorLower.send_w(self.temp_w[0])
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
        elif not self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # pushXpull(A,B)  v^- 
            #                 wW-
            #                 --W
            # pullXclear(A,B) --^ 
            self.word[channelB] = self.connectorUpper.receive_w()
            self.bit[channelB] = False
            self.extend() 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            self.connectorLower.send_o("pullXclear",
                                       channelA, channelB)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()
        elif self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # pushXpull(A,B) v-^ 
            #                w-W
            #                -w-
            #        push(B) -v- 
            self.temp_w[0] = self.word[channelB]
            self.word[channelB] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("push", channelB)
            self.connectorLower.send_w(self.temp_w[0])
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
        elif self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # pushXpull(A,B) v 
            #                w
            #                -
            #       clear(B) - 
            self.word[channelB] = self.connectorUpper.receive_w()
            self.bit[channelB] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelB)
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])        

    # === ORDER OPERATIONS =====================================================

    def min(self, channelA):
        """Sends up the minimum element from the channel.
           Theta(n)xTheta(n), propagation: |/."""
        if not self.bit[channelA]:
            # Domino:
            # min(A) -^ 
            #        -W
            #        W-
            # min(A) ^- 
            self.connectorLower.send_o("min", channelA)
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            if self.temp_b[0]:
                self.connectorUpper.send_W(self.word[channelA],
                                           self.bit[channelA])
            elif not self.temp_b[0]:
                if self.temp_w[0] < self.word[channelA]:
                    self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])
                else:
                    self.connectorUpper.send_W(self.word[channelA],
                                               self.bit[channelA])
        elif self.bit[channelA]:
            # Domino:
            # min(A) ^ 
            #        W
            #        -
            # none   - 
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])

    #---------------------------------------------------------------------------  
    def memberND(self, channelA):
        """Precondition: channel elements are in non-decreasing order.
           O(n)xO(n), propagation: |/."""
        if not self.bit[channelA]:
            self.temp_w[0] = self.connectorUpper.receive_w()
            if self.word[channelA] == self.temp_w[0]:
                # Domino:
                # memberND(A) v^ 
                #             wb
                #             --
                # none        -- 
                self.connectorUpper.send_b(True)
            elif self.word[channelA] > self.temp_w[0]:
                # Domino:
                # memberND(A) v^ 
                #             wb
                #             --
                # none        -- 
                self.connectorUpper.send_b(False)
            else:
                # Domino:
                # memberND(A) v--^ 
                #             w--b
                #             -wb-
                # memberND(A) -v^-  
                self.connectorLower.send_o("memberND", channelA)
                self.connectorLower.send_w(self.temp_w[0])
                self.temp_b[0] = self.connectorLower.receive_b()
                self.connectorUpper.send_b(self.temp_b[0])
        elif self.bit[channelA]:
            # Domino:
            # memberND(A) v^ 
            #             wb
            #             --
            # none        -- 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_b(False)

    #---------------------------------------------------------------------------  
    def insertND(self, channelA): 
        """Precondition: channel elements are in non-decreasing order.
           Theta(1)xTheta(n), propagation: |."""
        if not self.bit[channelA]:
            self.temp_w[0] = self.connectorUpper.receive_w()
            if self.temp_w[0] > self.word[channelA]:
                # Domino:
                # insertND(A) v- 
                #             w-
                #             -w
                # insertND(A) -v 
                self.connectorLower.send_o("insertND", channelA)
                self.connectorLower.send_w(self.temp_w[0])
            else:
                # Domino:
                # insertND(A) v- 
                #             w-
                #             -w
                #     push(A) -v 
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.word[channelA])
                self.word[channelA] = self.temp_w[0]
        elif self.bit[channelA]:
            # Domino:
            # insertND(A) v 
            #             w
            #             -
            #    clear(A) - 
            self.word[channelA] = self.connectorUpper.receive_w()
            self.bit[channelA] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelA)

    #---------------------------------------------------------------------------  
    def insertUniqueI(self, channelA): 
        """Precondition: channel elements are in increasing order.
           Theta(1)xO(n), propagation: |."""
        if not self.bit[channelA]:
            self.temp_w[0] = self.connectorUpper.receive_w()
            if self.temp_w[0] > self.word[channelA]:
                # Domino:
                # insertUniqueI(A) v-
                #                  w-
                #                  -w
                # insertUniqueI(A) -v 
                self.connectorLower.send_o("insertUniqueI", channelA)
                self.connectorLower.send_w(self.temp_w[0])
            elif self.temp_w[0] < self.word[channelA]:
                # Domino:
                # insertUniqueI(A) v-
                #                  w-
                #                  -w
                #          push(A) -v
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.word[channelA])
                self.word[channelA] = self.temp_w[0]
            elif self.temp_w[0] == self.word[channelA]:
                # Domino:
                # insertUniqueI(A) v
                #                  w
                #                  -
                # none             -
                pass
        elif self.bit[channelA]:
            # Domino:
            # insertUniqueI(A) v 
            #                  w
            #                  -
            #         clear(A) - 
            self.word[channelA] = self.connectorUpper.receive_w()
            self.bit[channelA] = False
            self.extend() 
            self.connectorLower.send_o("clear", channelA)

    #--- ORDER OPERATIONS, sorts -----------------------------------------------
    
    def insertAllND(self, channelA, channelB):
        """Insert all items from channelA into channelB.
           Precondition: channelB is in non-decreaisng order, possibly empty;
           Post: channelB contains all items from both channels, sorted.
                 channelA becomes empty. 
           Theta(m)xTheta(m+n), 
           where m is the length of channelA, and n is the length of channelB."""
           # propagation: |-\
        # Exercise: rewrite with pull(A)xclear(B) and insert(B)xpull(A).
        if not self.bit[channelA]:
            if self.bit[channelB]:
                # Domino:
                # insertAllND(A,B)   -                       -         -
                #                    -                       -         -
                #                    W                       w         W
                #            pull(A) ^ clear(B) (insertND(B) v pull(A) ^)+
                self.word[channelB] = self.word[channelA]
                self.connectorLower.send_o("pull", channelA)
                self.word[channelA], self.bit[channelA] = \
                                         self.connectorLower.receive_W()
                self.connectorLower.send_o("clear", channelB)
                self.bit[channelB] = False
            elif not self.bit[channelB]:
                # Domino:
                # insertAllND(A,B)   -         -
                #                    -         -
                #                    w         W
                #       (insertND(B) v pull(A) ^)+
                pass
            while not self.bit[channelA]:  
                self.connectorLower.send_o("insertND", channelB)
                if self.word[channelA] >= self.word[channelB]:
                    self.connectorLower.send_w(self.word[channelA])
                elif self.word[channelA] < self.word[channelB]:
                    self.connectorLower.send_w(self.word[channelB])
                    self.word[channelB] = self.word[channelA] 
                self.connectorLower.send_o("pull", channelA)
                self.word[channelA], self.bit[channelA] = \
                                     self.connectorLower.receive_W()
        elif self.bit[channelA]:
            # Domino:
            # insertAllND(A,B) 
            # 
            # 
            # none
            pass

    #---------------------------------------------------------------------------
    def iSort(self, channelA): 
        """Theta(n)xTheta(n)""" # propagation: |-\.
        if not self.bit[channelA]:
            # Domino:
            # iSort(A) -                  --
            #                    -                  --
            #                    b                  ww
            #     workFromEnd(A) ^ pullXinsertND(A) v^
            self.connectorLower.send_o("workFromEnd", channelA)
            self.connectorLower.receive_b() # just for synchronization
            self.connectorLower.send_o("pullXinsertND", channelA) 
            self.connectorLower.send_w(self.word[channelA]) 
            self.temp_w[0] = self.connectorLower.receive_w()
            if self.temp_w[0] < self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
        elif self.bit[channelA]:
            # Domino:
            # iSort(A)
            #
            #
            # none
            pass
        
    def workFromEnd(self, channelA): 
        """Theta(n)xTheta(n)""" # propagation: |-\.
        if not self.bit[channelA]:
            # Domino:
            # workFromEnd(A) -^                  --
            #                -b                  --
            #                b-                  ww
            # workFromEnd(A) ^- pullXinsertND(A) v^ 
            self.connectorLower.send_o("workFromEnd", channelA)
            self.connectorLower.receive_b() # just for synchronization
            self.connectorUpper.send_b(Any) # just for synchronization
            self.connectorLower.send_o("pullXinsertND", channelA) 
            self.connectorLower.send_w(self.word[channelA])
            self.temp_w[0] = self.connectorLower.receive_w()
            if self.temp_w[0] < self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
        elif self.bit[channelA]:
            # Domino:
            # workFromEnd(A) ^ 
            #                b
            #                -
            # none           - 
            self.connectorUpper.send_b(Any) # just for synchronization
            
    def pullXinsertND(self, channelA):
        """Precondition: the part of the chain below the top element is sorted
           (non-decreasing).
           Post: the chain is sorted.
           Pulls up items smaller than the top item and
           moves the top item into the gap.
           pull(A)XinsertND(A)
           Theta(1)xO(n)""" # propagation: \."""
        if not self.bit[channelA]:
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_w(self.word[channelA])
            if self.temp_w[0] > self.word[channelA]:
                # Domino:   
                # pullXinsertND(A) v^-- 
                #                  ww--
                #                  --ww               
                # pullXinsertND(A) --v^ 
                self.connectorLower.send_o("pullXinsertND", channelA)
                self.connectorLower.send_w(self.temp_w[0])
                self.word[channelA] = self.connectorLower.receive_w()
                if self.temp_w[0] < self.word[channelA]:
                    self.word[channelA] = self.temp_w[0]
            elif self.temp_w[0] <= self.word[channelA]:
                # Domino:
                # pullXinsertND(A) v^
                #                  ww
                #                  --
                # none             --
                pass
        elif self.bit[channelA]:
            # Domino:
            # pullXinsertND(A) v^ 
            #                  ww
            #                  --
            # none             --  
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_w(self.temp_w[0])

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
        if not self.bit[channelA]:
            # Domino:
            # bSort(A)             --                  --
            #                      --                  --
            #                      wW                  wW
            # bubbleDownBeginND(A) v^ (bubbleDownND(A) v^)*
            self.connectorLower.send_o("bubbleDownBeginND", channelA)
            self.connectorLower.send_w(self.word[channelA])
            self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
            if self.temp_b[0] and self.temp_w[0] < self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
            while self.temp_b[0]:
                self.connectorLower.send_o("bubbleDownND", channelA)
                self.connectorLower.send_w(self.word[channelA])
                self.temp_w[0], self.temp_b[0] = self.connectorLower.receive_W()
                if self.temp_b[0] and self.temp_w[0] < self.word[channelA]:
                    self.word[channelA] = self.temp_w[0]
        elif self.bit[channelA]:
            # Domino:
            # bSort(A)  
            #                     
            #            
            # none  
            pass 
            
    def bubbleDownBeginND(self, channelA):
        """Bubbles the biggest item to the bottom
           Marks the bottom bit = False. Marks all the bits above = True.
           At this point the sorted part consists of this single item.
           This is a non-standard use of the bits: True does not mean empty.
           Theta(1)xTheta(n), propagation: ."""
        if not self.bit[channelA]:
            # Domino:
            # bubbleDownBeginND(A) v^-- 
            #                      wW--
            #                      --wW
            # bubbleDownBeginND(A) --v^ 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(self.word[channelA], True)
            if self.temp_w[0] > self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
            self.connectorLower.send_o("bubbleDownBeginND", channelA)
            self.connectorLower.send_w(self.word[channelA])
            self.temp_w[0], self.bit[channelA] = self.connectorLower.receive_W()
            if self.bit[channelA] and self.temp_w[0] < self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
        elif self.bit[channelA]:
            # Domino:
            # bubbleDownBeginND(A) v^ 
            #                      wW
            #                      --
            # none                 -- 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(Any, False)

    def bubbleDownND(self, channelA):
        """Bubbles the biggest item to the lowest CPE whose bit == True.
           Changes that bit to False.
           In this way one item has been added to the sorted part.
           Theta(1)xO(n), propagation: ."""
        if self.bit[channelA]:
            # Domino:
            # bubbleDownBeginND(A) v^-- 
            #                      wW--
            #                      --wW
            # bubbleDownBeginND(A) --v^ 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(self.word[channelA], True)
            if self.temp_w[0] > self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
            self.connectorLower.send_o("bubbleDownND", channelA)
            self.connectorLower.send_w(self.word[channelA])
            self.temp_w[0], self.bit[channelA] = self.connectorLower.receive_W()
            if self.bit[channelA] and self.temp_w[0] < self.word[channelA]:
                self.word[channelA] = self.temp_w[0]
        elif not self.bit[channelA]:
            # Domino:
            # bubbleDownBeginND(A) v^ 
            #                      wW
            #                      --
            # none                 -- 
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(Any, False)

    #--- ORDER OPERATIONS, merge -----------------------------------------------

    def mergeNDsimple(self, channelA, channelB, resultChannel): 
        """ """
        if not self.bit[channelA] and not self.bit[channelB]:
            if self.word[channelA] <= self.word[channelB]:
                # Domino:
                # mergeNDsimple(A,B,R) - 
                #                      -
                #                      w
                #              push(B) v  mergeNDsimple(A,B,R)
                self.connectorLower.send_o("push", channelB)
                self.connectorLower.send_w(self.word[channelB])
                self.connectorLower.send_o("mergeNDsimple", channelA, channelB,
                                           resultChannel)
                self.word[resultChannel] = self.word[channelA]
                self.bit[resultChannel] = False
            elif self.word[channelA] > self.word[channelB]:
                # Domino:
                # mergeNDsimple(A,B,R) - 
                #                      -
                #                      w
                #              push(A) v  mergeNDsimple(A,B,R)
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.word[channelA])
                self.connectorLower.send_o("mergeNDsimple", channelA, channelB,
                                           resultChannel)
                self.word[resultChannel] = self.word[channelB]
                self.bit[resultChannel] = False
        elif not self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # mergeNDsimple(A,B,R)
            # 
            # 
            # copy(A,R)
            self.connectorLower.send_o("copy", channelA, resultChannel)
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False
        elif self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # mergeNDsimple(A,B,R)
            # 
            # 
            # copy(B,R)
            self.connectorLower.send_o("copy", channelB, resultChannel)
            self.word[resultChannel] = self.word[channelB]
            self.bit[resultChannel] = False
        elif self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # mergeNDsimple(A,B,R)
            # 
            # 
            # none
            self.bit[resultChannel] = True

    #---------------------------------------------------------------------------
    def mergeND(self, channelA, channelB): 
        if not self.bit[channelB] and not self.bit[channelA]:
            if self.word[channelB] <= self.word[channelA]:
                # Domino:
                # mergeNDsimple(A,B,R) - 
                #                      -
                #                      w
                #              push(A) v  mergeNDsimple(A,B,R)
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.word[channelA])
                self.connectorLower.send_o("mergeND", channelA, channelB) 
            elif self.word[channelB] > self.word[channelA]:
                # Domino:
                # mergeNDsimple(A,B,R) - 
                #                      -
                #                      w
                #              push(B) v  mergeNDsimple(A,B,R)
                self.connectorLower.send_o("push", channelB)
                self.connectorLower.send_w(self.word[channelB])
                self.connectorLower.send_o("mergeND", channelA, channelB)
                self.word[channelB] = self.word[channelA]
        elif not self.bit[channelB] and self.bit[channelA]:
            # Domino:
            # mergeND(A,B)
            # 
            # 
            # none
            pass
        elif self.bit[channelB] and not self.bit[channelA]:
            # Domino:
            # mergeND(A,B)
            # 
            # 
            # copy(A,B)
            self.connectorLower.send_o("copy", channelA, channelB)
            self.word[channelB] = self.word[channelA]
            self.bit[channelB] = False
        elif self.bit[channelB] and self.bit[channelA]:
            # Domino:
            # mergeND(A,B)
            # 
            # 
            # none
            pass

    # === INDEXING OPERATIONS =============================================

    def length(self, channelA):
        if self.bit[channelA]: # if CPE is empty
            self.connectorUpper.send_w(0)
        elif not self.bit[channelA]: # if CPE is not empty
            self.connectorLower.send_o("lengthAux", channelA)
            self.connectorLower.send_w(1)
            self.temp_w[0] = self.connectorLower.receive_w()
            self.connectorUpper.send_w(self.temp_w[0])

    def lengthAux(self, channelA):
        self.temp_w[0] = self.connectorUpper.receive_w()
        if self.bit[channelA]: # if CPE is empty
            self.connectorUpper.send_w(self.temp_w[0])
        elif not self.bit[channelA]: # if CPE is not empty
            self.connectorLower.send_o("lengthAux", channelA)
            self.temp_w[0] += 1
            self.connectorLower.send_w(self.temp_w[0])
            self.temp_w[0] = self.connectorLower.receive_w()
            self.connectorUpper.send_w(self.temp_w[0])

    # ---------------------------------------------------------------------

    def getItem(self, channelA):
        self.temp_w[0] = self.connectorUpper.receive_w() # index
        if self.bit[channelA]: # if CPE is empty
            self.connectorUpper.send_W(Any,True) # notFound=True
        else: # CPE non-empty
            if self.temp_w[0] == 0: # found it
                self.connectorUpper.send_W(self.word[channelA], False)
            else: # keep looking
                self.temp_w[0] -= 1 # update index
                self.connectorLower.send_o("getItem", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # send index
                self.temp_w[0], self.temp_b[0] =self.connectorLower.receive_W()
                self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])

    # ---------------------------------------------------------------------

    def setItem0(self, channelA):
        self.temp_w[0] = self.connectorUpper.receive_w() # index
        self.temp_w[1] = self.connectorUpper.receive_w() # item
        if self.bit[channelA]: # if CPE is empty
            pass
        else: # CPE non-empty
            if self.temp_w[0] == 0: # found it
                self.word[channelA] = self.temp_w[1]
            else: # keep looking
                self.temp_w[0] -= 1 # update index
                self.connectorLower.send_o("setItem0", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # send index
                self.connectorLower.send_w(self.temp_w[1]) # send item

    def setItem(self, channelA):
        self.temp_w[0] = self.connectorUpper.receive_w() # index
        self.temp_w[1] = self.connectorUpper.receive_w() # item
        if self.bit[channelA]: # if CPE is empty
            self.connectorUpper.send_b(True)
        else: # CPE non-empty
            if self.temp_w[0] == 0: # found it
                self.connectorUpper.send_b(False)
                self.word[channelA] = self.temp_w[1]
            else: # keep looking
                self.temp_w[0] -= 1 # update index
                self.connectorLower.send_o("setItem", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # send index
                self.connectorLower.send_w(self.temp_w[1]) # send item
                self.temp_b[0] = self.connectorLower.receive_b()
                self.connectorUpper.send_b(self.temp_b[0])

    # ---------------------------------------------------------------------

    def getSetItem(self, channelA):
        self.temp_w[0] = self.connectorUpper.receive_w() # index
        self.temp_w[1] = self.connectorUpper.receive_w() # item
        if self.bit[channelA]: # if CPE is empty
            self.connectorUpper.send_W(Any,True) 
        else: # CPE non-empty
            if self.temp_w[0] == 0: # found it
                self.connectorUpper.send_W(self.word[channelA], False)
                self.word[channelA] = self.temp_w[1]
            else: # keep looking
                self.temp_w[0] -= 1 # update index
                self.connectorLower.send_o("getSetItem", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # send index
                self.connectorLower.send_w(self.temp_w[1]) # send item
                self.temp_w[0], self.temp_b[0] =self.connectorLower.receive_W()
                self.connectorUpper.send_W(self.temp_w[0], self.temp_b[0])

    # ---------------------------------------------------------------------

    def memberIndex(self, channelA): 
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # item
            if self.word[channelA] == self.temp_w[0]: # if found here
            # Domino
            # memberIndex v ^
            #             w W
            #             - -
            # none        - -
                self.connectorUpper.send_W(0,False) # index 0
            else: # keep looking below
            # Domino
            # memberIndex    v - - - ^
            #                w - - - W
            #                - w w W -
            # memberIndexAux - v v ^ -
                self.connectorLower.send_o("memberIndexAux", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # item
                self.connectorLower.send_w(0) # CPE's index
                self.temp_w[0],self.temp_b[0] = self.connectorLower.receive_W()
                self.connectorUpper.send_W(self.temp_w[0],self.temp_b[0])
        elif self.bit[channelA]: # if current CPE terminates the list
            # Domino
            # memberIndex v ^
            #             w W
            #             - -
            # none        - -            
            _ = self.connectorUpper.receive_w()
            self.connectorUpper.send_W(Any,True) # not found anywhere

    def memberIndexAux(self, channelA): 
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # item
            self.temp_w[1] = self.connectorUpper.receive_w() # index
            self.temp_w[1] += 1 # update index
            if self.word[channelA] == self.temp_w[0]: # found here
            # memberIndexAux v v ^
            #                w w W
            #                - - W -
            # none           - - ^ -                
                self.connectorUpper.send_W(self.temp_w[1],False)
            else: # keep looking below
            # memberIndexAux v v - - - ^
            #                w w - - - W
            #                - - w w W -
            # memberIndexAux - - v v ^ -            
                self.connectorLower.send_o("memberIndexAux", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # item
                self.connectorLower.send_w(self.temp_w[1]) # CPE's index
                self.temp_w[0],self.temp_b[0] = self.connectorLower.receive_W()
                self.connectorUpper.send_W(self.temp_w[0],self.temp_b[0])
        elif self.bit[channelA]: # if current CPE terminates the list
        # memberIndexAux v v ^
        #                w w W
        #                - - -
        # none           - - -  
            _ = self.connectorUpper.receive_w() # item
            _ = self.connectorUpper.receive_w() # index
            self.connectorUpper.send_W(Any,True) # not found anywhere

    # ------------------------------------------------------------------------

    def insertAtIndex0(self, channelA):
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # index
            self.temp_w[1] = self.connectorUpper.receive_w() # item
            if self.temp_w[0] == 0: # index found
                # insertAtIndex0 v v      - 
                #                w w      - 
                #                - -      w
                #                - - push v
                self.temp_w[0] = self.word[channelA] # old item
                self.word[channelA] = self.temp_w[1] # put item in channelA
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # push old item
            else: # index not found
                # insertAtIndex0 v v               - - 
                #                w w               - - 
                #                - -               w w 
                #                - - insertAtIndex v v 
                self.temp_w[0] -= 1 # adjust index
                self.connectorLower.send_o("insertAtIndex0", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # index
                self.connectorLower.send_w(self.temp_w[1]) # item
        elif self.bit[channelA]: # if current CPE terminates the list
            # insertAtIndex0 v v ^   
            #                w w b
            #                - - -
            #                - - - 
            _ = self.connectorUpper.receive_w() # index
            _ = self.connectorUpper.receive_w() # item

    def insertAtIndex(self, channelA):
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # index
            self.temp_w[1] = self.connectorUpper.receive_w() # item
            if self.temp_w[0] == 0: # index found
                # insertAtIndex v v ^      - 
                #               w w b      - 
                #               - - -      w
                #               - - - push v
                self.connectorUpper.send_b(False) # confirmation, index was good
                self.temp_w[0] = self.word[channelA] # old item
                self.word[channelA] = self.temp_w[1] # put item in channelA
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # push old item
            else: # index not found
                # insertAtIndex v v               - - - ^
                #               w w               - - - b
                #               - -               w w b -
                #               - - insertAtIndex v v ^ -
                self.temp_w[0] -= 1 # adjust index
                self.connectorLower.send_o("insertAtIndex", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # index
                self.connectorLower.send_w(self.temp_w[1]) # item
                self.temp_b[0] = self.connectorLower.receive_b()
                self.connectorUpper.send_b(self.temp_b[0])
        elif self.bit[channelA]: # if current CPE terminates the list
            # insertAtIndex v v ^   
            #               w w b
            #               - - -
            #               - - - 
            _ = self.connectorUpper.receive_w() # index
            _ = self.connectorUpper.receive_w() # item
            self.connectorUpper.send_b(True) # badIndex

    # ------------------------------------------------------------------------

    def deleteAtIndex(self, channelA):
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # index
            if self.temp_w[0] == 0: # index found
                # deleteAtIndex v      - 
                #               w      - 
                #               -      W
                #               - pull ^
                self.connectorLower.send_o("pull", channelA)
                self.word[channelA],self.bit[channelA] = \
                    self.connectorLower.receive_W()
            else: # index not found, keep looking
                # deleteAtIndex v               - 
                #               w               - 
                #               -               w 
                #               - deleteAtIndex v 
                self.temp_w[0] -= 1 # adjust index
                self.connectorLower.send_o("deleteAtIndex", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # index
        elif self.bit[channelA]: # if current CPE terminates the list
            # deleteAtIndex v   
            #               w
            #               -
            #               -
            _ = self.connectorUpper.receive_w() # index


    def deleteGetAtIndex(self, channelA):
        if not self.bit[channelA]: # if CPE's channelA is non-empty
            self.temp_w[0] = self.connectorUpper.receive_w() # index
            if self.temp_w[0] == 0: # index found
                # deleteAtIndex v ^      - 
                #               w b      - 
                #               - -      W
                #               - - pull ^
                self.connectorUpper.send_W(self.word[channelA],False) #
                self.connectorLower.send_o("pull", channelA)
                self.word[channelA],self.bit[channelA] = \
                    self.connectorLower.receive_W()
            else: # index not found, keep looking
                # deleteAtIndex v               - - ^
                #               w               - - W
                #               -               w W -
                #               - deleteAtIndex v ^ -
                self.temp_w[0] -= 1 # adjust index
                self.connectorLower.send_o("deleteGetAtIndex", channelA)
                self.connectorLower.send_w(self.temp_w[0]) # index
                self.temp_w[0],self.temp_b[0] = self.connectorLower.receive_W()
                self.connectorUpper.send_W(self.temp_w[0],self.temp_b[0])
        elif self.bit[channelA]: # if current CPE terminates the list
            # deleteAtIndex v ^   
            #               w b
            #               - -
            #               - -
            _ = self.connectorUpper.receive_w() # index
            self.connectorUpper.send_W(Any,True) # badIndex


    # === LOADERS AND UNLOADERS ===========================================

    def loadWords(self, channelA):
        """Puts multiple words into the channel
           with the first item at the top.
           Each item is handled in Theta(1)xO(n), propagation: ."""
        # Domino:
        # loadWords(A)         v-
        #                      W-
        #                      -W
        # clear(A) (addLast(A) -v)*
        self.word[channelA], self.bit[channelA] = \
                             self.connectorUpper.receive_W()
        if not self.bit[channelA]:
            self.extend()
            self.connectorLower.send_o("clear", channelA)
            self.temp_w[0], self.temp_b[0] = self.connectorUpper.receive_W()
            while not self.temp_b[0]:
                self.connectorLower.send_o("addLast", channelA)
                self.connectorLower.send_w(self.temp_w[0])
                self.temp_w[0], self.temp_b[0] = self.connectorUpper.receive_W()

    def loadWordsReverse(self, channelA):
        """Puts multiple words into the channel
           with the first item at the bottom.
           Each item is handled in Theta(1)xO(n), propagation: ."""
        # Domino:
        # loadWords(A) v+ 
        #              W
        #              -
        # none         - 
        self.word[channelA], self.bit[channelA] = \
                             self.connectorUpper.receive_W()
        if not self.bit[channelA]:
            self.extend()
            self.connectorLower.send_o("clear", channelA)
            self.temp_w[0] = self.word[channelA]
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorUpper.receive_W()
            while not self.bit[channelA]:
                self.connectorLower.send_o("push", channelA)
                self.connectorLower.send_w(self.temp_w[0])
                self.temp_w[0] = self.word[channelA]
                self.word[channelA], self.bit[channelA] = \
                                     self.connectorUpper.receive_W()
            self.word[channelA] = self.temp_w[0]
            self.bit[channelA] = False

    #----LOADERS, ordered -----------------------------------------------------

    def loadWordsND(self, channelA):
        # Domino:
        # loadWordsND(A)        v-
        #                       W-
        #                       -w
        # clear(A) (insertND(A) -v)*
        self.word[channelA], self.bit[channelA] = \
                             self.connectorUpper.receive_W()
        if not self.bit[channelA]:
            self.extend()
            self.connectorLower.send_o("clear", channelA)
            self.temp_w[0], self.temp_b[0] = \
                                 self.connectorUpper.receive_W()
            while not self.temp_b[0]:
                self.connectorLower.send_o("insertND", channelA)
                if self.temp_w[0] >= self.word[channelA]:
                    self.connectorLower.send_w(self.temp_w[0])
                elif self.temp_w[0] < self.word[channelA]:
                    self.connectorLower.send_w(self.word[channelA])
                    self.word[channelA] = self.temp_w[0]
                self.temp_w[0], self.temp_b[0] = \
                                 self.connectorUpper.receive_W()

    def loadWordsUniqueI(self, channelA):
        # Domino:
        # loadWordsI(A)        v-
        #                      W-
        #                      -w
        # clear(A) (insertI(A) -v)*
        self.word[channelA], self.bit[channelA] = \
                             self.connectorUpper.receive_W()
        if not self.bit[channelA]:
            self.extend()
            self.connectorLower.send_o("clear", channelA)
            self.temp_w[0], self.temp_b[0] = \
                                 self.connectorUpper.receive_W()
            while not self.temp_b[0]:
                if self.temp_w[0] > self.word[channelA]:
                    self.connectorLower.send_o("insertUniqueI", channelA)
                    self.connectorLower.send_w(self.temp_w[0])
                elif self.temp_w[0] < self.word[channelA]:
                    self.connectorLower.send_o("insertUniqueI", channelA)
                    self.connectorLower.send_w(self.word[channelA])
                    self.word[channelA] = self.temp_w[0]
                elif self.temp_w[0] == self.word[channelA]:
                    pass
                self.temp_w[0], self.temp_b[0] = \
                                 self.connectorUpper.receive_W()
    # --- UNLOADERS ----------------------------------------------------

    def unloadAllWords(self, channelA):
        """Removes and sends up all words from the channel, leaving it empty.
           with the top item handled first.
           Each item is handled in Theta(1)xO(n), propagation: ."""
        # Domino:
        # unloadAllWords(A)  ^- 
        #                    W-
        #                    -W
        #           (pull(A) -^)+
        while True:
            self.connectorUpper.send_W(self.word[channelA], self.bit[channelA])
            if self.bit[channelA]:
                break
            self.connectorLower.send_o("pull", channelA)
            self.word[channelA], self.bit[channelA] = \
                                 self.connectorLower.receive_W()

    # --- unloadWordsReverse helpers -----------------------------------

    def moveLast(self, channelA, aux1):
        """ """
        if not self.bit[channelA]:
            # Domino:
            # moveLast(A,X) ^-
            #               b-
            #               -b
            # moveLast(A,X) -^
            self.connectorUpper.send_b(False)
            self.connectorLower.send_o("moveLast", channelA, aux1)
            self.bit[aux1] = not self.connectorLower.receive_b()
            if not self.bit[aux1]:
                self.word[aux1] = self.word[channelA]
                self.bit[channelA] = True
        elif self.bit[channelA]:
            # Domino:
            # moveLast(A,X) ^
            #               b
            #               -
            # none          -
            self.connectorUpper.send_b(True)
            self.bit[aux1] = True 

    def pullEnd(self, channelA, aux1):
        """ """
        if not self.bit[channelA] and self.bit[aux1]:
            # Domino:
            # pullEnd(A,X) ^-
            #              W-
            #              -W
            # pullEnd(A,X) -^
            self.connectorUpper.send_W(self.word[aux1], self.bit[aux1])
            self.connectorLower.send_o("pullEnd", channelA, aux1)
            self.word[aux1], self.bit[aux1] = self.connectorLower.receive_W()
        elif not self.bit[channelA] and not self.bit[aux1]:
            # Domino:
            # pullEnd(A,X) ^-
            #              W-
            #              -W
            # pullEnd(A,X) -^
            self.connectorUpper.send_W(self.word[aux1], self.bit[aux1])
            self.connectorLower.send_o("pullEnd", channelA, aux1)
            self.word[aux1], self.bit[aux1] = self.connectorLower.receive_W()
            if self.bit[aux1]:
                self.word[aux1] = self.word[channelA]
                self.bit[aux1] = False
                self.bit[channelA] = True
        elif self.bit[channelA] and not self.bit[aux1]:
            # Domino:
            # pullEnd(A,X) ^
            #              W
            #              -
            # none         -
            self.connectorUpper.send_W(self.word[aux1], self.bit[aux1])
            self.bit[aux1] = True
        elif self.bit[channelA] and self.bit[aux1]:
            # Domino:
            # pullEnd(A,X) ^
            #              W
            #              -
            # none         -
            self.connectorUpper.send_W(Any, True)

    unloadWordsReverseNext = pullEnd

    def unloadWordsReverseBegin(self, channelA, aux1):
        """If channelA is empty, send up an empty word.
            Otherwise, pulls up channelA from the end through aux1
            and sends up the last channelA item."""
        if self.bit[channelA]: # if top CPE is empty
            # Domino:
            # unloadWordsReverseBegin(A,X) ^
            #                              W
            #                              -
            # none                         -
            self.connectorUpper.send_W(Any, True)
        elif not self.bit[channelA]: # if top CPE is not empty
            # Domino:
            # unloadWordsReverseBegin(A,X) -               -   ^
            #                              -               -   W
            #                              b               W   -
            #                moveLast(A,X) ^ (pullEnd(A,X) ^)* -
            self.connectorLower.send_o("moveLast", channelA, aux1)
            empty = self.connectorLower.receive_b()
            if empty: # if channelA below is empty:
                self.connectorUpper.send_W(self.word[channelA], False)
                self.bit[channelA] = True
            else:
                while True:
                    self.connectorLower.send_o("pullEnd", channelA, aux1)
                    self.word[aux1], self.bit[aux1] = \
                                     self.connectorLower.receive_W()
                    if not self.bit[aux1]:
                        break
                self.connectorUpper.send_W(self.word[aux1], False)
                self.connectorLower.send_o("pullEnd", channelA, aux1)
                self.word[aux1], self.bit[aux1] = \
                                 self.connectorLower.receive_W()
                if self.bit[aux1]:
                    self.word[aux1] = self.word[channelA]
                    self.bit[aux1] = False
                    self.bit[channelA] = True

    def unloadAllWordsReverse(self, channelA, aux1):
        """ """
        if self.bit[channelA]: # if top CPE is empty
            # Domino:
            # unloadAllWordsReverse(A,X) ^
            #                            W
            #                            -
            # none                       -
            self.connectorUpper.send_W(Any, True)
        elif not self.bit[channelA]: # if top CPE is not empty
        # Domino:
        # unloadAllWordsReverse(A,X) -               -                 -^   ^
        #                            -               -                 -W   W
        #                            b               W                 W-   -
        #              moveLast(A,X) ^ (pullEnd(A,X) ^)* (pullEnd(A,X) ^-)* -
            self.connectorLower.send_o("moveLast", channelA, aux1)
            empty = self.connectorLower.receive_b()
            if empty: # if channelA below is empty:
                self.connectorUpper.send_W(self.word[channelA], False)
                self.connectorUpper.send_W(Any, True)
            else: # if channelA below is not empty:
                valueObtined = False # Received a non-empty word? False.
                while True:
                    self.connectorLower.send_o("pullEnd", channelA, aux1)
                    self.word[aux1], self.bit[aux1] = \
                                     self.connectorLower.receive_W()
                    if not self.bit[aux1]: # if not empty
                        valueObtined = True
                        self.connectorUpper.send_W(self.word[aux1],
                                                   self.bit[aux1])
                    if valueObtined and self.bit[aux1]:
                        break
                self.connectorUpper.send_W(self.word[channelA], False)
                self.connectorUpper.send_W(Any, True)

    #### ARITHMETIC ########################################################

    def loadFirstWord(self, channelA):
        """Theta(1)xTheta(1), non-propagating."""
        # Domino:
        # loadFirstWord(A) v
        #                  w
        #                  -
        # none             -
        self.word[channelA] = self.connectorUpper.receive_w()
        self.bit[channelA] = False # continuation bit

    def loadNextWord(self, channelA):
        """Theta(1)xTheta(n), propagation |."""
        if self.bit[channelA]: # continuation bit
            # Domino:
            # loadNextWord(A) v-
            #                 w-
            #                 -w
            # loadNextWord(A) -v  
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.connectorLower.send_o("loadNextWord", channelA)
            self.connectorLower.send_w(self.temp_w[0])
        elif not self.bit[channelA]: # continuation bit
            # Domino:
            # loadNextWord(A)  v-
            #                  w-
            #                  -w
            # loadFirstWord(A) -v  
            self.temp_w[0] = self.connectorUpper.receive_w()
            self.bit[channelA] = True # continuation bit
            self.extend()
            self.connectorLower.send_o("loadFirstWord", channelA)
            self.connectorLower.send_w(self.temp_w[0])

    def equal(self, channelA, channelB):
        """O(n)xO(n), propagation |/."""
        if self.bit[channelA] and self.bit[channelB]:
            if self.word[channelA] != self.word[channelB]:
                # Domino:
                # equal(A,B) ^
                #            b
                #            -
                # equal(A,B) -
                self.connectorUpper.send_b(False)
            elif self.word[channelA] == self.word[channelB]:
                # Domino:
                # equal(A,B) -^
                #            -b
                #            b-
                # equal(A,B) ^-
                self.connectorLower.send_o("equal", channelA, channelB)
                self.temp_b[0] = self.connectorLower.receive_b()
                self.connectorUpper.send_b(self.temp_b[0])
        elif self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # equal(A,B) ^
            #            b
            #            -
            # equal(A,B) -
            self.connectorUpper.send_b(False)
        elif not self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # equal(A,B) ^
            #            b
            #            -
            # equal(A,B) -
            self.connectorUpper.send_b(False)
        elif not self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # equal(A,B) ^
            #            b
            #            -
            # equal(A,B) -
            if self.word[channelA] != self.word[channelB]:
                self.connectorUpper.send_b(False)
            elif self.word[channelA] == self.word[channelB]:
                self.connectorUpper.send_b(True)

    def le(self, channelA, channelB):
        """O(n)xO(n), propagation |/."""
        if self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # le(A,B) -^
            #         -B
            #         B-
            # le(A,B) ^-
            self.connectorLower.send_o("le", channelA, channelB)
            self.temp_b[0], self.temp_b[1] = self.connectorLower.receive_B()
            if self.temp_b[1]: # if sure
                self.connectorUpper.send_B(self.temp_b[0], True) # that, sure
            else: # if not sure
                if self.word[channelA] < self.word[channelB]:
                    self.connectorUpper.send_B(True, True) # true, sure
                elif self.word[channelA] > self.word[channelB]:
                    self.connectorUpper.send_B(False, True) # false, sure
                elif self.word[channelA] == self.word[channelB]:
                    self.connectorUpper.send_B(True, False) # true, maybe
        elif self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # le(A,B) ^
            #         B
            #         -
            # none    -
            self.connectorUpper.send_B(False, True) # true, sure
        elif not self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # le(A,B) ^
            #         B
            #         -
            # none    -
            self.connectorUpper.send_B(True, True) # true, sure
        elif not self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # le(A,B) ^
            #         B
            #         -
            # none    -
            if self.word[channelA] < self.word[channelB]:
                self.connectorUpper.send_B(True, True) # true, sure
            elif self.word[channelA] > self.word[channelB]:
                self.connectorUpper.send_B(False, True) # false, sure
            elif self.word[channelA] == self.word[channelB]:
                self.connectorUpper.send_B(True, False) # true, maybe

    def less(self, channelA, channelB):
        """O(n)xO(n), propagation |/."""
        if self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # less(A,B) -^
            #           -B
            #           B-
            # less(A,B) ^-
            self.connectorLower.send_o("less", channelA, channelB)
            self.temp_b[0], self.temp_b[1] = self.connectorLower.receive_B()
            if self.temp_b[1]: # if sure
                self.connectorUpper.send_B(self.temp_b[0], True) # that, sure 
            else: # if not sure
                if self.word[channelA] < self.word[channelB]:
                    self.connectorUpper.send_B(True, True) # true, sure
                elif self.word[channelA] > self.word[channelB]:
                    self.connectorUpper.send_B(False, True) # false, sure
                elif self.word[channelA] == self.word[channelB]:
                    self.connectorUpper.send_B(False, False) # false, maybe
        elif self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # less(A,B) ^
            #           B
            #           -
            # none      -
            self.connectorUpper.send_B(False, True) # true, sure
        elif not self.bit[channelA] and self.bit[channelB]:
            # Domino:
            # less(A,B) ^
            #           B
            #           -
            # none      -
            self.connectorUpper.send_B(True, True) # true, sure
        elif not self.bit[channelA] and not self.bit[channelB]:
            # Domino:
            # less(A,B) ^
            #           B
            #           -
            # none      -
            if self.word[channelA] < self.word[channelB]:
                self.connectorUpper.send_B(True, True) # true, sure
            elif self.word[channelA] > self.word[channelB]:
                self.connectorUpper.send_B(False, True) # false, sure
            elif self.word[channelA] == self.word[channelB]:
                self.connectorUpper.send_B(False, False) # false, maybe

    def copyInt(self, channelA, resultChannel):
        """ """
        if self.bit[channelA]: # if continued
            # Domino:
            # copyInt(A,R) 
            #           
            #           
            # copyInt(A,R)
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("copyInt", channelA, resultChannel)
        elif not self.bit[channelA]: # if last word
            # Domino:
            # copyInt(A,R) 
            #           
            #           
            # none
            self.word[resultChannel] = self.word[channelA]
            self.bit[resultChannel] = False

    def conj(self, channelA, channelB, resultChannel):
        """Theta(n)xTheta(n) where n is the length of the shorter integer."""
        # todo: this code can produce 0-words at the end, remove them!
        # Domino:
        # conj(A,B,R) 
        #           
        #           
        # conj(A,B,R) 
        if self.bit[channelA] and self.bit[channelB]: # if continued
            self.word[resultChannel] = self.word[channelA] & self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("conj", channelA, channelB,
                                       resultChannel)
        elif self.bit[channelA] and not self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] & self.word[channelB]
            self.bit[resultChannel] = False
        elif not self.bit[channelA] and self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] & self.word[channelB]
            self.bit[resultChannel] = False
        elif not self.bit[channelA] and not self.bit[channelB]: # if last words
            self.word[resultChannel] = self.word[channelA] & self.word[channelB]
            self.bit[resultChannel] = False

    def disj(self, channelA, channelB, resultChannel):
        """Theta(1)xTheta(n) where n is the length of the longer integer."""
        # Domino:
        # disj(A,B,R) 
        #           
        #           
        # disj(A,B,R)
        if self.bit[channelA] and self.bit[channelB]: # if continued
            self.word[resultChannel] = self.word[channelA] | self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("disj", channelA, channelB,
                                       resultChannel)
        elif self.bit[channelA] and not self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] | self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("copyInt", channelA, resultChannel)
        elif not self.bit[channelA] and self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] | self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("copyInt", channelB, resultChannel)
        elif not self.bit[channelA] and not self.bit[channelB]: # if last words
            self.word[resultChannel] = self.word[channelA] | self.word[channelB]
            self.bit[resultChannel] = False

    def exdisj(self, channelA, channelB, resultChannel):
        """Theta(1)xTheta(n) where n is the length of the longer integer."""
        # Domino:
        # disj(A,B,R) 
        #           
        #           
        # disj(A,B,R)
        if self.bit[channelA] and self.bit[channelB]: # if continued
            self.word[resultChannel] = self.word[channelA] ^ self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("disj", channelA, channelB,
                                       resultChannel)
        elif self.bit[channelA] and not self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] ^ self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("copyInt", channelA, resultChannel)
        elif not self.bit[channelA] and self.bit[channelB]:
            self.word[resultChannel] = self.word[channelA] ^ self.word[channelB]
            self.bit[resultChannel] = True
            self.connectorLower.send_o("copyInt", channelB, resultChannel)
        elif not self.bit[channelA] and not self.bit[channelB]: # if last words
            self.word[resultChannel] = self.word[channelA] ^ self.word[channelB]
            self.bit[resultChannel] = False

