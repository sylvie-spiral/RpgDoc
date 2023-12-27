#! /bin/bash
rawfiles=(doc/*)
pandoc "${rawfiles[@]}" $@ -o out/Document.pdf
./pdfsizeopt-linux/pdfsizeopt out/Document.pdf