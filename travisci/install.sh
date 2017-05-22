#!/bin/bash

set -euv

# Install old (pytest-)flake8 for py26
if [ ${TRAVIS_PYTHON_VERSION:0:3} == 2.6 ]; then
  pip install pytest-flake8==0.5 flake8==2.6.2
fi

# https://github.com/release-engineering/kobo/issues/31
if [ ${TRAVIS_PYTHON_VERSION:0:1} == 3 ]; then
  pip install git+git://github.com/release-engineering/kobo.git@python-3-dev
fi

pip install pytest-flake8
