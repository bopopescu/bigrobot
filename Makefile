clean:
	find . -name "*.pyc" -exec rm -fv {} \;
	find . -name ".DS_Store" -exec rm -fv {} \;
	find . -name "*.orig" -exec rm -fv {} \;
