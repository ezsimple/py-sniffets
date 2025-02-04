#!/bin/bash
result=$(curl -s -X GET -H "Content-Type: application/json" https://a1.mkeasy.kro.kr/quotes/krandom | jq -r '.[] | {q: .q | gsub("^[ ]+|[ ]+$"; ""), k: .k | gsub("^[ ]+|[ ]+$"; ""), a: .a | gsub("^[ ]+|[ ]+$"; "")}')

# JSON 파싱
q=$(echo "$result" | jq -r '.q')
k=$(echo "$result" | jq -r '.k')
a=$(echo "$result" | jq -r '.a')

# 출력
echo -e "$q\n$k\n\n-- $a" | cowsay -nsf $(cowsay -l | tail -n +2 | tr ' ' '\n' | shuf -n1)
