.PHONY: publish
publish:
	rm -rf dist/
	uv build
	uv publish