# store the current working directory
CWD := $(shell pwd)
BASEDIR := $(CWD)
PRINT_STATUS = export EC=$$?; cd $(CWD); if [ "$$EC" -eq "0" ]; then printf "SUCCESS!\n"; else exit $$EC; fi
VERSION=0.0.1

BUILDS    := .build
DEPLOY    := $(BUILDS)/deploy
TARDIR    := tendrl-bridge-common-$(VERSION)
RPMBUILD  := $(HOME)/rpmbuild


dist:
	rm -fr $(HOME)/$(BUILDS)
	mkdir -p $(HOME)/$(BUILDS) $(RPMBUILD)/SOURCES
	cp -fr $(BASEDIR) $(HOME)/$(BUILDS)/$(TARDIR)
	cd $(HOME)/$(BUILDS); \
	tar --exclude-vcs --exclude=.* -zcf tendrl-bridge-common-$(VERSION).tar.gz $(TARDIR); \
	cp tendrl-bridge-common-$(VERSION).tar.gz $(RPMBUILD)/SOURCES
	# Cleaning the work directory
	rm -fr $(HOME)/$(BUILDS)


rpm:
	@echo "target: rpm"
	@echo  "  ...building rpm $(V_ARCH)..."
	rm -fr $(BUILDS)
	mkdir -p $(DEPLOY)/latest
	mkdir -p $(RPMBUILD)/SPECS
	sed -e "s/@VERSION@/$(VERSION)/" bridge_common.spec \
	        > $(RPMBUILD)/SPECS/bridge_common.spec
	rpmbuild -ba $(RPMBUILD)/SPECS/bridge_common.spec
	$(PRINT_STATUS); \
	if [ "$$EC" -eq "0" ]; then \
		FILE=$$(readlink -f $$(find $(RPMBUILD)/RPMS -name tendrl-bridge-common-$(VERSION)*.rpm)); \
		cp -f $$FILE $(DEPLOY)/latest/; \
		printf "\nThe bridge common RPMs are located at:\n\n"; \
		printf "   $(DEPLOY)/latest\n\n\n\n"; \
	fi
