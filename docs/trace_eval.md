# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Khánh Linh
>
> **Mã Sinh Viên / Mã Học viên:** 2A202602409
>
> **Chủ đề Lựa chọn:** Đề tài mở — Scholarship Planning Agent (Trợ lý tìm kiếm học bổng và lập kế hoạch chuẩn bị hồ sơ)
>
> **Ngày cập nhật báo cáo:** 13/09/2026

**Mô tả đề tài:** Scholarship Planning Agent hỗ trợ học sinh/sinh viên tìm kiếm học bổng và trường phù hợp trong nước hoặc quốc tế dựa trên hồ sơ cá nhân. Agent phân tích GPA, chứng chỉ ngoại ngữ, hoạt động ngoại khóa và mục tiêu học tập; đối chiếu điều kiện tuyển sinh để xác định yêu cầu còn thiếu. Từ đó, hệ thống đề xuất học bổng, chương trình hoặc hoạt động cần chuẩn bị, đồng thời tạo checklist và timeline cá nhân hóa theo từng hạn nộp hồ sơ.

**Phạm vi báo cáo:** Phần thiết kế và kế hoạch kiểm thử dưới đây áp dụng cho Scholarship Planning Agent. Phần nghiệm thu phản ánh đúng bằng chứng đang có trong repository: trace của bài mẫu học vụ, có phản hồi Mock và chưa có kết quả tra cứu thành công. Các công cụ và tình huống học bổng được ghi rõ là đề xuất, chưa phải chức năng đã triển khai hoặc kiểm thử đạt.

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 5 / 5 | Agent cần thu thập và kiểm tra hồ sơ, xác định mục tiêu, tìm trường/học bổng, đối chiếu điều kiện, phân tích thiếu hụt rồi lập kế hoạch. Các bước phụ thuộc nhau: chỉ có thể đề xuất lịch thi chứng chỉ sau khi biết yêu cầu đầu vào và hạn nộp của chương trình. |
| **2. Tool Interaction** | 5 / 5 | Để tư vấn có căn cứ, Agent cần công cụ đọc hồ sơ, tra cứu dữ liệu trường/học bổng và lấy điều kiện, deadline từ nguồn chính thức. Công cụ có thể được cung cấp qua MCP Server; việc lưu checklist và cập nhật tiến độ cần kho dữ liệu kế hoạch. LLM đơn thuần không đủ để bảo đảm thông tin tuyển sinh còn hiệu lực. |
| **3. Dynamic Decision** | 5 / 5 | Bước tiếp theo thay đổi theo kết quả tra cứu: thiếu thang điểm GPA thì hỏi bổ sung; chứng chỉ chưa đạt thì lập kế hoạch cải thiện; deadline đã qua thì tìm đợt khác; không có lựa chọn phù hợp thì đề xuất điều chỉnh phạm vi tìm kiếm để người dùng quyết định. Agent phải dựa vào Observation thay vì thực hiện một chuỗi cố định. |
| **4. Long Horizon Goal** | 4 / 5 | Mục tiêu chuẩn bị hồ sơ thường kéo dài nhiều tháng, gồm thi chứng chỉ, bổ sung hoạt động, xin thư giới thiệu và hoàn thiện bài luận. Agent cần lưu mục tiêu, deadline và trạng thái công việc giữa các lần người dùng quay lại. Chấm 4 điểm vì phạm vi ban đầu là hỗ trợ lập/cập nhật kế hoạch; chưa bao gồm tự theo dõi liên tục hoặc tự nộp hồ sơ. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19 / 20** | **19 > 12:** Bài toán rất phù hợp triển khai Agentic System vì có suy luận nhiều bước, sử dụng công cụ, quyết định theo dữ liệu và mục tiêu dài hạn. Điểm này đánh giá độ phù hợp của đề tài, không phải điểm nghiệm thu sản phẩm. |

### 1.1. Đầu vào và đầu ra dự kiến

**Đầu vào:** Bậc học hiện tại và bậc học muốn ứng tuyển; GPA kèm thang điểm; ngành học; chứng chỉ và ngày hết hạn; hoạt động ngoại khóa, thành tích, kinh nghiệm; quốc gia/khu vực mong muốn; kỳ nhập học; ngân sách và mức hỗ trợ cần có. Thông tin quốc tịch hoặc cư trú chỉ cần thu thập khi liên quan đến điều kiện học bổng.

