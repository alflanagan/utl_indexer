REQTS_SRC = requirements.in dev-requirements.in emacs-requirements.in
REQTS_PINNED = $(REQTS_SRC:.in=.txt)
APIDOC_FLAGS = -T -e -o doc/api
EXCLUDED_LIB = utl_lib/parsetab.py utl_lib/utl_lex.py utl_lib/utl_lex_comments.py
RST_DOCS = doc/parse_file.rst doc/lex_file.rst doc/index.rst doc/unpack_zip_files.rst doc/utl_grammar.rst

.PHONY: pin_reqts

%.txt: %.in
	pip-compile $<

pin_reqts: 
	pip install --upgrade pip pip-tools setuptools; \
	rm -f $(REQTS_PINNED); \
	$(MAKE) $(REQTS_PINNED); \
	pip-sync $(REQTS_PINNED)

doc: doc/_build/html/index.html

doc/_build/html/index.html: utl_lib/*.py  $(RST_DOCS)
	rm -f doc/api/*; \
	sphinx-apidoc ${APIDOC_FLAGS} utl_lib $(EXCLUDED_LIB); \
	sphinx-apidoc ${APIDOC_FLAGS} utl_test; \
	cd doc; \
	$(MAKE) clean; \
	$(MAKE) html
