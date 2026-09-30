# Evidence manifest — Lê Đức Hùng (2A202602849)

Tất cả nguồn là output/ảnh sinh từ lần chạy thật trên code ở commit `6b69ca3`. Không có secret; dữ liệu PII chỉ là dữ liệu giả.

| # | File | Nguồn | Chứng minh | CP |
|---|---|---|---|---|
| 01 | `01-pytest.txt` | output `python -m pytest -q` | 33 test pass | CP0–CP4 |
| 02 | `02-log-validator.txt` | output `scripts/validate_logs.py` | 100/100, 0 PII leak | CP1 |
| 03 | `03-dashboard-validator.txt` | output `scripts/validate_dashboard.py` | 6/6 panel | CP2 |
| 04 | `04-structured-log.png` | terminal / `data/logs.jsonl` (`req-ab000101`) | JSON log có ts, event, correlation_id, model, env, feature, latency | CP1 |
| 05 | `05-pii-redaction.png` | terminal / `data/logs.jsonl` (`req-a11ce001`) | input giả → `[REDACTED_*]`, 0 chuỗi PII gốc trong log | CP1 |
| 06 | **thiếu** | Langfuse UI | danh sách ≥ 10 trace | CP2 |
| 07 | **thiếu** | Langfuse UI | waterfall root → retrieval + generation | CP2 |
| 08 | **thiếu** | Langfuse UI | metadata correlation_id/model/prompt/token/cost | CP2 |
| 09 | **thiếu** | Langfuse UI | prompt `day13-chat` v1/v2 + labels | CP2 |
| 10 | **thiếu** | Langfuse UI | production label trước/sau promote/rollback | CP2 |
| 11 | `11-dashboard-overview.png` | `scripts/dashboard.py` từ `data/logs.jsonl` | 6 panel có dữ liệu, time range, đơn vị, threshold | CP2 |
| 12 | `12-incident-metric.png` | `scripts/dashboard.py` (cửa sổ 05:05–05:12:36Z) | latency P95 2655 ms trong challenge | CP3 |
| 13 | `13-incident-log.png` | terminal / `data/logs.jsonl` | `req-d31dfb4b` latency 2653 ms + incident_enabled/disabled | CP3 |
| 14 | **thiếu** | Langfuse UI | trace `1ef3ab0695c05cacd5bec783d980ca2c` (`req-d31dfb4b`), span `retrieval` 2501 ms | CP3 |

## Chụp thủ công các ảnh còn thiếu (cần đăng nhập Langfuse, KHÔNG mở trang API Keys)
0. Đổi tên project thành `day13-k4-l3b-2A202602849` (Settings → General) để tên hiển thị trong ảnh.
1. 06: Tracing → Traces, lọc thời gian quanh 05:08–05:14Z (30/09/2026).
2. 07/08: mở trace `d9033d69b66c4975f390950b09208bdb` (baseline v1), xem tree và metadata/usage/cost.
3. 09/10: Prompts → `day13-chat` (v1 `baseline,production`; v2 `candidate`). Để có ảnh trước/sau, có thể chạy `python scripts/manage_prompts.py promote` rồi `rollback` và chụp trang Prompts sau mỗi lần; trace ID đã ghi trong REPORT §5.
4. 14: mở trace `1ef3ab0695c05cacd5bec783d980ca2c`, chọn span `retrieval` (2501 ms).