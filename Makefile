clean:
	@echo "Cleaning the project..."
	@rm -rf dist > /dev/null 2>&1
	@echo "Clean completed successfully."
build:
	@echo "Building the project..."
	@rm -rf dist > /dev/null 2>&1
	@mkdir dist > /dev/null 2>&1
	@zip -q -j ./dist/pyappm.zip ./src/pyappm/*.py ./src/pyappm/py.typed ./src/pyappm/pyappm LICENSE.txt README.md -x ./src/pyappm/installer.py > /dev/null 2>&1
	@echo "Build completed successfully."
	@echo "The build is located in the dist directory."
	@echo "Now uploading: dist/pyappm.zip"
	@./upload
	@echo "Upload completed successfully."
	@echo "Now installing"
	@./install
	@echo "Install completed successfully."

