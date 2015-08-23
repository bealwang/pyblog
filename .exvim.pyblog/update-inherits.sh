#!/bin/bash
export DEST="./.exvim.pyblog"
export TOOLS="/home/genial/.exvim//vimfiles/tools/"
export TMP="${DEST}/_inherits"
export TARGET="${DEST}/inherits"
sh ${TOOLS}/shell/bash/update-inherits.sh
