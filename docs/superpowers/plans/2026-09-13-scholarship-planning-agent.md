# Scholarship Planning Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển starter project học vụ thành Scholarship Planning Agent chạy được cả 5 test case với bốn MCP tool và ReAct loop nhiều bước.

**Architecture:** `src/tools.py` sở hữu schema và dữ liệu Mock; `src/mcp_server.py` đóng gói mọi tool result theo JSON-RPC 2.0. Provider nhận lịch sử Observation để chọn hành động tiếp theo; `src/app.py` duy trì vòng lặp cho tới final answer hoặc giới hạn bước và ghi trace cho từng sự kiện.

**Tech Stack:** Python 3.10–3.12, `unittest`, JSON Schema dạng dictionary, Google GenAI SDK, OpenAI SDK, python-dotenv.

## Global Constraints

- Công bố đúng bốn tool: `profile_query`, `scholarship_search`, `scholarship_details`, `study_plan_save`.
- Dữ liệu học bổng trong Mock phải ghi rõ là dữ liệu thử nghiệm.
- Không bịa hồ sơ, điều kiện hoặc deadline khi tool không trả dữ liệu.
- Không ghi API key vào trace hoặc Git.
- Giữ hỗ trợ Mock Offline, Gemini và OpenAI.
- Giới hạn vòng lặp bằng `MAX_ITERATIONS` và trả kết luận rõ ràng khi hết bước.

---

### Task 1: Tool schemas và backend học bổng

**Files:**
- Create: `tests/test_scholarship_agent.py`
- Modify: `src/tools.py`

**Interfaces:**
- Produces: `TOOLS_SCHEMA`, `execute_profile_query(student_id)`, `execute_scholarship_search(degree_level, major, regions, intake, funding_need)`, `execute_scholarship_details(scholarship_id, intake)`, `execute_study_plan_save(student_id, scholarship_id, tasks)`, `dispatch_tool_call(tool_name, arguments)`.
- Return format: mọi executor trả JSON string có trường `status`; dispatcher giữ giao diện hiện tại.

- [ ] **Step 1: Viết kiểm tra thất bại cho schema và tool backend**

```python
class ToolBackendTests(unittest.TestCase):
    def test_tool_registry_contains_four_scholarship_tools(self):
        self.assertEqual(
            {tool["name"] for tool in TOOLS_SCHEMA},
            {"profile_query", "scholarship_search", "scholarship_details", "study_plan_save"},
        )

    def test_profile_query_success_and_not_found(self):
        success = json.loads(dispatch_tool_call("profile_query", {"student_id": "SV2026001"}))
        missing = json.loads(dispatch_tool_call("profile_query", {"student_id": "SV9999999"}))
        self.assertEqual(success["status"], "SUCCESS")
        self.assertIn("gpa_scale", success["data"])
        self.assertEqual(missing["status"], "NOT_FOUND")

    def test_search_details_and_plan_save(self):
        search = json.loads(dispatch_tool_call("scholarship_search", {
            "degree_level": "Thạc sĩ", "major": "Công nghệ thông tin",
            "regions": ["Việt Nam", "Quốc tế"], "intake": "2027",
            "funding_need": "Hỗ trợ học phí",
        }))
        details = json.loads(dispatch_tool_call("scholarship_details", {
            "scholarship_id": "HB_TEST_01", "intake": "2027",
        }))
        saved = json.loads(dispatch_tool_call("study_plan_save", {
            "student_id": "SV2026001", "scholarship_id": "HB_TEST_01",
            "tasks": [{"title": "Thi IELTS", "due_date": "2026-11-30", "priority": "high"}],
        }))
        self.assertGreaterEqual(len(search["data"]), 1)
        self.assertEqual(details["status"], "SUCCESS")
        self.assertEqual(saved["status"], "SUCCESS")
```

- [ ] **Step 2: Chạy kiểm tra và xác nhận thất bại vì tool mới chưa tồn tại**

