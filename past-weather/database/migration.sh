#!/bin/bash
# 트랜젝션 분리를 위해 파일을 분리함
python truncate_tables.py
python migration_data.py
python vacuum.py
