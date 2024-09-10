#!/usr/bin/sh
BASEDIR=$(dirname $0) &&
    python3 "$BASEDIR"/compilation.py -I "$1"/idl -O "$1"/output &&
    mkdir -p "$1"/temp &&
    cp -rf "$1"/output/* "$1"/temp &&
    cp -rf "$1"/impl/* "$1"/temp &&
    mkdir -p "$1"/build &&
    g++ "$1"/temp/*.cpp -I "$BASEDIR"/../runtime/include -shared -fPIC -o "$1"/build/libtest.so &&
    echo "Dynamic link library is generated successfully." &&
    rm "$1"/temp/*.cpp "$1"/temp/*_impl.h &&
    cp -rf "$1"/src/* "$1"/temp &&
    g++ "$1"/temp/*.cpp "$1"/build/libtest.so -I "$BASEDIR"/../runtime/include -o "$1"/build/test &&
    echo "Excutable file is generated successfully, running..." &&
    "$1"/build/test
