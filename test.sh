#!/bin/sh

# Just a rudimentary sanity test, better than nothing.

EXPECTED='110101010101011111111'
R=`echo '11111110000001' | src/nhohnhehr.py bits eg/reverse-esque.nho`
if [ $R = $EXPECTED ]; then
    echo 'Sanity test passed.'
else
    echo "Expected $EXPECTED but got $R."
    exit 1
fi
