ROOT := $(CURDIR)
RULES := $(ROOT)/rules
SEMGREP ?= semgrep

.PHONY: test check-contract test-scanners test-benchmark validate test-upstream test-backports test-custom scan-public-snapshot scan-all-apps

test: check-contract test-scanners test-benchmark validate test-upstream test-backports test-custom

check-contract:
	python3 scripts/check_rule_contract.py

test-scanners:
	SEMGREP="$(SEMGREP)" python3 -m unittest discover -s tests

test-benchmark:
	python3 benchmarks/run.py --semgrep-command "$(SEMGREP)"

validate:
	$(SEMGREP) --validate --config=$(RULES) $(ROOT)

test-upstream:
	$(SEMGREP) --test --strict --test-ignore-todo $(RULES)/upstream/frappe

test-backports:
	$(SEMGREP) --test --strict --test-ignore-todo $(RULES)/backports

test-custom:
	$(SEMGREP) --test --strict --test-ignore-todo $(RULES)/custom

scan-public-snapshot:
	python3 scripts/scan_public_snapshot.py \
		--source-repo "$(SOURCE_REPO)" \
		--source-mode "$(or $(SOURCE_MODE),commit)" \
		$(if $(SOURCE_REVISION),--source-revision "$(SOURCE_REVISION)") \
		--source-name "$(SOURCE_NAME)" \
		--output "$(SCAN_OUTPUT)" \
		--semgrep-command "$(SEMGREP)" $(SCAN_OPTIONS)

scan-all-apps:
	python3 scripts/scan_all_apps.py \
		--apps-root "$(or $(APPS_ROOT),..)" \
		--output "$(SCAN_OUTPUT)" \
		--semgrep-command "$(SEMGREP)" $(SCAN_OPTIONS)
