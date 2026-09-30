# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Lê Đức Hùng
- **MSSV:** _<điền MSSV thật khi nộp>_
- **Lớp:** K4-L3B
- **Repository URL:** _<điền URL repo cá nhân khi nộp>_
- **Commit SHA cuối:** _<sẽ điền ở CP4 sau khi đẩy repo cá nhân>_
- **Challenge ID:** _<Lab Coach gửi riêng tại CP3; KHÔNG tự tạo>_
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-<MSSV>` — _xem mục 10: chưa cấu hình local tại CP0 vì không có key/host thật trong môi trường này_

> Trung thực: MSSV / Repository URL / Commit SHA là metadata do chính học viên đặt khi tạo repo cá nhân. Báo cáo đang được khởi tạo trên repo đề bài để ghi lại kết quả thực tế từng checkpoint; mọi số liệu trong báo cáo chỉ phản ánh việc chạy trên máy này với `.env` chỉ chứa giá trị placeholder (không có Langfuse key thật).

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline (CP0) | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | **30/100** | _sẽ cập nhật ở CP1_ | Baseline thấp là đúng: `correlation_id="MISSING"` do `app/middleware.py` chưa wire-up (TODO CP1); thiếu enrichment `user_id_hash/session_id/feature/model`; PII scrubbing hiện pass vì input test chưa chứa email/điện thoại khớp pattern. Cần xóa `data/logs.jsonl` cũ rồi chạy lại sau khi sửa CP1. |
| `validate_dashboard.py` | **HỢP LỆ: 6/6 panel** | _giữ nguyên_ | Dashboard contract đúng ngay từ CP0 vì `config/dashboard.yaml` đã có đủ 6 panel (latency, traffic, errors, cost, tokens, quality) đúng schema và threshold. |
| `pytest` | **22 passed** | _sẽ cập nhật_ | Toàn bộ test public pass (test_dashboard_validator, test_validate_logs, test_chat_observability, test_tracing_adapter, test_challenge_config, test_pii, test_metrics, test_prompt_management, test_agent_prompt_trace, test_cli_windows_encoding). |
| Số traces hợp lệ | **0** | _sẽ cập nhật ở CP2_ | `tracing_enabled()=False` vì `.env` không có Langfuse key thật; chỉ có root observation giả do Langfuse SDK tự tạo fallback. Cần CP2 với project cá nhân để có trace thật. |
| Số PII leak | **0** trong baseline logs | _sẽ cập nhật_ | Validator báo 0 vì `payload` chỉ chứa `message_preview` rỗng hoặc ngắn không khớp regex. Sau CP1 phải gửi payload có email/phone để chứng minh scrubbing chạy đúng. |
| Latency P95 / TTFT P95 | **161 ms / 59 ms** (trên 10 request) | _sẽ cập nhật_ | Đo từ `/metrics` sau khi chạy `scripts/load_test.py` 1 lần. TTFT P95 = 59 ms (FakeLLM ngủ 50 ms). |
| Retrieval success rate | **100%** (10/10) | _sẽ cập nhật_ | Không bật incident `tool_fail`; retrieval corpus đủ match cho 10 query trong `data/sample_queries.jsonl`. |

> Ghi chú: "Kết quả cuối" sẽ được lấp đầy sau CP1, CP2, CP3. Bảng này là baseline trung thực của CP0, không dùng để đánh giá cuối cùng.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
- **Các metadata được ghi vào structured log:**
- **Cách bảo đảm PII được scrub trước khi ghi:**
- **Cách kiểm chứng kết quả:**

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
- **Cấu trúc root/retrieval/generation observations:**
- **Cách nối trace với log:**
- **Prompt name:**
- **Version/label baseline:**
- **Version/label candidate:**
- **Trace ID của mỗi version:**
- **Cách promote và rollback `production`:**

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
- **SLO và lý do chọn:**
- **Cách tính error budget:**
- **Ba alert và runbook tương ứng:**

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

## 10. CP0 — Setup và baseline (đã chạy thực tế trên máy này)

### 10.1 Môi trường đã chuẩn bị

- Hệ điều hành: Windows 10 build 19045 (PowerShell).
- Python: 3.12.10 (system). Lab khuyến nghị ≥ 3.11 — đạt.
- Virtual env: tạo bằng `python -m venv .venv` tại thư mục gốc; chưa commit (đã được `.gitignore` qua `.venv/`).
- Dependencies: cài bằng `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`. Kết quả: cài thành công 40 gói, bao gồm `fastapi 0.118.0`, `uvicorn 0.37.0`, `pydantic 2.11.4`, `structlog 25.4.0`, `langfuse 4.15.6`, `httpx 0.28.1`, `PyYAML 6.0.3`, `pytest 8.3.5`, `python-dotenv 1.1.0`.
- `.env`: tạo từ `.env.example` (lệnh `Copy-Item .env.example .env`); các giá trị `LANGFUSE_*` để trống theo mặc định. **Không có API key thật được commit/in vào `.env`**.

### 10.2 Lệnh đã chạy và kết quả thực

| Lệnh | Kết quả |
|---|---|
| `python -m venv .venv` | OK (exit 0). |
| `.\.venv\Scripts\python.exe -m pip install --upgrade pip` | OK; pip nâng lên 26.2.1. |
| `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` | OK; 40 packages. |
| `.\.venv\Scripts\python.exe -m pytest -q` | **22 passed in ~3.5–6.0s** (test_dashboard_validator, test_validate_logs, test_chat_observability, test_tracing_adapter, test_challenge_config, test_pii, test_metrics, test_prompt_management, test_agent_prompt_trace, test_cli_windows_encoding). |
| `.\.venv\Scripts\python.exe scripts/validate_dashboard.py` | **HỢP LỆ: 6/6 panel có trong dashboard contract.** |
| `.\.venv\Scripts\python.exe scripts/validate_logs.py` (chưa có log) | Lỗi: `data\logs.jsonl not found. Run the app and send some requests first.` — đúng kỳ vọng. |
| `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | Khởi động OK; `INFO: Uvicorn running on http://127.0.0.1:8000`. |
| `GET http://127.0.0.1:8000/health` | **HTTP 200** — `{"ok":true,"tracing_enabled":false,"incidents":{"rag_slow":false,"tool_fail":false,"cost_spike":false}}`. |
| `GET http://127.0.0.1:8000/metrics` | `{"traffic":10,"latency_p50":154.0,"latency_p95":161.0,"latency_p99":161.0,"ttft_p95":59.0,"avg_cost_usd":0.0022,"total_cost_usd":0.0221,"tokens_in_total":338,"tokens_out_total":1409,"error_breakdown":{},"quality_avg":0.88}` (sau 10 request từ load_test). |
| `.\.venv\Scripts\python.exe scripts/load_test.py` | 10 request, tất cả HTTP 200; `correlation_id` in ra đều là chuỗi `"MISSING"` (xác nhận `app/middleware.py` chưa wire TODO). File `data/logs.jsonl` được tạo (kích thước ~6.2 KB sau 1 lượt). |
| `.\.venv\Scripts\python.exe scripts/validate_logs.py` (sau load_test) | **Estimated Score: 30/100.** Missing required fields = 20, missing enrichment = 20, unique correlation IDs = 0, PII leaks = 0. Đây là baseline thật của CP0. |

