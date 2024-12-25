.PHONY: format

format:
	find . -type f -name '*.py' -exec black {} \;