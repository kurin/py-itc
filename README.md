py-itc
======

An interval tree clock implementation in Python.

Interval Tree Clocks
--------------------

An interval tree clock is like a vector clock, only more annoying.

The "problem" with vector clocks is that you can't add and remove
nodes arbitrarily.  At some point you need to do some garbage
collection, or your vector will just keep growing.

To fix this, some grad students from like I think Portugal came up
with a way, way more complicated data structure that you can use
instead.  The way you use it is with the _fork-event-join_ model.

Fork-Event-Join
---------------

So say you're passing messages in a distributed system between A
and B, and then C joins the system.  C will talk to either A or B
and say "hi, I'm new here," at which point A or B will _fork_ their
clock, splitting it into two clocks.  It will keep one and send the
other to C.  At some point one of the three systems will register
an event, and record the _event_ on their clock, knocking it into
the future.  At this point (say the node is B), A and C's clocks will
be less than B's clock (although the only comparison available, for
some reason, is less-than-or-equal-to).

So now B communicates with A and says "hey look this changed," and
B also sends its clock.  A compares clocks and agrees that B's clock
is strictly in A's future.  A then _joins_ its clock with B's clock,
_forks_ another pair of clocks and gives one back to B.

Now A and B flip a coin to see who has to tell C.  No matter who
loses, C's clock is strictly in the past of each of them.  They
share data, C _joins_ and _forks_ some new clocks, and now all
clocks are relatively equal, meaning for any pair x, y where x and
y can be A, B, or C, `x <= y == True` and `y <= x == True`.

In Code
-------

How does this work in code?  Well, the first node on the scene
initiates the `Stamp()` class:

```python
import itc

clock = itc.Stamp()               # A creates the initial stamp
```

When another node joins, it forks and sends one copy to the new node:

```python
clock, remote = clock.fork()      # A forks the clock, creating two cotemporal copies
bits = remote.encode()            # encodes the one it's not keeping
TCPWizardSendingObject(B, bits)   # sends it to the other side
```

While the remote node loads the other end:

```python
bits = TCPRecvFromEther()         # B receive the clock from the first node
clock = itc.Stamp.load(bits)      # and turns it into a python object
```

Time passes...

```python
stuff = Stuff.wait_around()       # A or B, call it B, waits here for something to happen
Stuff.handle_stuff(stuff)         # and reacts to it, presumably changing internal state
clock.event()                     # notes that an event happened
state = Stuff.get_new_state()     # gets some kind of representation of that new state
TCPWizSendObj(o, clock, state)    # and sends the new clock to some other node
```

And the other node handles it:

```python
bits, state = TCPRecvFrEth()      # A pulls down the state and the clock object
othclk = itc.Stamp.load(bits)
if clock <= othclk:               # THIS node is strictly in the past of the node we just got the data from
    Stuff.update(state)           # this presumably means we can update our state to match the other node's state
                                  # without difficulty

clock = clock + othclk            # join the two clocks
clock, othclk = clock.fork()      # and then fork it
TCPWizSendObj(o, clock)           # and send it back
```

Finally, it's important for B to replace its clock with the new
clock, although you can skip this clock if the ID parts of the clock
are the same.
```python
bits = TCPRecvFrEth()             # get the clock
o = itc.Stamp.load(bits)          # load it
if clock <= o and o <= clock:     # they are cotemporal
    clock = o                     # replace it
```

This last step is necessary because of reasons.

What's Really Happening (Kinda)
-------------------------------

So an interval tree clock is two parts, the interval tree and the
clock.  Duh.

The interval tree can conceptually represent the real line between
0 and 1, or `(0, 1)`.  When a clock is forked, this line is split
into `(0, .5)` and `(.5, 1)`.  When those lines are forked they are
themselves split, and so on.  This is also known as the ID.

This way, all IDs are guaranteed to be unique.

When an event is registered, the clock is incremented.  The clock
can also thought of as taking place in the space above the interval
`(0, 1)`.  When it is incremented, the space above the line "owned"
by the clock, represented by the value of the ID, is increased.
For example, if my ID is `(0, .25)`, then I own the airspace above
that interval and can increase it.

If this all sounds like bullshit, don't worry, I didn't get it
either.  Check out the awesome graphic at
https://github.com/ricardobcl/Interval-Tree-Clocks.  And maybe read
the rest of that, too.
