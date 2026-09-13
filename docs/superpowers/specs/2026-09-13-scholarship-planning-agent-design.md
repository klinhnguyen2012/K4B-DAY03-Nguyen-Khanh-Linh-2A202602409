# Scholarship Planning Agent — Thiết kế hệ thống

## 1. Mục tiêu

Chuyển bài mẫu Trợ lý Học vụ thành Scholarship Planning Agent hỗ trợ học sinh và sinh viên:

- tra cứu hồ sơ cá nhân;
- tìm trường, chương trình và học bổng trong nước hoặc quốc tế;
- đối chiếu hồ sơ với điều kiện của từng học bổng;
- xác định thông tin, chứng chỉ và tài liệu còn thiếu;
- tạo checklist và timeline theo deadline;
- xử lý an toàn khi không tìm thấy hồ sơ hoặc dữ liệu học bổng.

Hệ thống phải chạy được với Mock Offline Provider để kiểm thử miễn phí và tiếp tục hỗ trợ Gemini/OpenAI thông qua native tool calling.

## 2. Phạm vi

Thay thế hai công cụ học vụ cũ bằng bốn công cụ học bổng:

1. `profile_query`
2. `scholarship_search`
3. `scholarship_details`
4. `study_plan_save`

Các thay đổi nằm trong `src/tools.py`, `src/providers.py`, `src/prompts.py`, `src/mcp_server.py` và `src/app.py`. Bộ dữ liệu là dữ liệu giả lập phục vụ bài Lab; hệ thống không tự kết nối website học bổng thật trong phạm vi này.

## 3. Tool schemas

### 3.1. `profile_query`

Tra cứu hồ sơ theo `student_id`.

- `student_id`: `string`, bắt buộc.
- Thành công: trả `status`, `student_id` và `data` gồm họ tên, GPA, thang điểm, chứng chỉ, hoạt động, bậc học, ngành mong muốn, khu vực, kỳ nhập học và nhu cầu tài chính.
- Không tìm thấy: trả `status = NOT_FOUND` và thông báo rõ ràng.

### 3.2. `scholarship_search`

Tìm lựa chọn theo mục tiêu học tập.

- `degree_level`: `string`, bắt buộc.
- `major`: `string`, bắt buộc.
- `regions`: mảng `string`, bắt buộc.
- `intake`: `string`, bắt buộc.
- `funding_need`: `string`, bắt buộc.
- Kết quả: danh sách học bổng có mã, trường, quốc gia, chương trình, mức hỗ trợ, kỳ nhập học và deadline.
- Nếu không có lựa chọn phù hợp: trả danh sách rỗng cùng thông báo; không tạo dữ liệu giả ngoài kho dữ liệu kiểm thử.

### 3.3. `scholarship_details`

Lấy điều kiện của một học bổng cụ thể.

- `scholarship_id`: `string`, bắt buộc.
- `intake`: `string`, bắt buộc.
- Kết quả: điều kiện GPA, ngoại ngữ, tài liệu, hoạt động, mức hỗ trợ, deadline và nguồn dữ liệu thử nghiệm.
- Mã hoặc kỳ nhập học không tồn tại: trả `NOT_FOUND`.

### 3.4. `study_plan_save`

Lưu checklist và timeline cho học bổng đã chọn.

- `student_id`: `string`, bắt buộc.
- `scholarship_id`: `string`, bắt buộc.
- `tasks`: mảng object, bắt buộc. Mỗi task có `title`, `due_date` và `priority`; `priority` chỉ nhận `high`, `medium`, `low`.
- Thành công: trả `status = SUCCESS`, `plan_id`, các mã liên quan, danh sách task và thông báo.
- Hồ sơ hoặc học bổng không tồn tại, task rỗng hoặc dữ liệu sai: trả trạng thái lỗi có giải thích.

## 4. Dữ liệu giả lập

Kho hồ sơ có ít nhất:

- `SV2026001`: hồ sơ hợp lệ để chạy TC02 và TC03;
- không chứa `SV9999999` để chạy TC05.

Kho học bổng có ít nhất:

- `HB_TEST_01`: dùng cho TC03, có kỳ nhập học, yêu cầu, tài liệu và deadline cụ thể;
- thêm các lựa chọn ngành Công nghệ thông tin ở Việt Nam và quốc tế để TC04 có kết quả so sánh;
- ít nhất một lựa chọn yêu cầu IELTS cao hơn hồ sơ mẫu để Agent chỉ ra khoảng thiếu.

