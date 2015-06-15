#!/usr/bin/env dash
# Execute tests for a module and generate a coverage report
# Author: A. Lloyd Flanagan

if [ $# -lt 1 ]; then
    echo "Usage: $(basename $0) module_name"
    echo "       Runs coverage with program test_{module_name}.py"
    exit 1
fi

MODULE_DIR=utl_lib
MODULE_NAME=${1%.py} # .py is optional
MODULE_FILE=../${MODULE_DIR}/${MODULE_NAME}.py
TEST_SUITE=test_${MODULE_NAME}.py

if [ ! -r ${MODULE_FILE} ]; then
    echo "ERROR: can't locate module to test: expected \"${MODULE_FILE}\"." >&2
    exit 2
fi

if [ ! -r ${TEST_SUITE} ]; then
    echo "ERROR: can't locate test file for module '${MODULE_NAME}': expected \"${TEST_SUITE}\"." >&2
    exit 3
fi
    
coverage run --source=${MODULE_DIR}.${MODULE_NAME} --branch ${TEST_SUITE}
coverage report -m ${MODULE_FILE}

# Local Variables:
# indent-tabs-mode: nil
# tab-width: 4
# End:
