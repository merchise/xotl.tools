#!/bin/bash

PYDEV=$(locate pysrc/pydevd.py |grep 3.8 |head -1)
SERVER=127.0.0.1
PORT=5678

# Use /usr/bin/env to ensure virtualenvs are considered
/usr/bin/env python -u "$PYDEV" --vm_type python --client "$SERVER" --port $PORT $@
