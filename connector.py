# TO DO:
# 1. Move extend from the CPE class to Connector class.
# 2. Detect deadlocks when both CPEs initiate send or both initiate receive.
# 3. Enforce word size.

from myThreading import EventPlus, Any

# WORD_SIZE = 2 # in bits; excludes the continuation bit.

#=================================

class Connector:
    """A two-way communication channel between two threads.
       Conceptually, connector objects correspond to two sets of wires conncecting
       asynchronous circuits, which carry data, request and acknowledge
       signals, in either direction.
       This implementation uses a 4-phase bundled data handshaking protocol
       driven by the sender.
       At our chosen level of abstraciton, we are simulating
       the up and down push channels between the circuts by a single Connector.

       All the send and receive methods are explicitely typed,
       to aid correct communication protocol design.
       Some incompatibilites between
       interacting protocols will raise Type errors.
       There is no raising exceptions in
       circuits we model, but it would be impossible to send a word over
       a single wire meant for a bit -- these kinds of potentital design
       errors are reported.

       The object Any is a legal value to be transmitted 
       by the send/receive methods. While coding communication protocols,
       when the transmitted value does not matter we send Any.
       The protocol code should be witten in a way which does not confuse
       such Any values with O or False; Indications of such confusions
       are be reported as TypeError to aid in correct protocol design.
       The circuts we model have only True/False values represented by voltage;
       when protocol coded in this program sends Any,
       an arbitrarily chosen value should be transmittd by the circuit. 
       """

    def __init__(self):
        self.operation = Any # str (except this initial value.)
        self.channels = Any # a tuple of non-negative integers, possibly empty
        self.word = Any # non-negative int or Any 
        self.bit = Any # True/False/Any
        self.bit2 = Any # True/False/Any
        self.reqEvent = EventPlus()
        self.ackEvent = EventPlus()
        self.status = "ready"

    # SEND ------------------------------------------------------

    def send_o(self, operation, *channels):
        """4-phase bundled data protocol;
           operation parameter should be a string.
           (The O in the name stands for "operation".)
           Takes as parameters a string and arbitrarily many integers;
           the integers are channel numbers for the operation."""
        if not isinstance(operation, str):
            raise TypeError("send_o%s: operation should be a string." %
                            str((operation,)+channels))
        for ch in channels:
            if not isinstance(ch, int):
                raise TypeError("send_o%s: every channel should be an int." %
                                str((operation,)+channels))
            # value checking is done in the CPE.run definition.
        self.ackEvent.waitForFalse()
        if self.status != "ready":
            raise RuntimeError("send_o%: Connector status %s, not ready." %
                               ((operation,)+channels, self.status))
        else:
            self.status = "o"
        self.operation = operation
        self.channels = channels            
        self.reqEvent.setTrue()      
        self.ackEvent.waitForTrue()  
        self.reqEvent.setFalse()

    def send_w(self, word):
        """4-phase bundled word protocol;
           word parameter should be a nonnegative int or Any.
           (The w in the name stands for "word".)"""
        if not isinstance(word, int) and word is not Any:
            raise TypeError("send_w(%s): word should be an int or Any." %
                            str(word))
        if word is not Any and word < 0:
            raise ValueError("send_w(%s): word cannot be negative." %
                             str(word))
        #if word is not Any and word >= 2**WORD_SIZE:
        #    raise ValueError("send_w(%s): word can have only %s bits." %
        #                     (str(word), WORD_SIZE))
        self.ackEvent.waitForFalse()
        if self.status != "ready":
            raise RuntimeError("send_w%s: Connector status %s, not ready." %
                               (word, self.status))
        else:
            self.status = "w" 
        self.word = word             
        self.reqEvent.setTrue()      
        self.ackEvent.waitForTrue()  
        self.reqEvent.setFalse()

    def send_W(self, word, bit):
        """4-phase bundled word protocol;
           word parameter should be a nonnegative int or Any,
           bit parameter should be a bool or Any.
           (The W in the name represents a word plus an additonal bit.)"""
        if not isinstance(word, int) and word is not Any:
            raise TypeError("send_W(%s, %s): word should be an int or Any." %
                            (word, bit)) 
        if not isinstance(bit, bool) and word is not Any:
            raise TypeError("send_W(%s, %s): bit should be a bool." %
                            (word, bit))
        if word is not Any and word < 0:
            raise ValueError("send_W(%s, %s): word cannot be negative." %
                             (word, bit))
        #if word is not Any and word >= 2**WORD_SIZE:
        #    raise ValueError("send_w(%s): word can have only %s bits." %
        #                     (str(word), WORD_SIZE))
        self.ackEvent.waitForFalse()
        if self.status != "ready":
            raise RuntimeError("send_W(%s, %s): Connector status %s, not ready." %
                               (word, bit,self.status))
        else:
            self.status = "W"
        self.word = word
        self.bit = bit      
        self.reqEvent.setTrue()      
        self.ackEvent.waitForTrue()  
        self.reqEvent.setFalse()

    def send_b(self, bit):
        """4-phase bundled word protocol;
           bit parameter should be a bool or Any.
           (The b in the name stands for "bit".)"""
        if not isinstance(bit, bool) and bit is not Any:
            raise TypeError("send_b(%s): bit should be a bool or Any." %
                            str(bit))
        self.ackEvent.waitForFalse()
        if self.status != "ready":
            raise RuntimeError("send_b(%s): Connector status %s, not ready." %
                               (bit, self.status))
        else:
            self.status = "b" 
        self.bit = bit             
        self.reqEvent.setTrue()      
        self.ackEvent.waitForTrue()  
        self.reqEvent.setFalse()

    def send_B(self, bit, bit2):
        """4-phase bundled word protocol;
           bit parameter should be a bool or Any,
           bit2 parameter should be a bool or Any.
           (The B represents a bit plus an additonal bit.)"""
        if not isinstance(bit, bool) and bit is not Any:
            raise TypeError("send_B(%s, %s): bit should be a bool or Any." %
                            (bit, bit2)) 
        if not isinstance(bit2, bool) and bit2 is not Any:
            raise TypeError("send_B(%s, %s): bit2 should be a bool or Any." %
                            (bit, bit2))
        self.ackEvent.waitForFalse()
        if self.status != "ready":
            raise RuntimeError(
                "send_B(%s, %s): Connector status %s, not ready." %
                               (bit, bit2, self.status))
        else:
            self.status = "B" 
        self.bit = bit
        self.bit2 = bit2      
        self.reqEvent.setTrue()      
        self.ackEvent.waitForTrue()  
        self.reqEvent.setFalse()

    # RECEIVE ------------------------------------------------
        
    def receive_o(self):
        """4-phase bundled word protocol;
           (The o in the name stands for an operation.)"""
        self.reqEvent.waitForTrue()
        if self.status != "o":
            raise TypeError("Connector mismatch: send %s, receive o." %
                            self.status)
        operation = self.operation
        channels = self.channels
        self.ackEvent.setTrue()      
        self.reqEvent.waitForFalse()
        self.status = "ready"
        self.ackEvent.setFalse()     
        return operation, channels

    def receive_w(self):
        """4-phase bundled word protocol.
           (The w in the name stands for a word.)"""
        self.reqEvent.waitForTrue()
        if self.status != "w":
            raise TypeError("Connector mismatch: sent %s, receive w." %
                            self.status)
        word = self.word
        self.ackEvent.setTrue()      
        self.reqEvent.waitForFalse()
        self.status = "ready"
        self.ackEvent.setFalse()     
        return word

    def receive_W(self):
        """4-phase bundled word protocol.
           (The W in the name stands for a word plus an additonal bit.)"""
        self.reqEvent.waitForTrue()
        if self.status != "W":
            raise TypeError("Connector mismatch: sent %s, receive W." %
                            self.status)
        word = self.word
        bit = self.bit
        self.ackEvent.setTrue()      
        self.reqEvent.waitForFalse()
        self.status = "ready"
        self.ackEvent.setFalse()     
        return word, bit

    def receive_b(self):
        """4-phase bundled word protocol.
           (The b in the name stands for a bit.)"""
        self.reqEvent.waitForTrue()
        if self.status != "b":
            raise TypeError("Connector mismatch: send %s, receive b." %
                            self.status)
        bit = self.bit
        self.ackEvent.setTrue()      
        self.reqEvent.waitForFalse()
        self.status = "ready"
        self.ackEvent.setFalse()     
        return bit

    def receive_B(self):
        """4-phase bundled word protocol.
           (The B in the name stands for a bit plus an additonal bit.)"""
        self.reqEvent.waitForTrue()
        if self.status != "B":
            raise TypeError("Connector mismatch: send %s, receive B." %
                            self.status)
        bit = self.bit
        bit2 = self.bit2
        self.ackEvent.setTrue()      
        self.reqEvent.waitForFalse()
        self.status = "ready"
        self.ackEvent.setFalse()     
        return bit, bit2

#==========================================================

