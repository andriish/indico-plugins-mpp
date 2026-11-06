#!/bin/bash
# This file is part of the MPP Indico plugins.
# Copyright (C) 2026 MPP
#
# The MPP Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

for dir in $(find -name pytest.ini -exec dirname {} \;); do
    pushd "$dir" >/dev/null
    pytest "$@"
    popd >/dev/null
done
