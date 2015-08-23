#!/bin/bash
export DEST="./.exvim.pyblog"
export TOOLS="/home/genial/.exvim//vimfiles/tools/"
export TMP="${DEST}/_symbols"
export TARGET="${DEST}/symbols"
sh ${TOOLS}/shell/bash/update-symbols.sh