### 10.3 Files đã thay đổi trong CP0

- Tạo mới: `.env` (chỉ chứa placeholder, không có key thật).
- Tạo mới: `.venv/` (đã được `.gitignore`).
- Tạo mới: `data/logs.jsonl` (đã được `.gitignore`).
- Snapshot baseline: `data/logs.cp0-baseline.jsonl` (bản sao của `logs.jsonl` ngay sau load_test CP0; **CHƯA commit**, giữ trong working tree để so sánh với logs sau CP1). Bước này chỉ để đối chiếu; nếu muốn giữ sạch working tree có thể xóa sau CP1 vì validator đọc `data/logs.jsonl`.
- Cập nhật: `submission/REPORT.md` (mục 1, mục 3, mục 10) để ghi lại baseline trung thực.

### 10.4 `.gitignore` đã bảo vệ

Kiểm tra nội dung hiện tại (không sửa, chỉ xác nhận):

```text
.venv/
__pycache__/
*.pyc
.DS_Store
data/logs.jsonl
data/audit.jsonl
.env
config/challenge.json
.pytest_cache/
.antigravity/
```

Đủ che `.env`, `data/logs.jsonl`, `data/audit.jsonl`, `config/challenge.json`, virtual environment và cache theo yêu cầu CP0.

### 10.5 Blocker / việc cần con người xử lý

1. **Chưa có Langfuse Cloud project cá nhân**: máy này không có `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` thật. Hệ quả trung thực:
   - `GET /health` trả `"tracing_enabled": false`.
   - `scripts/validate_logs.py` báo 0 unique correlation ID vì middleware vẫn đặt `"MISSING"`.
   - Không có trace thật trên Langfuse để dẫn evidence. → CP2 sẽ tạo evidence khi có key thật.
2. **Không có `config/challenge.json`** vì Lab Coach chưa release; CP3 phải chờ.
3. **Port 8000 từng bị chiếm** bởi PID 12820 (process đã chết nhưng socket chưa được kernel giải phóng). Đã xử lý bằng `taskkill /F /PID 12820` (lúc đầu fail vì process không tồn tại); sau khi socket hết TIME_WAIT, restart uvicorn thành công trên cổng 8000 — đây là blocker vận hành, không phải lỗi code.

### 10.6 Đánh giá trung thực CP0

- **CP0 hoàn thành đúng nghĩa "setup + baseline":** môi trường cài đặt được, app chạy được, `/health` ok, log được tạo, cả ba public validator chạy được, baseline được ghi lại trong mục 3 và mục 10 của báo cáo này.
- **CP0 KHÔNG đòi hỏi** điểm validator cao. Việc `validate_logs.py` chỉ đạt 30/100 là **đúng baseline** vì CP1 chưa wire correlation ID, enrichment và scrubber. Repo có sẵn các TODO dành cho CP1, CP2. Không sửa code để "nâng điểm" baseline vì đó là gian lận.
- **Các bước tiếp theo** (ngoài phạm vi của PROMPT 0): CP1 (correlation ID + PII), CP2 (trace + prompt + dashboard), CP3 (challenge chính thức), CP4 (evidence + report cuối). Mỗi checkpoint sẽ được cập nhật trong file này với số liệu thật và evidence cá nhân.
