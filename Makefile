.PHONY: upload
.PHONY: install

clean:
	@echo "Cleaning the project..."
	@rm -rf dist > /dev/null 2>&1
	@echo "Clean completed successfully."
	
build:
	@echo "Building the project..."
	@mkdir dist > /dev/null 2>&1
	@zip -q -j ./dist/pyappm.zip ./src/pyappm/*.py ./src/pyappm/py.typed ./src/pyappm/pyappm LICENSE.txt README.md CHANGELOG.md -x ./src/pyappm/installer.py > /dev/null 2>&1
	@echo "Build completed successfully."
	@echo "The build is located in the dist directory."

upload:
	@scp -r ./dist/pyappm.zip ./src/pyappm/installer.py root@10.32.1.5:/inetpub/www/pyappm.nl/downloads
	@echo "Upload completed successfully."

install:
	@echo "Now installing"
	@./install
	@echo "Install completed successfully."

all:
	make clean
	make build
	make upload
	make install