Run: `python3 -m unittest tests.test_scholarship_agent.ToolBackendTests -v`

Expected: FAIL do registry vẫn chứa `academic_query` và `schedule_appointment`.

- [ ] **Step 3: Thay schema và backend bằng bốn tool mới**

Tạo hồ sơ `SV2026001`, học bổng `HB_TEST_01` và ít nhất hai lựa chọn CNTT. Thêm kiểm tra tham số rỗng, danh sách task rỗng, priority không hợp lệ, hồ sơ/học bổng không tồn tại. Trả `INVALID_ARGUMENTS`, `NOT_FOUND`, `SUCCESS` hoặc `UNKNOWN_TOOL` theo thiết kế.

- [ ] **Step 4: Chạy kiểm tra backend**

Run: `python3 -m unittest tests.test_scholarship_agent.ToolBackendTests -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tools.py tests/test_scholarship_agent.py
git commit -m "feat: add scholarship planning tools"
```

### Task 2: MCP JSON-RPC dispatcher

**Files:**
- Modify: `tests/test_scholarship_agent.py`
- Modify: `src/mcp_server.py`

**Interfaces:**
- Consumes: `dispatch_tool_call(tool_name, arguments) -> str`.
- Produces: `MCPScholarshipServer.call_tool(tool_name, arguments) -> dict` có `jsonrpc`, `server`, `tool`, `result`.

- [ ] **Step 1: Viết kiểm tra thất bại cho MCP envelope**

```python
class MCPServerTests(unittest.TestCase):
    def test_call_tool_wraps_result_as_json_rpc(self):
        server = MCPScholarshipServer()
        response = server.call_tool("profile_query", {"student_id": "SV2026001"})
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["server"], "scholarship-planning-mcp-server")
        self.assertEqual(response["tool"], "profile_query")
        self.assertEqual(response["result"]["status"], "SUCCESS")
```

- [ ] **Step 2: Chạy kiểm tra và xác nhận thất bại vì server hiện trả `{}`**

Run: `python3 -m unittest tests.test_scholarship_agent.MCPServerTests -v`

Expected: FAIL khi truy cập `response["jsonrpc"]`.

- [ ] **Step 3: Triển khai và đổi tên server**

Đổi lớp thành `MCPScholarshipServer`, tên mặc định thành `scholarship-planning-mcp-server`; gọi dispatcher, `json.loads()` kết quả và đóng gói JSON-RPC. Cập nhật smoke test trong `__main__` để gọi `profile_query` và kiểm tra bốn schema.

- [ ] **Step 4: Chạy kiểm tra MCP**

Run: `python3 -m unittest tests.test_scholarship_agent.MCPServerTests -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/mcp_server.py tests/test_scholarship_agent.py
git commit -m "feat: dispatch scholarship tools through MCP"
```

### Task 3: Prompt và provider nhiều bước

**Files:**
- Modify: `tests/test_scholarship_agent.py`
- Modify: `src/prompts.py`
- Modify: `src/providers.py`

**Interfaces:**
- Produces: `generate_with_tools(prompt, tools_schema, system_prompt="", observations=None)` cho cả ba provider.
- `observations`: danh sách dictionary gồm `tool_name`, `arguments`, `result`.

- [ ] **Step 1: Viết kiểm tra thất bại cho quyết định của Mock Provider**

