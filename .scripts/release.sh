#!/usr/bin/bash
set -euxo pipefail

rm -rf dist build
python -m pip install -U pip
python -m pip install -U setuptools wheel twine
python setup.py sdist bdist_wheel
twine check dist/*
python -m twine upload -u __token__ dist/*