**Đầu ra:** Danh sách trường, chương trình và học bổng phù hợp kèm nguồn, thời điểm tra cứu, điều kiện và deadline; bảng so sánh yêu cầu với hồ sơ; danh sách việc cần bổ sung; checklist và timeline theo từng lựa chọn. Mỗi gợi ý phải giải thích vì sao phù hợp và còn thiếu điều gì. Đáp ứng điều kiện tối thiểu không đồng nghĩa chắc chắn được nhận học bổng.

### 1.2. Luồng xử lý và công cụ đề xuất

Các công cụ sau là thiết kế cho đề tài, **chưa được khai báo trong `src/tools.py` hiện tại**.

| Bước | Công cụ / xử lý đề xuất | Kết quả cần có |
| :--- | :--- | :--- |
| 1. Đọc và xác thực hồ sơ | `profile_query(student_id)` | Hồ sơ có GPA và thang điểm, chứng chỉ, hoạt động, mục tiêu; liệt kê trường còn thiếu. Nếu không tìm thấy hồ sơ, yêu cầu người dùng cung cấp thông tin. |
| 2. Tìm lựa chọn ban đầu | `scholarship_search(degree, major, regions, intake, funding_need)` | Danh sách chương trình/học bổng cùng trường, mức hỗ trợ và đường dẫn nguồn chính thức. |
| 3. Lấy điều kiện cụ thể | `scholarship_details(scholarship_id, intake)` | Điều kiện của đúng kỳ tuyển sinh, hồ sơ bắt buộc, deadline kèm múi giờ và ngày kiểm tra nguồn. Phân biệt hạn nhập học với hạn học bổng. |
| 4. Phân tích mức phù hợp | Agent đối chiếu hồ sơ với dữ liệu công cụ | Phân loại: đáp ứng điều kiện đã xác minh, cần bổ sung, không đáp ứng, hoặc chưa đủ dữ liệu. Không tự quy đổi GPA nếu chưa có quy tắc của đơn vị tuyển sinh. |
| 5. Lập kế hoạch | `study_plan_save(student_id, scholarship_id, tasks)` | Checklist được lưu với thời hạn, trạng thái, phụ thuộc giữa các việc và tiêu chí hoàn thành. Chỉ thông báo đã lưu khi công cụ trả về thành công. |
| 6. Cập nhật tiến độ | `study_plan_update(plan_id, task_id, status)` | Kế hoạch được điều chỉnh theo việc đã hoàn thành, kết quả thi mới hoặc thay đổi deadline đã xác minh. |

**Cách vận hành ReAct dự kiến:** Agent chọn công cụ phù hợp, nhận Observation rồi quyết định hành động tiếp theo. Ví dụ, nếu nguồn tuyển sinh yêu cầu chứng chỉ cao hơn mức hiện có, Agent xác định khoảng thiếu và kiểm tra thời gian còn lại trước khi đưa việc ôn/thi vào kế hoạch. Khi công cụ lỗi hoặc dữ liệu thiếu, Agent phải nêu phần chưa xác minh; không tự tạo điều kiện, học bổng hay deadline để lấp chỗ trống.

### 1.3. Checklist và timeline cá nhân hóa mẫu

Ví dụ giả định: một sinh viên có GPA 3,5/4,0, IELTS 6,0, đã tham gia câu lạc bộ, muốn tìm học bổng thạc sĩ ngành Công nghệ thông tin. Giả sử một chương trình trong bộ dữ liệu thử nghiệm yêu cầu IELTS 6,5 và hai thư giới thiệu. Đây là **dữ liệu minh họa**, không phải điều kiện của một học bổng thực tế; cần kiểm tra thêm yêu cầu điểm thành phần, hạn chứng chỉ và các điều kiện khác trước khi đánh giá đủ điều kiện.

Gọi **D** là deadline đã xác minh của hồ sơ đang xét. Các mốc sau là kế hoạch đề xuất, được điều chỉnh theo thời gian thực tế còn lại và lịch công bố kết quả thi.

