#!/bin/sh

perl -pne "s/\s+/+/g" < wikipedia_search_queries.txt > wikipedia_search_queries_modified.txt

for query in $(cat wikipedia_search_queries_modified.txt); do curl "http://127.0.0.1:5000/api/search?query=$query"; done
