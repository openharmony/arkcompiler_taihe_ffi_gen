#!/bin/bash -eux

# Assuming pwd is //test/integer and Taihe is installed at //dist
export TAIHE_OUT_PATH=$(realpath ../../dist)

gn gen out --args="target_cpu=\"$(uname -m)\""

ninja -C out


lib_path=$(realpath ./out)
cp "$lib_path/libinteger_napi.so" "$lib_path/integer.node"