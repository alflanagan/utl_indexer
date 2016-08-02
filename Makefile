REQTS_SRC = requirements.in dev-requirements.in emacs-requirements.in
REQTS_PINNED = $(REQTS_SRC:.in=.txt)

.PHONY: pin_reqts

%.txt: %.in
	pip-compile $<

pin_reqts: 
	pip install --upgrade pip pip-tools setuptools
	rm -f $(REQTS_PINNED)
	$(MAKE) $(REQTS_PINNED)

# for SRC in $(REQTS_SRC):
# pip-compile requirements.in
# pip-compile dev-requirements.in
# # pip-compile emacs-requirements.in

# pip-sync requirements.txt dev-requirements.txt # emacs-requirements.txt
