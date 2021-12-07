#!/bin/sh

curl -L "https://about.gitlab.com/features/" > gitlab_features_expected.html

wget https://raw.githubusercontent.com/big-data-team/python-course/master/gitlab_features.html