Mọi tên học bổng và nguồn trong kho Mock phải được đánh dấu là dữ liệu thử nghiệm.

## 5. Luồng ReAct

Agent duy trì lịch sử hội thoại gồm yêu cầu người dùng, tool call và Observation. Sau mỗi tool call, kết quả được đưa lại cho provider để provider quyết định gọi công cụ tiếp theo hoặc trả lời cuối cùng. Vòng lặp dừng khi:

- provider trả văn bản cuối cùng;
- đạt `MAX_ITERATIONS`;
- xảy ra lỗi không thể tiếp tục.

Luồng theo test case:

- TC01: trả lời trực tiếp, không gọi tool.
- TC02: `profile_query` rồi tổng hợp hồ sơ.
- TC03: `profile_query → scholarship_details → study_plan_save → final answer`.
- TC04: nếu thiếu thông tin bắt buộc thì hỏi lại; khi đủ dữ liệu, chạy `scholarship_search → scholarship_details → final answer` và tạo timeline trong câu trả lời. Không tự lưu kế hoạch khi người dùng chưa yêu cầu lưu.
- TC05: `profile_query` trả `NOT_FOUND`, sau đó Agent yêu cầu người dùng cung cấp thông tin tối thiểu.

Mock Provider quyết định bước tiếp theo dựa trên câu hỏi và các Observation đã có. Gemini/OpenAI nhận cùng lịch sử để native tool calling có thể tiếp tục qua nhiều vòng.

## 6. Phân tích hồ sơ

Agent phân loại từng điều kiện thành:

- đáp ứng;
- chưa đáp ứng;
- thiếu dữ liệu để đánh giá.

Agent không tự quy đổi GPA khi nguồn không cung cấp quy tắc, không khẳng định người dùng chắc chắn nhận học bổng và không bịa deadline. Timeline phải được tạo từ deadline do `scholarship_details` trả về.

## 7. Xử lý lỗi

- Tool không tồn tại: trả `UNKNOWN_TOOL`.
- Thiếu hoặc sai tham số: trả `EXECUTION_ERROR` hoặc `INVALID_ARGUMENTS` với thông báo cụ thể.
- Không tìm thấy hồ sơ/học bổng: trả `NOT_FOUND`.
- Không có kết quả tìm kiếm: trả `SUCCESS` với danh sách rỗng và hướng dẫn điều chỉnh tiêu chí.
- MCP Server luôn đóng gói kết quả theo JSON-RPC 2.0.
- Khi hết số vòng lặp, Agent trả thông báo chưa thể hoàn tất thay vì im lặng hoặc tạo kết quả giả.

## 8. Waterfall trace

Mỗi bước lưu:

- số thứ tự bước;
- câu hỏi ban đầu;
- loại hành động;
- tên tool và arguments nếu có;
- Observation;
- câu trả lời cuối cùng nếu có;
- độ trễ đo thực tế của bước.

Trace không ghi API key và không dùng một giá trị độ trễ cố định để đại diện cho thời gian thực thi.

## 9. Tiêu chí nghiệm thu

- `TOOLS_SCHEMA` chứa đúng bốn tool mới và không còn hai tool học vụ cũ.
- Tool router thực thi được cả bốn tool.
- MCP Server trả kết quả JSON-RPC có `jsonrpc`, `server`, `tool` và `result`.
- Mock Provider gọi đúng tool và chạy được chuỗi nhiều bước của TC03.
- Năm câu hỏi trong `config/test_cases.json` đều được thực thi, không còn `TODO`.
- TC05 không bịa hồ sơ khi mã sinh viên không tồn tại.
- Trace ghi đủ các tool call và Observation của mỗi test case.
- Các kiểm tra cú pháp, schema, tool backend và test suite offline đều hoàn tất không lỗi.

## 10. Giới hạn

Dữ liệu trường và học bổng trong bài Lab là dữ liệu Mock, không đại diện cho thông tin tuyển sinh đang còn hiệu lực. Việc tìm kiếm dữ liệu thật, xác minh nguồn chính thức, nhắc việc tự động và nộp hồ sơ nằm ngoài phạm vi triển khai này.