```python
class MockProviderTests(unittest.TestCase):
    def test_tc03_calls_tools_in_order(self):
        provider = MockOfflineProvider()
        prompt = "Dùng hồ sơ sinh viên SV2026001 và học bổng thử nghiệm HB_TEST_01 đã chọn, hãy tạo checklist."
        first = provider.generate_with_tools(prompt, TOOLS_SCHEMA, observations=[])
        second = provider.generate_with_tools(prompt, TOOLS_SCHEMA, observations=[{"tool_name": "profile_query", "result": {"status": "SUCCESS"}}])
        third = provider.generate_with_tools(prompt, TOOLS_SCHEMA, observations=[
            {"tool_name": "profile_query", "result": {"status": "SUCCESS"}},
            {"tool_name": "scholarship_details", "result": {"status": "SUCCESS", "data": {"deadline": "2027-01-31"}}},
        ])
        self.assertEqual(first["tool_name"], "profile_query")
        self.assertEqual(second["tool_name"], "scholarship_details")
        self.assertEqual(third["tool_name"], "study_plan_save")

    def test_tc05_finishes_after_not_found(self):
        response = MockOfflineProvider().generate_with_tools(
            "Tra cứu SV9999999 và đề xuất học bổng", TOOLS_SCHEMA,
            observations=[{"tool_name": "profile_query", "result": {"status": "NOT_FOUND"}}],
        )
        self.assertEqual(response["type"], "text")
        self.assertIn("không tìm thấy", response["content"].lower())

    # TC04: hồ sơ nhập trực tiếp phải tìm rồi đọc chi tiết học bổng.
    def test_tc04_searches_then_reads_scholarship_details(self):
        provider = MockOfflineProvider()
        prompt = "GPA 3.5/4.0, IELTS 6.0, học thạc sĩ CNTT trong nước hoặc quốc tế, cần hỗ trợ học phí."
        first = provider.generate_with_tools(prompt, TOOLS_SCHEMA, observations=[])
        second = provider.generate_with_tools(prompt, TOOLS_SCHEMA, observations=[
            {"tool_name": "scholarship_search", "result": {
                "status": "SUCCESS", "data": [{"scholarship_id": "HB_TEST_01"}],
            }},
        ])
        self.assertEqual(first["tool_name"], "scholarship_search")
        self.assertEqual(second["tool_name"], "scholarship_details")
```

- [ ] **Step 2: Chạy kiểm tra và xác nhận thất bại do provider chưa nhận Observation**

Run: `python3 -m unittest tests.test_scholarship_agent.MockProviderTests -v`

Expected: FAIL vì chữ ký hàm chưa có `observations` và tool name còn thuộc bài học vụ.

- [ ] **Step 3: Cập nhật prompt và provider**

Prompt mô tả vai trò học bổng, bốn tool, quy tắc đối chiếu và chống bịa dữ liệu. Mock Provider hỗ trợ chính xác luồng TC01–TC05. Gemini/OpenAI nối Observation vào nội dung prompt dạng JSON để mô hình chọn tool kế tiếp; giữ schema native tool calling hiện tại.

- [ ] **Step 4: Chạy kiểm tra provider**

Run: `python3 -m unittest tests.test_scholarship_agent.MockProviderTests -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/prompts.py src/providers.py tests/test_scholarship_agent.py
git commit -m "feat: guide scholarship tool decisions"
```

### Task 4: ReAct loop, trace và test suite hoàn chỉnh

**Files:**
- Modify: `tests/test_scholarship_agent.py`
- Modify: `src/app.py`
- Verify: `config/test_cases.json`
- Generate: `docs/trace_waterfall.json`

**Interfaces:**
- Consumes: `MCPScholarshipServer`, provider `generate_with_tools(..., observations=list)`.
- Produces: `run_react_agent(user_query, provider, mcp_server) -> list[dict]` với nhiều `TOOL_EXECUTION` và một `FINAL_ANSWER`.

- [ ] **Step 1: Viết kiểm tra thất bại cho chuỗi TC03 và TC05**

```python
class ReactLoopTests(unittest.TestCase):
    def test_tc03_records_three_tool_calls_and_final_answer(self):
        traces = run_react_agent(TEST_CASES[2]["question"], MockOfflineProvider(), MCPScholarshipServer())
        actions = [trace.get("tool_name") for trace in traces if trace["action_type"] == "TOOL_EXECUTION"]
        self.assertEqual(actions, ["profile_query", "scholarship_details", "study_plan_save"])
        self.assertEqual(traces[-1]["action_type"], "FINAL_ANSWER")

    def test_tc05_does_not_invent_missing_profile(self):
        traces = run_react_agent(TEST_CASES[4]["question"], MockOfflineProvider(), MCPScholarshipServer())
        self.assertEqual(traces[0]["observation"]["status"], "NOT_FOUND")
        self.assertIn("không tìm thấy", traces[-1]["output"].lower())
```

