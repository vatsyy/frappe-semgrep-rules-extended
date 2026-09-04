ROOT := $(CURDIR)
RULES := $(ROOT)/rules
UPSTREAM_RULES := $(RULES)/upstream/frappe
BACKPORT_RULES := $(RULES)/backports
CUSTOM_RULES := $(RULES)/custom

.PHONY: test check-contract check-governance test-governance test-benchmark test-ci test-scan-contract test-all-apps-contract test-comparison test-pilot-evidence test-batch01-evidence test-batch02-evidence validate test-upstream test-backports test-custom scan-public-snapshot scan-all-apps

test: check-contract check-governance test-governance test-benchmark test-ci test-scan-contract test-all-apps-contract test-comparison test-pilot-evidence test-batch01-evidence test-batch02-evidence validate test-upstream test-backports test-custom

check-contract:
	python3 scripts/check_rule_contract.py

check-governance:
	python3 scripts/check_governance.py

test-governance:
	python3 -m unittest tests.test_governance

test-benchmark:
	python3 -m unittest tests.test_benchmark_contract

test-ci:
	python3 -m unittest tests.test_ci_contract

test-scan-contract:
	python3 -m unittest tests.test_snapshot_scan

test-all-apps-contract:
	python3 -m unittest tests.test_all_apps_scan

test-comparison:
	python3 -m unittest tests.test_compare_scan_findings

test-pilot-evidence:
	python3 -m unittest tests.test_pilot_evidence

test-batch01-evidence:
	python3 -m unittest tests.test_batch01_evidence

test-batch02-evidence:
	python3 -m unittest tests.test_batch02_evidence

scan-public-snapshot:
	python3 scripts/scan_public_snapshot.py \
		--source-repo "$(SOURCE_REPO)" \
		--source-mode "$(or $(SOURCE_MODE),commit)" \
		$(if $(SOURCE_REVISION),--source-revision "$(SOURCE_REVISION)") \
		--source-name "$(SOURCE_NAME)" \
		--output "$(SCAN_OUTPUT)" \
		$(SCAN_OPTIONS)

scan-all-apps:
	python3 scripts/scan_all_apps.py \
		--apps-root "$(or $(APPS_ROOT),..)" \
		--output "$(SCAN_OUTPUT)" \
		$(SCAN_OPTIONS)

validate:
	semgrep --validate --config=$(RULES) $(ROOT)

test-upstream:
	semgrep --test --strict --test-ignore-todo $(UPSTREAM_RULES)

test-backports:
	semgrep --test --strict --test-ignore-todo $(BACKPORT_RULES)

test-custom:
	semgrep --test --strict --test-ignore-todo $(CUSTOM_RULES)
