#!/usr/bin/env python3

"""
Inspired by: https://ogden.eu/run-notebooks
Thanks!
"""

import nbformat
import sys
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

OUT_FILE = "italy-czechia_time_zero_comparison.ipynb"
SRC_FILE = f"src/{OUT_FILE}"


with open(SRC_FILE) as f:
    nb = nbformat.read(f, as_version=4)
    # timeout is just an estimate
    ep = ExecutePreprocessor(timeout=180, kernel_name='python')
    try:
        out = ep.preprocess(nb)
    except CellExecutionError as e:
        print(f'Error executing the notebook {SRC_FILE}.', file=sys.stderr)
        print(f'See notebook {OUT_FILE} for the traceback.', file=sys.stderr)
        print(e, file=sys.stderr)
        exit(1)
    except TimeoutError:
        print(f'Timeout executing the notebook {SRC_FILE}.', file=sys.stderr)
        exit(1)
    finally:
        # Write output file
        with open(OUT_FILE, mode='wt') as f:
            nbformat.write(nb, f)