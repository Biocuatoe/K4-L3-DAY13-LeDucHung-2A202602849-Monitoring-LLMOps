# Alert Runbook — K4-L3B Day 13 Monitoring & LLMOps

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

---

## Alert 1: HighLatencyP95

- **Tên:** `HighLatencyP95`
- **Severity:** `warning`
- **Duration:** `5m`
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** latency P95 của `response_sent.latency_ms` (SLO: `fast_successful_requests`)
- **Điều kiện và thời gian duy trì:** `p95(latency_ms) > 2000ms` trong 5 phút (ngưỡng cảnh báo sớm, chặt hơn SLO 3000ms; rút ra từ challenge `rag_slow`: P95 = 2655ms vượt 2000ms nhưng chưa vượt SLO 3000ms)
- **Ảnh hưởng tới người dùng:** người dùng phải chờ hơn 2 giây để nhận câu trả lời thay vì trung bình < 200ms
- **Ba bước kiểm tra đầu tiên:**
  1. **Metrics →** Mở dashboard latency, xác nhận P95/P99 vượt ngưỡng 2000ms và thời gian duy trì ≥ 5 phút.
  2. **Logs →** Lọc `data/logs.jsonl` trong khoảng đó: `jq '. | select(.event == "response_sent" and .latency_ms > 2000)' data/logs.jsonl`. Lấy một `correlation_id` có `latency_ms` cao.
  3. **Traces →** Mở trace cùng `correlation_id` trên Langfuse, kiểm tra span `retrieval` và `generation` để xác định bước nào bất thường (retrieval chậm → RAG issue; generation chậm → LLM issue).
- **Mitigation tạm thời:**
  - Nếu generation span chậm: rollback prompt version về baseline, kiểm tra `LANGFUSE_PROMPT_LABEL`.
  - Nếu retrieval span chậm: tắt incident `rag_slow` nếu đang bật trong demo.
  - Nếu không xác định được: restart uvicorn, giảm tải.
- **Owner:** `student-2A202602849`

---

## Alert 2: ElevatedErrorRate

- **Tên:** `ElevatedErrorRate`
- **Severity:** `critical`
- **Duration:** `10m`
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** error rate từ `request_failed` / `request_received` (SLO: `fast_successful_requests`)
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 2%` trong 10 phút
- **Ảnh hưởng tới người dùng:** hơn 2% request trả về HTTP 500, người dùng không nhận được câu trả lời
- **Ba bước kiểm tra đầu tiên:**
  1. **Metrics →** Mở dashboard errors, xác nhận `error_rate_pct` > 2% và khoảng thời gian ≥ 10 phút.
  2. **Logs →** Lọc `data/logs.jsonl`: `jq '. | select(.event == "request_failed")' data/logs.jsonl`. Xác định `error_type` phổ biến nhất (`RuntimeError`, `TimeoutError`, v.v.).
  3. **Traces →** Lấy `correlation_id` từ log failed, mở trace trên Langfuse để xem span nào gây lỗi. Kiểm tra retrieval span có `tool_success=false`.
- **Mitigation tạm thời:**
  - Nếu `RuntimeError` từ retrieval: tắt incident `tool_fail`, kiểm tra vector store.
  - Nếu lỗi từ LLM generation: rollback prompt, restart uvicorn.
  - Escalate nếu không tự xử lý được sau 2 mitigation attempts.
- **Owner:** `student-2A202602849`

---

## Alert 3: DegradedRetrievalSuccess

- **Tên:** `DegradedRetrievalSuccess`
- **Severity:** `warning`
- **Duration:** `15m`
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** retrieval success rate từ `tool_success` field trong `response_sent` event (Guardrail: `retrieval_success_rate_pct_min: 90`)
- **Điều kiện và thời gian duy trì:** `retrieval_success_rate_pct < 90%` trong 15 phút
- **Ảnh hưởng tới người dùng:** retrieval thường xuyên thất bại hoặc trả về fallback, câu trả lời kém chất lượng do thiếu context
- **Ba bước kiểm tra đầu tiên:**
  1. **Metrics →** Mở dashboard errors panel, kiểm tra `tool_success_rate_pct` (nếu có) hoặc tính thủ công: `count(tool_success == true) / count(tool_success != null) * 100`.
  2. **Logs →** Lọc `data/logs.jsonl`: `jq '. | select(.tool_success == false)' data/logs.jsonl`. Xem xét patterns trong các query bị ảnh hưởng.
  3. **Traces →** Lấy `correlation_id` từ log retrieval fail, mở trace trên Langfuse. Kiểm tra retrieval span: có exception không? Latency retrieval có cao bất thường không?
- **Mitigation tạm thời:**
  - Tắt incident `tool_fail` nếu đang bật.
  - Kiểm tra corpus trong `app/mock_rag.py` — đảm bảo keywords phù hợp với query.
  - Nếu production: kiểm tra vector store connectivity, thử restart service.
- **Owner:** `student-2A202602849`
