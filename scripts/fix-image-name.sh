#! /bin/bash

find "$1" -type f -name '*.jp*g' | grep "\/content\/" | while read f
do
    echo "$f" | grep -qE " [0-9]\." && {
        n=$(echo "$f" | sed -E 's/ ([0-9]\.)/ 0\1/g')
        echo "$f -> $n"
        mv "$f" "$n"
    }
done