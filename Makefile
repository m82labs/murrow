install:
	@if [ -f '/usr/bin/figlet' ]; then figlet 'MURROW RSS'; fi
	@echo 'Installing Murrow RSS'
	@pip3 install -r requirements
	@mkdir -p /usr/bin/murrow_rss
	@cp -R ./* /usr/bin/murrow_rss/
	@chmod +x /usr/bin/murrow_rss/murrow.py
	@ln -s /usr/bin/murrow_rss/murrow.py /usr/bin/murrow
	@mkdir -p /usr/share/doc/murrow/examples
	@cp ./murrow.config.example /usr/share/doc/murrow/examples
uninstall:
	@echo 'Uninstalling...'
	@rm -rf /usr/bin/murrow /usr/bin/murrow_rss /usr/share/doc/murrow
	@echo "Users of Murrow on this system will also need to remove the '.murrow' directory from their home directory to completely uniinstall murrow."
