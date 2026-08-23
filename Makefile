ROOT := $(CURDIR)
RULES := $(ROOT)/rules
UPSTREAM_RULES := $(RULES)/upstream/frappe
BACKPORT_RULES := $(RULES)/backports
CUSTOM_RULES := $(RULES)/custom

.PHONY: test check-contract check-governance test-governance test-benchmark validate test-upstream test-backports test-custom

test: check-contract check-governance test-governance test-benchmark validate test-upstream test-backports test-custom

check-contract:
	python3 scripts/check_rule_contract.py

check-governance:
	python3 scripts/check_governance.py

test-governance:
	python3 -m unittest tests.test_governance

test-benchmark:
	python3 -m unittest tests.test_benchmark_contract

validate:
	semgrep --validate --config=$(RULES) $(ROOT)

test-upstream:
	semgrep --test --strict --test-ignore-todo $(UPSTREAM_RULES)

test-backports:
	semgrep --test --strict --test-ignore-todo $(BACKPORT_RULES)

test-custom:
	semgrep --test --strict --test-ignore-todo $(CUSTOM_RULES)
