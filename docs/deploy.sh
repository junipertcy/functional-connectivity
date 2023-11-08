#! /bin/bash
make html

aws s3 sync ./_build/html s3://docs.netscied.tw/functional-connectivity --acl public-read
aws cloudfront create-invalidation --distribution-id EJWRA9WAFT3AG --paths /functional-connectivity/*
