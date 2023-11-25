#! /bin/bash
rawfiles=(doc/*)
pandoc "${rawfiles[@]}" $@ --verbose
