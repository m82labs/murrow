install:
	pip install -r requirements
	mkdir -p /usr/bin/murrow_rss
	cp -R ./* /usr/bin/murrow_rss/
	chmod +x /usr/bin/murrow_rss/murrow.py
	ln -s /usr/bin/murrow_rss/murrow.py /usr/bin/murrow

uninstall:
	rm -rf /usr/bin/murrow /usr/bin/murrow_rss
