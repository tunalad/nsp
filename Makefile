PREFIX = /usr/local

SH_FILE = nsp.sh
AWK_FILE = nsp.awk
TSV_FILE = nsp.tsv

nsp: $(SH_FILE) $(AWK_FILE) $(TSV_FILE)
	cat $(SH_FILE) > $@
	echo 'exit 0' >> $@
	echo "#EOF" >> $@
	tar czf - $(AWK_FILE) $(TSV_FILE) >> $@
	chmod +x $@

test: $(SH_FILE)
	shellcheck -s sh $(SH_FILE)

clean:
	rm -f nsp

install: nsp
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f nsp $(DESTDIR)$(PREFIX)/bin
	chmod 755 $(DESTDIR)$(PREFIX)/bin/nsp

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/nsp

.PHONY: test clean install uninstall