| Mốc chuẩn bị | Công việc | Tiêu chí hoàn thành |
| :--- | :--- | :--- |
| D − 6 tháng | Xác định ngành, quốc gia, ngân sách; lập danh sách trường/học bổng | Mỗi lựa chọn có nguồn chính thức, kỳ tuyển sinh và điều kiện cần kiểm tra. |
| D − 5 tháng | Đánh giá ngoại ngữ; lên lịch ôn và thi | Có mục tiêu điểm, lịch học, ngày thi và ngày dự kiến nhận kết quả trước hạn yêu cầu. |
| D − 4 tháng | Bổ sung dự án hoặc hoạt động liên quan đến ngành | Có vai trò, kết quả và minh chứng cụ thể; không tham gia chỉ để tăng số lượng hoạt động. |
| D − 3 tháng | Chuẩn bị CV, bảng điểm; liên hệ người viết thư giới thiệu | Có bản CV, bảng điểm theo yêu cầu và xác nhận hỗ trợ từ người viết thư. |
| D − 2 tháng | Viết bài luận, hoàn thiện minh chứng; nhận kết quả chứng chỉ | Có bản nháp bài luận và kết quả ngoại ngữ; đánh giá lại mức phù hợp nếu chưa đạt. |
| D − 1 tháng | Rà soát hồ sơ theo từng chương trình | Đủ tài liệu bắt buộc, đúng định dạng, ngôn ngữ và yêu cầu chứng thực nếu có. |
| D − 7 ngày | Kiểm tra lần cuối và chủ động nộp sớm | Người dùng kiểm tra thông tin, nộp hồ sơ và lưu xác nhận tiếp nhận. |
| Sau khi nộp | Theo dõi yêu cầu bổ sung hoặc phỏng vấn | Cập nhật trạng thái, lịch phỏng vấn và hạn phản hồi vào kế hoạch. |

Checklist cá nhân hóa tương ứng:

- [ ] Xác nhận GPA kèm thang điểm và yêu cầu của từng chương trình.
- [ ] Xác minh mức hỗ trợ, chi phí còn lại và deadline kèm múi giờ.
- [ ] Đạt yêu cầu ngoại ngữ và bảo đảm chứng chỉ còn hiệu lực theo quy định.
- [ ] Hoàn thiện CV và minh chứng dự án/hoạt động phù hợp.
- [ ] Chuẩn bị bảng điểm, bằng cấp và bản dịch/chứng thực nếu được yêu cầu.
- [ ] Hoàn thành bài luận đúng đề, giới hạn độ dài và tiêu chí của chương trình.
- [ ] Có đủ thư giới thiệu và theo dõi hạn gửi riêng của người giới thiệu.
- [ ] Kiểm tra hồ sơ, nộp trước hạn và lưu xác nhận.

Nếu thời gian còn lại ngắn hơn kế hoạch mẫu, Agent phải tính lại tính khả thi, ưu tiên tài liệu bắt buộc và đề xuất đợt tiếp theo khi cần. Mỗi học bổng có deadline riêng; hệ thống cần gom các việc dùng chung và giữ riêng các yêu cầu đặc thù.

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

### 2.1. Bằng chứng hiện có

File [`trace_waterfall.json`](trace_waterfall.json) hiện chứa **3 sự kiện của 2 câu hỏi mẫu học vụ**: 2 `FINAL_ANSWER` và 1 `TOOL_EXECUTION`. Phản hồi của câu hỏi đầu có nhãn `[Mock Agent Response]`. File không ghi metadata xác nhận provider/model hoặc một lượt chạy API thật; vì vậy **chưa đủ bằng chứng nghiệm thu LLM API thật cho Scholarship Planning Agent**.

