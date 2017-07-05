#!/bin/bash

set -euv

# Install old eng-rhel-6 libs for py26
if [ ${TRAVIS_PYTHON_VERSION:0:3} == 2.6 ]; then
  pip install pytest==2.3.5 py==1.4.15 requests==2.3.0
fi

# https://github.com/release-engineering/kobo/issues/31
if [ ${TRAVIS_PYTHON_VERSION:0:1} == 3 ]; then
  pip install git+git://github.com/release-engineering/kobo.git@python-3-dev
fi

# We can run the flake8 tests on py27 and above
if [ ${TRAVIS_PYTHON_VERSION:0:3} != 2.6 ]; then
  pip install pytest-flake8
fi

pip install pytest-cov python-coveralls
