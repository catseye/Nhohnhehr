Test Suite for Nhohnhehr
========================

This test suite is written in [Falderal][] format.

[Falderal]: https://catseye.tc/node/Falderal

    -> Tests for functionality "Run Nhohnhehr program, outputting at most 80 bits"

"Reverse-esque" example.

    | +------------+
    | |    /}      |
    | |&#/$?   \   |
    | |  / \&      |
    | |            |
    | |            |
    | |         0  |
    | |         !  |
    | |            |
    | |            |
    | |    {1  /#  |
    | | {          |
    | |\\@         |
    | +------------+
    + 11111110000001
    = 110101010101011111111

"Read and store" example.

    | +------+
    | |    /}|
    | |&#/$?@|
    | |  / \&|
    | |      |
    | | {    |
    | |\\    |
    | +------+
    + 11111110000001
    = 

Truth-machine example.

    | +---+
    | |@/0|
    | |$? |
    | |#\1|
    | +---+
    + 0
    = 0

    | +---+
    | |@/0|
    | |$? |
    | |#\1|
    | +---+
    + 1
    = 11111111111111111111111111111111111111111111111111111111111111111111111111111111
