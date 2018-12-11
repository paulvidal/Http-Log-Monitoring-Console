run:
	python monitoring_console.py

test:
	python -m unittest

generate:
	python log_generator.py --rate 100

local_run:
	python monitoring_console.py --path ./access.log

local_generate:
	python log_generator.py --path ./access.log --rate 1000