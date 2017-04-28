NAME = python-dns
VERSION = 1.14.0

all: srpm

clean:
	rm -rf dist/
	rm -rf $(NAME)-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-1.src.rpm
	rm -fr *.log

dist:
	git clone -b v$(VERSION) --single-branch https://github.com/rthalley/dnspython $(NAME)-$(VERSION)
	tar -zcvf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	rm -fr $(NAME)-$(VERSION)

srpm: dist
	fedpkg --dist epel7 srpm

rpm:  srpm
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-1.el7.src.rpm --resultdir=.

.PHONY: dist rpm srpm
