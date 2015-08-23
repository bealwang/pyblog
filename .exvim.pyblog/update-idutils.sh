#!/bin/bash
export DEST="./.exvim.pyblog"
export TOOLS="/home/genial/.exvim//vimfiles/tools/"
export TMP="${DEST}/_ID"
export TARGET="${DEST}/ID"
sh ${TOOLS}/shell/bash/update-idutils.sh
