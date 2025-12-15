from pathlib import Path

import polars as pl
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def format_si(value):
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "0"
    suffixes = [
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "k"),
    ]
    abs_num = abs(num)
    for threshold, suffix in suffixes:
        if abs_num >= threshold:
            scaled = num / threshold
            return f"{scaled:.1f}{suffix}" if scaled < 10 else f"{scaled:.0f}{suffix}"
    return f"{num:.0f}"

app.jinja_env.filters["si"] = format_si

DEFAULT_METRICS = {
    "looping_subnets": 0,
    "amplifying_subnets": 0,
    "max_amplification": 0,
    "router_ips": 0,
    "tum_hitlist": 0,
    "overlap_absolute": 0,
    "overlap_percentage": 0,
}

def load_references():
    ref_path = Path(app.root_path) / "static/bib/references.bib"
    if not ref_path.exists():
        return []
    content = ref_path.read_text(encoding="utf-8")
    entries = [entry.strip() for entry in content.split("\n@") if entry.strip()]
    normalized = []
    for entry in entries:
        if not entry.startswith("@"):
            entry = "@" + entry
        normalized.append(entry)
    return normalized

def load_metrics():
    metrics = DEFAULT_METRICS.copy()
    stats_path = Path(app.root_path) / "static/data/statistics.csv"
    if not stats_path.exists():
        return metrics
    try:
        df = pl.read_csv(stats_path, separator=";")
    except Exception:
        return metrics
    if df.height == 0:
        return metrics
    try:
        latest = df.sort("last-scan").to_dicts()[-1]
    except Exception:
        latest = df.to_dicts()[-1]
    column_map = {
        "router_ips": "router-ips",
        "overlap_absolute": "overlap-hitlist-absolute",
        "overlap_percentage": "overlap-hitlist-percentage",
        "looping_subnets": "looping-subnets",
        "amplifying_subnets": "amplifying-subnets",
        "max_amplification": "max-amplification",
    }
    for metric_key, column in column_map.items():
        value = latest.get(column)
        if value is None:
            continue
        try:
            metrics[metric_key] = float(value) if "percentage" in metric_key else int(value)
        except (TypeError, ValueError):
            continue
    return metrics

def load_affected_ases():
    ases_path = Path(app.root_path) / "static/data/affected-ases.csv"
    if not ases_path.exists():
        return pl.DataFrame({"asn": []})
    try:
        df = pl.read_csv(
            ases_path,
            has_header=False,
            new_columns=["asn"],
            dtypes={"asn": pl.Int64},
        )
    except Exception:
        return pl.DataFrame({"asn": []})
    return df

affected_ases_df = load_affected_ases()

def is_as_affected(asn_int: int) -> bool:
    if affected_ases_df.is_empty():
        return False
    try:
        match = affected_ases_df.filter(pl.col("asn") == asn_int)
    except Exception:
        return False
    return match.height > 0

def check_as_number(asn_value):
    try:
        asn_int = int(asn_value)
    except (TypeError, ValueError):
        return None, "Please enter a valid AS number.", "error"
    if asn_int < 0:
        return None, "Please enter a valid AS number.", "error"
    if is_as_affected(asn_int):
        return asn_int, "Your AS is affected by routing loops!", "affected"
    return asn_int, "Your AS is not affected!", "safe"

@app.route("/", methods=["GET", "POST"])
def index():
    metrics = load_metrics()
    references = load_references()
    as_result = None
    submitted_asn = ""
    if request.method == "POST":
        submitted_asn = request.form.get("asn", "").strip()
        _, message, state = check_as_number(submitted_asn)
        if state == "error":
            as_result = {"message": message, "state": "error"}
        else:
            as_result = {"message": message, "state": state}
    return render_template(
        "index.html",
        metrics=metrics,
        references=references,
        as_result=as_result,
        submitted_asn=submitted_asn
    )

@app.route("/check_as", methods=["POST"])
def check_as():
    data = request.get_json(silent=True) or {}
    asn_value = data.get("asn")
    asn_int, message, state = check_as_number(asn_value)
    if state == "error":
        return jsonify({"error": message}), 400
    return jsonify({
        "affected": state == "affected",
        "message": message,
        "asn": asn_int,
    })

@app.route("/artifacts")
def artifacts():
    return render_template("artifacts.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
