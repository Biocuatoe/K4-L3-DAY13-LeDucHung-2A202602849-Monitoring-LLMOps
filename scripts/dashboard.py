"""Render the six-panel runtime dashboard from data/logs.jsonl as a static HTML page.

Panels/aggregations/units/thresholds come from config/dashboard.yaml.
Usage: python scripts/dashboard.py [--minutes 60] [--out data/dashboard.html]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.metrics import percentile  # noqa: E402


def load_records(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        r["_t"] = datetime.fromisoformat(r["ts"].replace("Z", "+00:00"))
        rows.append(r)
    return rows


def minute(t: datetime) -> datetime:
    return t.replace(second=0, microsecond=0)


def svg_chart(series: dict[str, list[float]], labels: list[str], thr: float | None, unit: str,
              colors=("#2563eb", "#dc2626", "#16a34a", "#9333ea"), bars=False, thr2: float | None = None) -> str:
    w, h, ml, mb, mt = 520, 210, 52, 34, 12
    vals = [v for s in series.values() for v in s if v is not None] + ([thr] if thr is not None else [])
    top = max(vals) * 1.15 if vals and max(vals) > 0 else 1
    n = max(len(labels), 1)
    px = lambda i: ml + (w - ml - 10) * (i + 0.5) / n
    py = lambda v: mt + (h - mt - mb) * (1 - v / top)
    out = [f'<svg viewBox="0 0 {w} {h}" class="chart">']
    for k in range(5):
        v = top * k / 4
        out.append(f'<line x1="{ml}" x2="{w-10}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="grid"/>'
                   f'<text x="{ml-6}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{v:.3g}</text>')
    step = max(1, n // 8)
    for i, lab in enumerate(labels):
        if i % step == 0:
            out.append(f'<text x="{px(i):.1f}" y="{h-16}" class="ax" text-anchor="middle">{lab}</text>')
    for si, (name, s) in enumerate(series.items()):
        c = colors[si % len(colors)]
        if bars:
            bw = max(4, (w - ml - 10) / n * 0.6 / max(len(series), 1))
            for i, v in enumerate(s):
                x = px(i) - bw * len(series) / 2 + si * bw
                out.append(f'<rect x="{x:.1f}" y="{py(v):.1f}" width="{bw:.1f}" height="{py(0)-py(v):.1f}" fill="{c}"/>')
        else:
            pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(s) if v is not None)
            out.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.2"/>')
            for i, v in enumerate(s):
                if v is None:
                    continue
                out.append(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="3" fill="{c}"/>')
    if thr is not None:
        out.append(f'<line x1="{ml}" x2="{w-10}" y1="{py(thr):.1f}" y2="{py(thr):.1f}" class="thr"/>'
                   f'<text x="{w-12}" y="{py(thr)-4:.1f}" class="thrt" text-anchor="end">SLO/threshold {thr:g} {unit}</text>')
    if thr2 is not None:
        out.append(f'<line x1="{ml}" x2="{w-10}" y1="{py(thr2):.1f}" y2="{py(thr2):.1f}" class="thr2"/>'
                   f'<text x="{ml+4}" y="{py(thr2)-4:.1f}" class="thr2t">challenge threshold {thr2:g} {unit}</text>')
    lx = ml
    for si, name in enumerate(series):
        out.append(f'<rect x="{lx}" y="{h-9}" width="10" height="4" fill="{colors[si % len(colors)]}"/>'
                   f'<text x="{lx+14}" y="{h-4}" class="ax">{html.escape(name)}</text>')
        lx += 20 + 7 * len(name)
    out.append(f'<text x="4" y="10" class="ax">{html.escape(unit)}</text></svg>')
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=None)
    ap.add_argument("--since", help="ISO UTC start, overrides --minutes window start")
    ap.add_argument("--until", help="ISO UTC end")
    ap.add_argument("--out", default="data/dashboard.html")
    ap.add_argument("--title-suffix", default="")
    ap.add_argument("--challenge-threshold", type=float, default=None, help="extra latency line (ms)")
    args = ap.parse_args()

    cfg = yaml.safe_load((REPO_ROOT / "config/dashboard.yaml").read_text(encoding="utf-8"))["dashboard"]
    panels = {p["id"]: p for p in cfg["panels"]}
    rows = load_records(REPO_ROOT / "data/logs.jsonl")
    minutes = args.minutes or cfg["time_range_minutes"]
    end = datetime.fromisoformat(args.until.replace("Z", "+00:00")) if args.until else max(r["_t"] for r in rows)
    start = datetime.fromisoformat(args.since.replace("Z", "+00:00")) if args.since else end - timedelta(minutes=minutes)
    rows = [r for r in rows if start <= r["_t"] <= end]
    resp = [r for r in rows if r["event"] == "response_sent"]
    recv = [r for r in rows if r["event"] == "request_received"]
    fail = [r for r in rows if r["event"] == "request_failed"]

    buckets = sorted({minute(r["_t"]) for r in rows if r["event"] in ("response_sent", "request_received", "request_failed")})
    if buckets:
        buckets = [buckets[0] + timedelta(minutes=i) for i in range(int((buckets[-1] - buckets[0]).total_seconds() // 60) + 1)]
    labels = [b.strftime("%H:%M") for b in buckets]

    def by_min(rs, fn):
        d = defaultdict(list)
        for r in rs:
            d[minute(r["_t"])].append(r)
        return [fn(d.get(b, [])) for b in buckets]

    lat = [r["latency_ms"] for r in resp]
    ttft = [r["ttft_ms"] for r in resp]
    p50, p95, p99, tp95 = (percentile(lat, 50), percentile(lat, 95), percentile(lat, 99), percentile(ttft, 95))
    total_cost = sum(r["cost_usd"] for r in resp)
    tin, tout = sum(r["tokens_in"] for r in resp), sum(r["tokens_out"] for r in resp)
    q = sum(r["quality_score"] for r in resp) / len(resp) if resp else 0
    err_rate = 100 * len(fail) / len(recv) if recv else 0
    tools = [r for r in rows if r.get("tool_success") is not None]
    ret_ok = 100 * sum(1 for r in tools if r["tool_success"]) / len(tools) if tools else 100
    span_min = max((end - start).total_seconds() / 60, 1)
    per_min = len(recv) / span_min

    thr = lambda pid: panels[pid]["threshold"]
    def status(ok): return '<span class="ok">WITHIN SLO</span>' if ok else '<span class="bad">BREACH</span>'
    P = lambda pid, title: f'<section class="panel"><h2>{title}</h2><div class="sub">{html.escape(panels[pid]["title"])} &middot; unit: {panels[pid]["unit"]}</div>'
    body = []
    body.append(P("latency", "1. Latency (ms)") + svg_chart(
        {"P50": by_min(resp, lambda x: percentile([r["latency_ms"] for r in x], 50) if x else None),
         "P95": by_min(resp, lambda x: percentile([r["latency_ms"] for r in x], 95) if x else None),
         "P99": by_min(resp, lambda x: percentile([r["latency_ms"] for r in x], 99) if x else None),
         "TTFT P95": by_min(resp, lambda x: percentile([r["ttft_ms"] for r in x], 95) if x else None)},
        labels, thr("latency")["value"], "ms", thr2=args.challenge_threshold) +
        f'<div class="kpi">P50 <b>{p50:.0f}</b> &middot; P95 <b>{p95:.0f}</b> &middot; P99 <b>{p99:.0f}</b> &middot; TTFT P95 <b>{tp95:.0f}</b> ms &middot; SLO P95 &le; {thr("latency")["value"]} ms {status(p95 <= thr("latency")["value"])}</div></section>')
    body.append(P("traffic", "2. Traffic (requests/min)") + svg_chart(
        {"requests": by_min(recv, len)}, labels, thr("traffic")["value"], "req/min", bars=True) +
        f'<div class="kpi">requests <b>{len(recv)}</b> &middot; rate <b>{per_min:.2f}</b>/min (window avg) &middot; floor &ge; {thr("traffic")["value"]}/min</div></section>')
    body.append(P("errors", "3. Errors and retrieval success (%)") + svg_chart(
        {"error %": by_min(recv + fail, lambda x: 100 * sum(1 for r in x if r["event"] == "request_failed")
                           / max(1, sum(1 for r in x if r["event"] == "request_received"))),
         "retrieval success %": by_min([r for r in rows if r.get("tool_success") is not None],
                                        lambda x: 100 * sum(1 for r in x if r["tool_success"]) / len(x) if x else None)},
        labels, thr("errors")["value"], "%") +
        f'<div class="kpi">error rate <b>{err_rate:.1f}%</b> (failed {len(fail)}/{len(recv)}) &middot; retrieval success <b>{ret_ok:.1f}%</b> &middot; error SLO &le; {thr("errors")["value"]}% {status(err_rate <= thr("errors")["value"])}</div></section>')
    body.append(P("cost", "4. Cost (USD)") + svg_chart(
        {"USD/min": by_min(resp, lambda x: sum(r["cost_usd"] for r in x))}, labels, None, "USD/min", bars=True) +
        f'<div class="kpi">total <b>${total_cost:.4f}</b> in window &middot; budget &le; ${thr("cost")["value"]} {status(total_cost <= thr("cost")["value"])}</div></section>')
    body.append(P("tokens", "5. Tokens") + svg_chart(
        {"tokens in": by_min(resp, lambda x: sum(r["tokens_in"] for r in x)),
         "tokens out": by_min(resp, lambda x: sum(r["tokens_out"] for r in x))}, labels, None, "tokens/min", bars=True) +
        f'<div class="kpi">in <b>{tin}</b> &middot; out <b>{tout}</b> tokens &middot; cap &le; {thr("tokens")["value"]} {status(tin + tout <= thr("tokens")["value"])}</div></section>')
    body.append(P("quality", "6. Quality proxy (0-1)") + svg_chart(
        {"mean quality": by_min(resp, lambda x: sum(r["quality_score"] for r in x) / len(x) if x else None)},
        labels, thr("quality")["value"], "score") +
        f'<div class="kpi">mean <b>{q:.3f}</b> &middot; floor &ge; {thr("quality")["value"]} {status(q >= thr("quality")["value"])}</div></section>')

    fmt = "%Y-%m-%d %H:%M:%SZ"
    page = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(cfg['title'])}</title>
<style>
body{{font:13px/1.4 Segoe UI,Arial,sans-serif;background:#f6f7f9;color:#111;margin:0;padding:12px}}
h1{{font-size:18px;margin:0 0 2px}}.meta{{color:#444;margin-bottom:10px}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.panel{{background:#fff;border:1px solid #d0d4da;border-radius:6px;padding:8px}}
.panel h2{{font-size:14px;margin:0}}.sub{{color:#555;font-size:11px}}
.chart{{width:100%;height:auto}}.grid{{stroke:#e5e7eb}}.ax{{font-size:10px;fill:#444}}
.thr{{stroke:#dc2626;stroke-dasharray:5 4;stroke-width:1.5}}.thrt{{font-size:10px;fill:#dc2626}}
.thr2{{stroke:#ea580c;stroke-dasharray:2 3;stroke-width:1.5}}.thr2t{{font-size:10px;fill:#ea580c}}\n.kpi{{font-size:12px;margin-top:2px}}.ok{{color:#15803d;font-weight:700}}.bad{{color:#dc2626;font-weight:700}}
</style>
<h1>{html.escape(cfg['title'])} {html.escape(args.title_suffix)}</h1>
<div class="meta">Source: data/logs.jsonl &middot; time range: {start.strftime(fmt)} &rarr; {end.strftime(fmt)} ({(end-start).total_seconds()/60:.0f} min window, contract default {cfg['time_range_minutes']} min) &middot; refresh {cfg['refresh_seconds']}s &middot; records: {len(rows)}</div>
<div class="grid3">{''.join(body)}</div>"""
    out = REPO_ROOT / args.out
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} | window {start.isoformat()} -> {end.isoformat()} | P95={p95:.0f}ms err={err_rate:.1f}% ret={ret_ok:.1f}%")


if __name__ == "__main__":
    main()
