#!/bin/bash
grep -o 'https://www.goodreads.com/quotes/tag/[^ ]*' log/crawling_goodreads.py-2024-11-05.log | sed 's/,//' | sed 's/://' | sed 's/://' | sed 's/"//' | uniq
