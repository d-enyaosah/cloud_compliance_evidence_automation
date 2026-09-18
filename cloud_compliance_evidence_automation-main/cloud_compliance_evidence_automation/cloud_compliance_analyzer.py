import argparse
import csv
import html
from collections import Counter
from datetime import date, datetime
from pathlib import Path


BASE_SCORE = {"missing": 5, "stale": 3, "partial": 2, "current": 0}
CRITICALITY = {"high": 3, "medium": 2, "low": 1}


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def evaluate(row, as_of):
    status = row["evidence_status"].strip().lower()
    review_date = parse_date(row.get("next_review_date", ""))
    if review_date and review_date < as_of and status == "current":
        status = "stale"
    score = BASE_SCORE.get(status, 5) * CRITICALITY.get(row["criticality"].strip().lower(), 2)
    rating = "Critical" if score >= 10 else "High" if score >= 6 else "Medium" if score >= 3 else "Low"
    action = {
        "missing": "Collect and validate control evidence",
        "stale": "Refresh and reapprove evidence",
        "partial": "Resolve evidence gap and document scope",
        "current": "Maintain monitoring cadence",
    }.get(status, "Clarify evidence status")
    return {**row, "normalized_status": status.title(), "risk_score": score, "risk_rating": rating, "recommended_action": action}


def analyze(input_path, output_dir, as_of=date.today()):
    output_dir.mkdir(parents=True, exist_ok=True)
    with input_path.open(newline="", encoding="utf-8") as f:
        rows = [evaluate(r, as_of) for r in csv.DictReader(f)]
    rows.sort(key=lambda r: (-int(r["risk_score"]), r["control_id"]))

    gap_fields = list(rows[0].keys())
    with (output_dir / "gap_report.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=gap_fields)
        writer.writeheader(); writer.writerows(rows)

    poam_fields = ["poam_id", "control_id", "frameworks", "technology_source", "weakness", "recommended_action", "owner", "target_date", "risk_rating", "risk_score"]
    poam_rows = []
    for index, row in enumerate((r for r in rows if r["normalized_status"] != "Current"), start=1):
        poam_rows.append({
            "poam_id": f"POAM-{index:03d}", "control_id": row["control_id"], "frameworks": row["frameworks"],
            "technology_source": row["technology_source"], "weakness": row["gap_description"],
            "recommended_action": row["recommended_action"], "owner": row["owner"], "target_date": row["target_date"],
            "risk_rating": row["risk_rating"], "risk_score": row["risk_score"],
        })
    with (output_dir / "poam.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=poam_fields)
        writer.writeheader(); writer.writerows(poam_rows)

    ratings = Counter(r["risk_rating"] for r in rows)
    sources = Counter(r["technology_source"] for r in rows if r["normalized_status"] != "Current")
    body = "".join(f"<tr><td>{html.escape(r['control_id'])}</td><td>{html.escape(r['frameworks'])}</td><td>{html.escape(r['technology_source'])}</td><td>{r['normalized_status']}</td><td>{r['risk_rating']}</td><td>{r['risk_score']}</td><td>{html.escape(r['owner'])}</td></tr>" for r in rows)
    source_items = "".join(f"<li>{html.escape(source)}: {count} open item(s)</li>" for source, count in sorted(sources.items()))
    report = f"""<!doctype html><html><head><meta charset='utf-8'><title>Cloud Compliance Monitoring Summary</title><style>body{{font-family:Arial,sans-serif;margin:32px;color:#17202a}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #d9d9d9;padding:8px;text-align:left}}th{{background:#17324d;color:white}}.metrics{{display:flex;gap:18px;margin:18px 0}}.metric{{padding:14px;background:#f4f7fa;border:1px solid #d9d9d9}}</style></head><body><h1>Cloud Compliance Monitoring Summary</h1><p>Synthetic personal-project data as of {as_of.isoformat()}.</p><div class='metrics'><div class='metric'>Controls: {len(rows)}</div><div class='metric'>Critical: {ratings['Critical']}</div><div class='metric'>High: {ratings['High']}</div><div class='metric'>Open POA&amp;M items: {len(poam_rows)}</div></div><h2>Open items by technology source</h2><ul>{source_items}</ul><h2>Control evidence review</h2><table><tr><th>Control</th><th>Frameworks</th><th>Source</th><th>Evidence</th><th>Rating</th><th>Score</th><th>Owner</th></tr>{body}</table><p><em>Illustrative mappings only; not a certification determination.</em></p></body></html>"""
    (output_dir / "monitoring_summary.html").write_text(report, encoding="utf-8")
    return rows, poam_rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate synthetic cloud compliance evidence.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--as-of", type=parse_date, default=date.today())
    args = parser.parse_args()
    analyze(args.input_csv, args.output_dir, args.as_of)
