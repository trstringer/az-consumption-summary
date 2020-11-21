CURRENT_DIR=$(shell pwd)
OUTPUT_DIR=~/.local/bin
OUTPUT_BIN=$(OUTPUT_DIR)/az-consumption-summary
REPORT_BIN=$(OUTPUT_DIR)/az-consumption-report

.PHONY: install install-report clean

install:
	if [ ! -d "$(CURRENT_DIR)/venv" ]; then \
		python3 -m venv venv; \
		. venv/bin/activate; \
		pip install -r requirements.txt; \
	fi; \
	sed 's|SOURCE_DIR|$(CURRENT_DIR)|g' ./az-consumption-summary > $(OUTPUT_BIN)
	chmod 755 $(OUTPUT_BIN)

install-report: install
	cp az-consumption-report.sh $(REPORT_BIN)

clean:
	if [ -f "$(OUTPUT_BIN)" ]; then rm $(OUTPUT_BIN); fi
	if [ -f "$(REPORT_BIN)" ]; then rm $(REPORT_BIN); fi