Đoạn sau được trích nguyên dữ liệu từ hai sự kiện cuối của file hiện có; đây là **trace bài mẫu chưa hoàn thiện**, không phải log học bổng đã chạy thành công:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {},
    "latency_ms": 799.12
  },
  {
    "step": 2,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Chưa thể trả lời chi tiết do chưa nhận được dữ liệu từ MCP Server (hãy hoàn thành TODO 2.1).",
    "latency_ms": 10.0
  }
]
```

### 2.2. Nhận xét trace và giới hạn hiện tại

- **Action:** Có một yêu cầu gọi `academic_query` với `student_id = SV2026001`, phù hợp với câu hỏi tra cứu trong bài mẫu.
- **Observation:** Kết quả là `{}`, chưa có dữ liệu hồ sơ hoặc trạng thái `SUCCESS`. Kiểm tra `src/mcp_server.py` cho thấy `call_tool()` hiện trả về `{}` ở phần chưa hoàn thiện.
- **Final Answer:** Nội dung đầu ra thông báo chưa nhận được dữ liệu. Trường `thought` nói “thành công” là chuỗi cố định trong mã nguồn, không chứng minh tool thực thi thành công.
- **Độ trễ:** Giữ nguyên các số liệu trong trace. Trong `src/app.py`, thời gian ở sự kiện tool được đo quanh lời gọi provider, còn `10.0` ở câu trả lời sau tool là giá trị cố định; chưa thể dùng chúng để kết luận thời gian thực thi MCP hoặc tổng độ trễ thực tế.
- **Luồng nhiều bước:** Mã hiện tại kết thúc sau một lần gọi tool và tổng hợp câu trả lời bằng mã Python. Cần bổ sung bước đưa Observation trở lại LLM để tiếp tục tra cứu, so sánh và lập kế hoạch học bổng qua nhiều công cụ.

### 2.3. Bộ 5 tình huống kiểm thử đề xuất cho Scholarship Planning Agent

Đây là kế hoạch kiểm thử trong báo cáo, **chưa được thực thi và chưa thay thế `config/test_cases.json`**. Cấu hình hiện tại vẫn là bài mẫu học vụ, trong đó TC03–TC05 chưa có câu hỏi hoàn chỉnh.

| Mã | Câu hỏi kiểm thử đề xuất | Hành vi và tiêu chí đạt | Trạng thái |
| :--- | :--- | :--- | :--- |
| TC01 — Hỏi đáp trực tiếp | “Scholarship Planning Agent hỗ trợ em những gì và em cần cung cấp thông tin nào?” | Giải thích khả năng hỗ trợ và thông tin đầu vào; không gọi tool khi chỉ giới thiệu chức năng; không khẳng định học bổng cụ thể còn mở. | Chưa chạy |
| TC02 — Tra cứu hồ sơ | “Hãy tra cứu hồ sơ của em với mã SV2026001 và liệt kê dữ liệu đã có để chuẩn bị tìm học bổng.” | Gọi `profile_query` đúng mã; trình bày chính xác dữ liệu trả về và chỉ rõ trường còn thiếu; không tự suy diễn thang GPA, chứng chỉ hoặc mục tiêu. | Chưa chạy |
| TC03 — Tạo kế hoạch | “Dùng hồ sơ và học bổng thử nghiệm HB_TEST_01 đã chọn, hãy tạo và lưu checklist chuẩn bị hồ sơ theo deadline của chương trình.” | Lấy hồ sơ và chi tiết học bổng; tạo công việc có hạn, phụ thuộc và tiêu chí hoàn thành; gọi `study_plan_save` đúng dữ liệu; chỉ xác nhận lưu sau `SUCCESS`. | Chưa chạy |
| TC04 — Suy luận nhiều bước | “Em có GPA 3,5/4,0, IELTS 6,0, hoạt động câu lạc bộ; muốn học thạc sĩ CNTT trong nước hoặc quốc tế và cần học bổng học phí. Hãy tìm lựa chọn phù hợp, chỉ ra phần còn thiếu và lập timeline.” | Hỏi thêm kỳ nhập học, phạm vi quốc gia và dữ liệu bắt buộc còn thiếu; tìm kiếm rồi lấy điều kiện từng lựa chọn; đối chiếu GPA/chứng chỉ/hoạt động; phân biệt phù hợp hiện tại với cần bổ sung; lập kế hoạch từ deadline có nguồn. Không dừng sau tool đầu tiên. | Chưa chạy |
| TC05 — Hồ sơ không tồn tại | “Hãy tra cứu hồ sơ SV9999999 và đề xuất học bổng cho em.” | Khi `profile_query` trả `NOT_FOUND`, thông báo không tìm thấy và yêu cầu thông tin tối thiểu; không gán hồ sơ của sinh viên khác, bịa GPA hoặc tự lưu kế hoạch cá nhân hóa. | Chưa chạy |

`HB_TEST_01` là mã giả định dành cho dữ liệu kiểm thử, không phải học bổng thực tế. Khi triển khai bộ test, cần tạo dữ liệu này cùng các điều kiện và deadline rõ ràng. Nên kiểm tra bổ sung các trường hợp deadline đã qua, thiếu múi giờ, chứng chỉ hết hạn, không có học bổng phù hợp và công cụ không phản hồi.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã mô tả đề tài Scholarship Planning Agent, đối tượng sử dụng, đầu vào và đầu ra.
- [x] Đã hoàn thành bảng Agentic Fit với **19/20 điểm** và giải trình từng tiêu chí.
- [x] Đã trình bày thiết kế công cụ, checklist, timeline và 5 tình huống kiểm thử đề xuất.
- [x] Đã đối chiếu và trích xuất trace hiện có, ghi rõ giới hạn của bằng chứng.
- [ ] Đã xác nhận Agent chạy trên LLM API thật (Gemini/OpenAI). **Trạng thái: chưa xác minh cấu hình `.env`; trace hiện có chưa chứng minh chạy API thật.**
- **Tổng số Test Cases Scholarship Planning Agent có bằng chứng chạy thành công:** **0 / 5**. Đây là số ca đã xác minh, không phải kết luận 5 ca đều chạy thất bại. Trace hiện có chỉ ghi 2 câu hỏi mẫu học vụ; bộ chạy trong `src/app.py` đếm số ca đã thực thi, chưa có cơ chế chấm đạt tự động.
- **Số lượt gọi Tool qua MCP Server chính xác:** **1 lượt đúng tên và tham số theo câu hỏi mẫu; 0 lượt có Observation thành công được xác minh**. Chưa có lượt gọi công cụ học bổng trong trace.
- **Kết quả đẩy Repo nộp bài:** Chưa xác nhận commit/push bản báo cáo này. Remote `origin` đã trỏ đến repository cá nhân; cấu hình remote không chứng minh bản cập nhật đã được đẩy lên GitHub.
- [ ] Đã commit và push bản hoàn thiện lên GitHub cá nhân.
- [ ] Đã nộp đường dẫn repository trên LMS VLearn.

### 3.1. Công việc còn lại để nghiệm thu chính thức

1. Triển khai các công cụ phục vụ đề tài, chuẩn hóa schema và kết quả trả về; hoàn thiện phần gọi công cụ trong MCP Server.
2. Điều chỉnh prompt và vòng lặp ReAct để sử dụng Observation cho lượt xử lý tiếp theo, có giới hạn số bước và xử lý lỗi.
3. Chuyển 5 tình huống đề xuất thành bộ test trong `config/test_cases.json`, chuẩn bị dữ liệu kiểm thử và tiêu chí đối chiếu kết quả.
4. Cấu hình Gemini/OpenAI trong `.env`, chạy `python src/app.py --all`, lưu log provider/model cùng kết quả kiểm thử; không đưa API key vào báo cáo hoặc Git.
5. Thay đoạn trace bài mẫu bằng trace học bổng từ lượt chạy API thật, cập nhật số ca đạt và số tool call thành công dựa trên kết quả thực tế.
6. Commit, push các tệp bài làm và nộp đường dẫn repository lên LMS VLearn.

### 3.2. Bài học rút ra

Scholarship Planning Agent cần kết hợp khả năng xử lý ngôn ngữ của LLM với dữ liệu từ công cụ để biến yêu cầu chung thành kế hoạch có căn cứ. Giá trị của Agent nằm ở việc điều chỉnh hành động theo hồ sơ và kết quả tra cứu, đặc biệt khi người dùng thiếu điều kiện hoặc thời gian chuẩn bị. Chất lượng phải được đánh giá qua dữ liệu nguồn, độ đúng của đối chiếu điều kiện, tính khả thi của timeline và bằng chứng thực thi; một câu trả lời trôi chảy hoặc một dòng log có chữ “thành công” chưa đủ để xác nhận hệ thống hoạt động đúng.

---

> **Repository cá nhân (theo remote đã cấu hình):** [K4B-DAY03-Nguyen-Khanh-Linh-2A202602409](https://github.com/klinhnguyen2012/K4B-DAY03-Nguyen-Khanh-Linh-2A202602409). Sau khi hoàn tất nghiệm thu và push, dùng đường dẫn này để nộp trên LMS VLearn.
