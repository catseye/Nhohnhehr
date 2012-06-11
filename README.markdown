The Nhohnhehr Programming Language
==================================

Nhohnhehr is a remotely fungeoid esoteric programming language designed
by Chris Pressey between December 4 and December 8, 2010.

Overview
--------

A Nhohnhehr program consists of a single object called a *room*, which
is a 2-dimensional, square grid of cells of finite, and usually small,
extent. To emphasize its bounds, the single room in a Nhohnhehr program
text must be delimited with an ASCII box, in the manner of the
following:

    +----+
    |    |
    |    |
    |    |
    |    |
    +----+

Arbitrary text, including comments, may occur outside this bounding box;
it will not be considered part of the Nhohnhehr program.

Once defined, the contents of a room are immutable. Although only a
single room may appear in a program text, new rooms may be created
dynamically at runtime and adjoined to the edges of existing rooms (see
below for details on how this works.)

Execution of Instructions
-------------------------

In a running Nhohnhehr program there is an instruction pointer. At any
given time it has a definite position inside one of the rooms of the
program, and is traveling in one of the four cardinal directions. It is
also associated with a five-state variable called the *edge mode*. As
the instruction pointer passes over non-blank cells, it executes them,
heeding the following meanings:

     / causes the pointer to travel north if it was traveling east,
       south if travelling west.
     \ causes the pointer to travel north if it was traveling west,
       south if travelling east.
     = sets wrap edge mode.
     & sets copy-room-verbatim edge mode.
     } sets copy-room-rotate-cw-90 edge mode.
     { sets copy-room-rotate-ccw-90 edge mode.
     ! sets copy-room-rotate-180 edge mode.
     # causes the instruction pointer to skip over the next cell
       (like # in Befunge-93.)
     ? inputs a bit.  If it is 0, rotate direction of travel 90 degrees
       counterclockwise; if it is 1, rotate direction of travel 90 degress
       clockwise; if no more input is available, the direction of travel
       does not change.
     0 outputs a 0 bit.
     1 outputs a 1 bit.
     @ halts the program.
     $ only indicates where initial instruction pointer is located;
       otherwise it has no effect.  The initial direction of travel is east.

Blank cells are NOPs.

Edge Crossing
-------------

If the instruction pointer reaches an edge of the room and tries to
cross it, what happens depends on the current edge mode:

-   In wrap edge mode (this is the initial edge mode), the pointer wraps
    to the corresponding other edge of the room, as if the room were
    mapped onto a torus.
-   In all other modes, if there already exists a room adjoining the
    current room on that edge, the instruction pointer leaves the
    current room and enters the adjoining room in the corresponding
    position. However, if no such adjoining room exists yet, one will be
    created by making a copy of the current room, transforming it
    somehow, and adjoining it. The instruction pointer then enters the
    new room, just as if it had already existed. The details of the
    transformation depend on the edge mode:
    -   In copy-room-verbatim edge mode, no translation is done.
    -   In copy-room-rotate-cw-90 edge mode, the copy of the current
        room is rotated clockwise 90 degrees before being adjoined.
    -   In copy-room-rotate-ccw-90 edge mode, the copy of the current
        room is rotated counterclockwise 90 degrees before being
        adjoined.
    -   In copy-room-rotate-180 edge mode, the copy of the current room
        is rotated 180 degrees before being adjoined.

Examples
--------

The following example reads in a sequence of bits and creates a series
of rooms, where 1 bits correspond to unrotated rooms and 0 bits
correspond to rooms rotated 90 degrees clockwise (though not precisely
one-to-one).

    +------+
    |    /}|
    |&#/$?@|
    |  / \&|
    |      |
    | {    |
    |\\    |
    +------+

After reading a 0 bit and leaving the right edge, the room is copied,
rotated 90 degrees clockwise, and adjoined, so that the rooms of the
program are:

    +------+------+
    |    /}|\   & |
    |&#/$?@|\{  # |
    |  / \&|   // |
    |      |    $ |
    | {    |   \?/|
    |\\    |   &@}|
    +------+------+

After leaving the right edge again, the current room is copied, this
time rotated 90 degrees counterclockwise, and adjoined, and we get:

    +------+------+------+
    |    /}|\   & |    /}|
    |&#/$?@|\{  # |&#/$?@|
    |  / \&|   // |  / \&|
    |      |    $ |      |
    | {    |   \?/| {    |
    |\\    |   &@}|\\    |
    +------+------+------+

Say we were to now read in a 1 bit; we would thus have:

    +------+------+------+------+
    |    /}|\   & |    /}|    /}|
    |&#/$?@|\{  # |&#/$?@|&#/$?@|
    |  / \&|   // |  / \&|  / \&|
    |      |    $ |      |      |
    | {    |   \?/| {    | {    |
    |\\    |   &@}|\\    |\\    |
    +------+------+------+------+

It should be fairly clear at this point that this program will read all
input bits, creating rooms thusly, terminating when there are no more
input bits.

The following program is a variation of the above which, when it
encounters the end of input, writes out the bits in the reverse order
they were read in, with the following changes:

* for every `1` in the input, a `1` comes out
* for every `0` in the input, `10` comes out
* there's an extra `1` at the end of the output

    +------------+
    |    /}      |
    |&#/$?   \   |
    |  / \&      |
    |            |
    |            |
    |         0  |
    |         !  |
    |            |
    |            |
    |    {1  /#  |
    | {          |
    |\\@         |
    +------------+

Computational Class
-------------------

The last example in the previous section was written to demonstrate that
Nhohnhehr is at least as powerful as a push-down automaton.

The author suspects Nhohnhehr to be more powerful still; at least a
linear bounded automaton, but possibly even Turing-complete. A strategy
for simulating a Turing machine could be developed from the above
examples: create new rooms to represent new tape cells, with each
possible orientation of the room representing a different tape symbol.
The finite control is encoded and embedded in the possible pathways that
the instruction pointer can traverse inside each room. Because rooms
cannot be changed once created, one might have to resort to creative
measures to "change" a tape cell; for instance, each tape cell might
have a "stack" of rooms, with a new room appended to the stack each time
the cell is to be "changed".

Source
------

This document was adapted from [the esolangs.org wiki page for
Nhohnhehr](http://www.esolangs.org/wiki/Nhohnhehr), which, like all
esowiki articles, has been placed under public domain dedication.

Implementation
--------------

The Nhohnhehr distribution contains a Nhohnhehr interpreter, written
in Python, based on [this implementation of
Nhohnhehr](http://esolangs.org/wiki/User:Marinus/Nhohnhehr_interpreter)
by [Marinus](http://www.esolangs.org/wiki/User:Marinus).  It
is effectively the reference interpreter, since it seems to correctly
implement the language described here, and there are, to the best of
my knowledge, no other implementations of Nhohnhehr in existence.
Like all content from the esowiki, it too is in the public domain.
