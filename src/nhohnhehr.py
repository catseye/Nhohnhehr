#!/usr/bin/env python

# ### Nhohnhehr interpreter ###

# Written by Marinus.  The contents of this file are in the public domain.
# Adapted from this esowiki page on May 10 2011:
#   http://www.esolangs.org/wiki/User:Marinus/Nhohnhehr_interpreter
# Adapted to run under Python 3, and to conform to PEP8 style,
#   by Chris Pressey, summer 2021.

# usage: nhohnhehr.py bits filename    (binary I/O)
#        nhohnhehr.py [bytes] filename (ASCII I/O)

import sys


def addvec(v1, v2):
    (x1, y1) = v1
    (x2, y2) = v2
    return (x1 + x2, y1 + y2)


def mulvec(v, m):
    (x, y) = v
    return (x * m, y * m)


# room
class Room(object):
    data = None
    size = 0

    def __getitem__(self, v):
        (x, y) = v
        if x >= 0 and y >= 0 and x < self.size and y < self.size:
            return self.data[y][x]
        else:
            raise IndexError("value out of range")

    def __str__(self):
        return "\n".join(''.join(str(item) for item in line) for line in self.data)

    # transformations
    NONE, CW, CCW, ROT = range(4)

    def transform(self, transformation):
        if transformation == Room.NONE:
            return
        elif transformation == Room.ROT:
            # rotate 180 degrees: flip lines, and reverse each line
            self.data.reverse()
            for line in self.data:
                line.reverse()
        elif transformation == Room.CCW:
            # clockwise 90 degrees
            data = self.data
            self.data = [[0] * self.size for x in range(self.size)]
            for y in range(self.size):
                for x in range(self.size):
                    self.data[self.size - x - 1][y] = data[y][x]
        elif transformation == Room.CW:
            # counterclockwise 90 degrees
            data = self.data
            self.data = [[0] * self.size for x in range(self.size)]
            for y in range(self.size):
                for x in range(self.size):
                    self.data[y][x] = data[self.size - x - 1][y]
        else:
            raise ValueError("invalid transformation (%d)" % transformation)

    # init room from file or from room+transformation
    def __init__(self, file=None, room=None, transform=None):
        if (file and room) or (not (file or room)):
            raise TypeError("Room needs to be initialized with either a file or a room.")

        # init from file
        if file:
            self.data = []

            # read file
            lines = file.readlines()

            # find possible top-left coordinates for the box
            possibleStartCoords = []
            for y in range(len(lines)):
                for x in range(len(lines[y])):
                    if lines[y][x] == '+':
                        try:
                            if lines[y][x + 1] == '-' and lines[y + 1][x] == '|':
                                possibleStartCoords.append((x, y))
                        except IndexError:
                            # we hit a boundary looking for | or -, so this
                            # isn't a valid one.
                            pass

            # check if a box can be found
            startCoords = None
            roomSize = 0
            for (x, y) in possibleStartCoords:

                line = lines[y]
                # find next '+'
                x2 = x + 1
                while x2 < len(line) and line[x2] != '+':
                    x2 += 1

                if x2 == len(line):
                    # no '+' here.
                    continue

                # found
                size = x2 - x
                ok = False
                # see if it's square
                try:
                    # check horizontal lines
                    if lines[y + size][x:x + size + 1] == '+' + '-' * (size - 1) + '+':
                        ok = True
                        # check vertical lines
                        for y2 in range(y + 1, y + size):
                            ok = ok and (lines[y2][x] + lines[y2][x + size] == '||')
                            if not ok:
                                break

                except IndexError:
                    # we went outside of the file, so this one isn't valid
                    ok = False

                if not ok:
                    # try next pair
                    continue
                else:
                    # found one!
                    if startCoords:
                        # but we already had one...
                        raise ValueError("Multiple valid rooms in one file, first room"
                                         " found at: (%d,%d); second one at: (%d,%d)."
                                         % (startCoords[0], startCoords[1], x, y))
                    else:
                        # + 1 because that's the start of the data, we don't need the boundary
                        startCoords = (x + 1, y + 1)
                        roomSize = size - 1
                        # and we have to continue looking in case we find another one,
                        # in which case the file is invalid.

            # no room in the file
            if not startCoords:
                raise ValueError("Cannot find a valid room in this file.")

            # we have a room, load it
            x, y = startCoords
            for lineno in range(roomSize):
                self.data.append([m for m in lines[lineno + y][x:roomSize + x]])

            self.size = roomSize

        # init from other room
        elif room:
            # this one's easier
            self.size = room.size
            self.data = [line[:] for line in room.data]

        # transformation needed?
        if transform:
            self.transform(transform)


