REPO ?= repo

.PHONY: all extract deploy fresh-all clean-cache clean-repo clean-all
.PRECIOUS: %/Release %/Packages.gz

all: extract deploy

extract:
	python3 extract_deepin_repo.py extraction_config.json $(REPO) files/ cache

FILES := $(foreach d, \
		debian-stable debian-testing ubuntu-bionic,\
		$(foreach f, InRelease Packages Packages.gz Release Release.gpg, $(REPO)/$(d)/$(f)))
deploy: $(FILES) $(REPO)/i-m.dev.gpg $(REPO)/setup.sh

fresh-all: clean-cache all

clean-cache:
	rm -rf cache

clean-repo:
	rm -rf $(REPO)

clean-all: clean-cache clean-repo

%/:
	mkdir -p $@

$(REPO)/i-m.dev.gpg:
	gpg --export -o $@

$(REPO)/setup.sh: $(REPO)/i-m.dev.gpg setup.template.sh
	sed "s~<GPG_KEY_CONTENT>~$$(base64 -w0 $<)~" $(word 2, $^) > $@
	chmod a+x $@

%/InRelease: %/Release
	gpg --yes --clear-sign -o $@ $<

%/Release.gpg: %/Release
	gpg --yes --detach-sign -a -o $@ $<

%/Release: %/Packages %/Packages.gz
	apt-ftparchive release $* > $@

%/Packages.gz: %/Packages
	gzip -c9 $< > $@