- [ ] **Step 2: Chạy kiểm tra và xác nhận thất bại vì loop dừng sau tool đầu tiên**

Run: `python3 -m unittest tests.test_scholarship_agent.ReactLoopTests -v`

Expected: FAIL vì chỉ có một `TOOL_EXECUTION`.

- [ ] **Step 3: Triển khai vòng lặp Observation**

Khởi tạo `observations = []`; truyền vào provider mỗi vòng; sau tool call, thêm `{tool_name, arguments, result}` rồi tiếp tục vòng lặp. Chỉ tạo `FINAL_ANSWER` khi provider trả text. Khi hết bước, thêm câu trả lời giới hạn rõ ràng. Đo latency riêng cho provider và tool thay vì gán `10.0` cố định. Đổi tên và nội dung CLI sang Scholarship Planning Agent.

- [ ] **Step 4: Chạy kiểm tra đơn vị và bộ 5 test case offline**

Run: `python3 -m unittest discover -s tests -v`

Expected: toàn bộ test PASS.

Run: `LLM_PROVIDER=mock python3 src/app.py --all`

Expected: `Đã thực thi 5/5 Test Cases`, `0 Test Cases đang chờ điền câu hỏi`; trace chứa tool calls của TC02–TC05 và chuỗi ba tool của TC03.

- [ ] **Step 5: Kiểm tra artifact và code cũ**

Run: `python3 -m json.tool config/test_cases.json >/dev/null && python3 -m json.tool docs/trace_waterfall.json >/dev/null`

Run: `rg -n "academic_query|schedule_appointment|Trợ lý Học vụ|TODO 1.2|TODO 2.1" src config/test_cases.json`

Expected: JSON hợp lệ; lệnh `rg` không tìm thấy nội dung nghiệp vụ cũ trong phạm vi triển khai.

- [ ] **Step 6: Commit**

```bash
git add src/app.py tests/test_scholarship_agent.py docs/trace_waterfall.json config/test_cases.json
git commit -m "feat: run scholarship agent test suite"
```

### Task 5: Đồng bộ báo cáo nghiệm thu offline

**Files:**
- Modify: `docs/trace_eval.md`

**Interfaces:**
- Consumes: kết quả `LLM_PROVIDER=mock python3 src/app.py --all` và `docs/trace_waterfall.json`.
- Produces: báo cáo không còn mô tả code hiện tại là bài mẫu học vụ; vẫn ghi rõ trace offline không thay thế bằng chứng API thật.

- [ ] **Step 1: Cập nhật số liệu và đoạn trace**

Thay đoạn trace học vụ cũ bằng một chuỗi tiêu biểu của TC03; ghi 5/5 test case đã thực thi offline, số lượt tool thành công đếm trực tiếp từ trace và trạng thái API thật vẫn chưa xác minh.

- [ ] **Step 2: Kiểm tra tính nhất quán**

Run: `rg -n "academic_query|schedule_appointment|TODO 1.2|TODO 2.1" docs/trace_eval.md`

Expected: chỉ còn lịch sử/bối cảnh nếu cần giải thích; không mô tả chúng là implementation hiện tại.

Run: `git diff --check`

Expected: không có lỗi whitespace.

- [ ] **Step 3: Chạy lại toàn bộ verification**

Run: `python3 -m unittest discover -s tests -v && LLM_PROVIDER=mock python3 src/app.py --all`

Expected: test PASS và test suite thực thi 5/5.

- [ ] **Step 4: Commit**

```bash
git add docs/trace_eval.md docs/trace_waterfall.json
git commit -m "docs: record scholarship agent offline evaluation"
```
