# Evidence manifest — Lê Đức Hùng (2A202602849)

Tất cả nguồn là output/ảnh sinh từ lần chạy thật trên code ở commit `6b69ca3` (project Langfuse `day13-k4-l3b-2A202602849`). Không có secret; dữ liệu PII chỉ là dữ liệu giả.

| # | File | Nguồn | Chứng minh | CP |
|---|---|---|---|---|
| 01 | `01-pytest.txt` | output `python -m pytest -q` | 33 test pass | CP0–CP4 |
| 02 | `02-log-validator.txt` | output `scripts/validate_logs.py` | 100/100, 0 PII leak | CP1 |
| 03 | `03-dashboard-validator.txt` | output `scripts/validate_dashboard.py` | 6/6 panel | CP2 |
| 04 | `04-structured-log.png` | terminal / `data/logs.jsonl` (`req-ab000201`) | JSON log có ts, event, correlation_id, model, env, feature, latency | CP1 |
| 05 | `05-pii-redaction.png` | terminal / `data/logs.jsonl` (`req-a11ce002`) | input giả → `[REDACTED_*]`, 0 chuỗi PII gốc trong log | CP1 |
| 06 | `06-trace-list.png` | Langfuse UI | project cá nhân, 31 trace gốc `day13-agent-request` | CP2 |
| 07 | `07-trace-waterfall.png` | Langfuse UI, trace `ef87b6b9…` | `lab-agent-run` → `retrieval` + `generation` (timeline) | CP2 |
| 08 | `08-trace-metadata.png` | Langfuse UI, span `generation` | correlation_id, model, prompt name/label/version, token, cost | CP2 |
| 09 | `09-prompt-versions.png` | Langfuse UI | `day13-chat` v1 (`production`,`baseline`), v2 (`latest`,`candidate`) | CP2 |
| 10 | `10-prompt-rollback.png` (+ `10a`, `10b`, `10c`) | Langfuse UI sau `manage_prompts.py promote/rollback` | production: v1 → v2 → v1 | CP2 |
| 11 | `11-dashboard-overview.png` | `scripts/dashboard.py` từ `data/logs.jsonl` | 6 panel có dữ liệu, time range, đơn vị, threshold | CP2 |
| 12 | `12-incident-metric.png` | `scripts/dashboard.py` (cửa sổ 05:28–05:32:51Z) | latency P95 ≈ 2665 ms trong challenge | CP3 |
| 13 | `13-incident-log.png` | terminal / `data/logs.jsonl` | `req-583d7b8f` latency 2660 ms + incident_enabled/disabled | CP3 |
| 14 | `14-incident-trace.png` | Langfuse UI, trace `b54dcfcd…` | span `retrieval` 2.50 s, `correlation_id=req-583d7b8f` | CP3 |

Ảnh Langfuse 07/08/14 được cắt (clip) phía trên dòng metadata `scope.attributes.public_key` do Langfuse tự thêm; không chỉnh sửa nội dung. Không có ảnh trang API Keys.