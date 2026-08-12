ROOT := $(CURDIR)
RULES := $(ROOT)/rules
UPSTREAM_RULES := $(RULES)/upstream/frappe
BACKPORT_RULES := $(RULES)/backports
CUSTOM_RULES := $(RULES)/custom

.PHONY: test validate test-upstream test-backports test-custom

test: validate test-upstream test-backports test-custom

validate:
	semgrep --validate --config=$(RULES) $(ROOT)

test-upstream:
	semgrep --test --strict --test-ignore-todo $(UPSTREAM_RULES)

test-backports:
	semgrep --test --strict --test-ignore-todo $(BACKPORT_RULES)

test-custom:
	semgrep --test --strict --test-ignore-todo $(CUSTOM_RULES)
