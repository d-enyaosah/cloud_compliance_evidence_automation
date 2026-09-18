# Cloud Compliance Evidence Automation

Portfolio project by Damian Probity Enyaosah.

This Python prototype evaluates a synthetic evidence inventory against illustrative CMMC Level 2 and NIST SP 800-171, FedRAMP/NIST SP 800-53, SOC 2, and PCI DSS control expectations. It identifies missing or stale evidence, assigns transparent risk scores, and produces a gap report, a prioritized plan of action and milestones (POA&M), and an HTML monitoring summary.

## What it accepts

The input CSV contains control identifiers, framework references, technology sources, evidence status, review dates, control criticality, and remediation ownership. Sample sources include AWS, GCP, GitHub, Okta, endpoints, and SaaS services.

## Scoring method

- Missing evidence: base score 5
- Stale evidence: base score 3
- Partial evidence: base score 2
- Current evidence: base score 0
- Criticality multiplier: High 3, Medium 2, Low 1

The final score is the base score multiplied by criticality. Scores of 10 or more are Critical, 6-9 are High, 3-5 are Medium, and 0-2 are Low.

## Outputs

- `output/gap_report.csv`
- `output/poam.csv`
- `output/monitoring_summary.html`

## Run

```bash
python cloud_compliance_analyzer.py data/sample_evidence_inventory.csv --output-dir output
python -m unittest discover -s tests
```

## Scope boundary

This is a synthetic project. It does not connect to live AWS, GCP, GitHub, Okta, endpoint, GRC, or SIEM APIs; it does not establish certification readiness; and its mappings are illustrative rather than a substitute for authoritative framework requirements or assessor judgment.
