REQTS_SRC = requirements.in dev-requirements.in emacs-requirements.in
REQTS_PINNED = $(REQTS_SRC:.in=.txt)
APIDOC_FLAGS = -T -e -o doc/api
EXCLUDED_LIB = utl_lib/parsetab.py utl_lib/utl_lex.py utl_lib/utl_lex_comments.py

.PHONY: pin_reqts

%.txt: %.in
	pip-compile $<

pin_reqts: 
	pip install --upgrade pip pip-tools setuptools; \
	rm -f $(REQTS_PINNED); \
	$(MAKE) $(REQTS_PINNED); \
	pip-sync $(REQTS_PINNED)

doc: doc/_build/html/index.html

doc/_build/html/index.html: utl_lib/*.py
	rm -f doc/api/*; \
	sphinx-apidoc ${APIDOC_FLAGS} utl_lib $(EXCLUDED_LIB); \
	sphinx-apidoc ${APIDOC_FLAGS} utl_test; \
	cd doc; \
	$(MAKE) clean; \
	$(MAKE) html
