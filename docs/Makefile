# consider gzipping the manpage
build:
	@pandoc cdflow.1.md -s -t man -o cdflow.1

# could do with some refinement...
install: build
	@cp cdflow.1 /usr/local/share/man/

uninstall:
	@rm -f /usr/local/share/man/cdflow.1

clean:
	@rm cdflow.1