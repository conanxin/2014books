.PHONY: pdf web epub clean all

pdf:
	bash scripts/build_pdf.sh

web:
	python3 scripts/generate_web.py

epub:
	bash scripts/build_epub.sh

clean:
	rm -rf web dist latex/*.aux latex/*.log latex/*.out latex/*.toc latex/*.lof latex/*.lot latex/*.fls latex/*.fdb_latexmk build/

all: web pdf epub
