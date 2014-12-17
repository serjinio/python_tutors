#!/bin/bash

output_file="res.dat"

echo "Compiling program sources..."
gcc -lm esrf_sat.c
if (($? != 0)); then
    echo "Some error occurred during esrf_sat compilation."
    exit 1
fi

echo "Running esrf_sat, output will be written to $output_file"
./a.out > $output_file
if (($? != 0)); then
    echo "Some error occurred during esrf_sat execution."
    exit 1
fi