class Environment(object):
    rooms = {}
    ip = ()
    direction = ()
    edgemode = None
    roomsize = 0
    halt = False

    # states
    WRAP, COPY, CW, CCW, ROT = range(5)

    # directions
    LEFT, RIGHT, UP, DOWN = (-1, 0), (1, 0), (0, -1), (0, 1)

    def __getitem__(self, v):
        # get whatever's in that room at that space
        (x, y) = v
        room = self.rooms[self.roomCoords((x, y))]
        roomX = x % self.roomsize
        roomY = y % self.roomsize
        return room[roomX, roomY]

    def __init__(self, room, io_system):
        self.rooms = {
            (0, 0): room
        }
        self.roomsize = room.size
        self.dir = Environment.RIGHT
        self.edgemode = Environment.WRAP
        self.io_system = io_system
        self.halt = False
        # find initial instruction pointer

        self.ip = (-1, -1)
        for x in range(self.roomsize):
            for y in range(self.roomsize):
                if room[x, y] == '$':
                    self.ip = (x, y)
                    break

        if self.ip == (-1, -1):
            raise ValueError("no $ in room")

    def infunc(self):
        return self.io_system.units_in()

    def outfunc(self, unit):
        return self.io_system.units_out(unit)

    def roomCoords(self, v):
        (x, y) = v
        return (int(x / self.roomsize), int(y / self.roomsize))

    def advanceIP(self):
        newIP = addvec(self.ip, self.dir)

        if self.roomCoords(self.ip) != self.roomCoords(newIP):
            if self.edgemode == Environment.WRAP:
                # wrap to edge of last room
                newIP = addvec(newIP, mulvec(self.dir, -self.roomsize))
            else:
                # make a new room if none exists yet
                if not self.roomCoords(newIP) in self.rooms:
                    # transformations
                    transform = {
                        Environment.COPY: Room.NONE,
                        Environment.CW: Room.CW,
                        Environment.CCW: Room.CCW,
                        Environment.ROT: Room.ROT
                    }[self.edgemode]
                    self.rooms.update({
                        self.roomCoords(newIP): Room(
                            room=self.rooms[self.roomCoords(self.ip)],
                            transform=transform
                        )
                    })
        self.ip = newIP

    def step(self):
        command = self[self.ip]
        ccwrot = {
            self.LEFT: self.DOWN,
            self.RIGHT: self.UP,
            self.UP: self.RIGHT,
            self.DOWN: self.LEFT
        }
        cwrot = {
            self.LEFT: self.UP,
            self.RIGHT: self.DOWN,
            self.UP: self.LEFT,
            self.DOWN: self.RIGHT
        }

        if command == '/':
            self.dir = ccwrot[self.dir]
        elif command == '\\':
            self.dir = cwrot[self.dir]
        elif command in '=&{}!':
            self.edgemode = {
                '=': self.WRAP,
                '&': self.COPY,
                '{': self.CCW,
                '}': self.CW,
                '!': self.ROT
            }[command]
        elif command == '#':
            self.advanceIP()
        elif command == '?':
            try:
                self.dir = (self.infunc() and cwrot or ccwrot)[self.dir]
            except IOError:
                # no more input available = do nothing
                pass
        elif command in '01':
            self.outfunc(int(command))
        elif command == '@':
            self.halt = True

        self.advanceIP()

    def run(self):
        while not self.halt:
            self.step()


class NhohnhehrIO(object):
    def units_in(self):
        raise NotImplementedError('implement units_in please')

    def units_out(self, unit):
        raise NotImplementedError('implement units_out please')


class BitsIO(NhohnhehrIO):
    def units_in(self):
        i = None
        while i not in ('0', '1'):
            i = sys.stdin.read(1)
            if i == '':
                raise IOError()  # eof
        return int(i)

    def units_out(self, bit):
        sys.stdout.write(('0', '1')[bit])
        sys.stdout.flush()


class BytesIO(NhohnhehrIO):
    def units_in(self, bits=[[]]):
        # get data if necessary
        if bits[0] == []:
            i = sys.stdin.read(1)
            if (i == ''):
                raise IOError()  # eof
            else:
                bits[0] = [int(bool(ord(i) & (1 << b))) for b in range(7, -1, -1)]

        # return data
        bit = bits[0][0]
        bits[0] = bits[0][1:]
        return bit

    def units_out(self, bit, bits=[[]]):
        bits[0].append(bit)

        # if we have 8 bits, output
        if len(bits[0]) == 8:
            sys.stdout.write(chr(sum(bits[0][7 - b] << b for b in range(7, -1, -1))))
            sys.stdout.flush()
            bits[0] = []


def main(argv):
    if len(argv) not in (2, 3) or (len(argv) == 3 and not argv[1] in ('bits', 'bytes')):
        print("""\
Usage: [python] %s [bits|bytes] filename
   bits/bytes: specify i/o mode

   In bits mode, i/o uses the characters '0' and '1'
     (and when reading input, everything that's not '0'
      or 1 is ignored).
   In bytes mode, i/o is done 8 bits at a time as ASCII.

   If no mode is given, bytes mode is used.
""" % argv[0])
        sys.exit()

    if len(argv) == 2:
        mode = 'bytes'
        fname = argv[1]
    else:
        mode = argv[1]
        fname = argv[2]

    io_system = {
        'bits': BitsIO(),
        'bytes': BytesIO(),
    }[mode]
    try:
        with open(fname, 'r') as f:
            Environment(Room(file=f), io_system).run()
        if mode == 'bits':
            print  # newline

    except Exception as e:
        print("Error: {}".format(e))


if __name__ == '__main__':
    main(sys.argv)
