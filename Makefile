VIRTUALENV ?= virtualenv2.7
VIRTUALENV_DIR ?= virtualenv
REQUIREMENTS ?= requirements.txt

WORKERS ?= worker
MASTER ?= master

WRK_SVC = $(WORKERS:%=./service/%)

all: run

$(VIRTUALENV_DIR):
	$(VIRTUALENV) $@

$(VIRTUALENV_DIR)/.install: $(VIRTUALENV_DIR) $(REQUIREMENTS)
	. ./$(VIRTUALENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS)
	touch $@

$(MASTER):
	ln -s ../sv/$(MASTER) service/$(MASTER)

run: $(VIRTUALENV_DIR)/.install $(WRK_SVC) $(MASTER)
	rm -rf service/*/supervise
	. ./$(VIRTUALENV_DIR)/bin/activate && runsvdir service/

clean:
	rm -rf $(VIRTUALENV_DIR)
	rm -rf service/*

$(WRK_SVC):
	ln -s ../sv/$(notdir $@) $@

.PHONY: all run clean
