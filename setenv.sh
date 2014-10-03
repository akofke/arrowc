#!/usr/bin/env bash

if $(test -z "$PS1") ; then
    echo "You must source this file not execute it"
    echo "run:"
    echo "    $ source setenv.sh"
    exit
fi

export BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P )"
export __PYTHONPATH=$PYTHONPATH
export __PATH=$PATH

leave () {
    export PYTHONPATH=$__PYTHONPATH
    export PATH=$__PATH
    deactivate
    unset BASEDIR
    unset __PYTHONPATH
    unset __PATH
    unset -f leave
    unset -f deactivate
    echo 'left the python virtual environment'
}

test -d "$BASEDIR/env" || virtualenv --no-site-packages "$BASEDIR/env"
source "$BASEDIR/env/bin/activate"

pip install -r "$BASEDIR/requirements.txt"

export PYTHONPATH="$BASEDIR:$PYTHONPATH"
export PATH="$BASEDIR/bin:$PATH"

echo "python environment activated"
echo "you can leave the python environment for this project with 'leave'"
