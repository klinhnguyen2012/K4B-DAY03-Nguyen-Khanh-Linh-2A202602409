# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Khánh Linh
>
> **Mã Sinh Viên / Mã Học viên:** 2A202602409
>
> **Chủ đề Lựa chọn:** Đề tài mở — Scholarship Planning Agent (Trợ lý tìm kiếm học bổng và lập kế hoạch chuẩn bị hồ sơ)
>
> **Ngày cập nhật báo cáo:** 13/09/2026

**Mô tả đề tài:** Scholarship Planning Agent hỗ trợ học sinh/sinh viên tìm kiếm học bổng và trường phù hợp trong nước hoặc quốc tế dựa trên hồ sơ cá nhân. Agent phân tích GPA, chứng chỉ ngoại ngữ, hoạt động ngoại khóa và mục tiêu học tập; đối chiếu điều kiện tuyển sinh để xác định yêu cầu còn thiếu. Từ đó, hệ thống đề xuất học bổng, chương trình hoặc hoạt động cần chuẩn bị, đồng thời tạo checklist và timeline cá nhân hóa theo từng hạn nộp hồ sơ.

**Phạm vi báo cáo:** Scholarship Planning Agent đã triển khai bốn công cụ học bổng, MCP JSON-RPC và vòng lặp ReAct nhiều bước. Bằng chứng ở Mục 2 là lượt chạy kiểm thử với `MockOfflineProvider`; đây là kiểm thử chức năng offline, không phải bằng chứng gọi Gemini/OpenAI API thật.

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

### 1.2. Luồng xử lý và công cụ đã triển khai

Các công cụ sau đã được khai báo trong `src/tools.py` và được MCP Server công bố cho Agent.

| Bước | Công cụ / xử lý đề xuất | Kết quả cần có |
| :--- | :--- | :--- |
| 1. Đọc và xác thực hồ sơ | `profile_query(student_id)` | Hồ sơ có GPA và thang điểm, chứng chỉ, hoạt động, mục tiêu; liệt kê trường còn thiếu. Nếu không tìm thấy hồ sơ, yêu cầu người dùng cung cấp thông tin. |
| 2. Tìm lựa chọn ban đầu | `scholarship_search(degree, major, regions, intake, funding_need)` | Danh sách chương trình/học bổng cùng trường, mức hỗ trợ và đường dẫn nguồn chính thức. |
| 3. Lấy điều kiện cụ thể | `scholarship_details(scholarship_id, intake)` | Điều kiện của đúng kỳ tuyển sinh, hồ sơ bắt buộc, deadline kèm múi giờ và ngày kiểm tra nguồn. Phân biệt hạn nhập học với hạn học bổng. |
| 4. Phân tích mức phù hợp | Agent đối chiếu hồ sơ với dữ liệu công cụ | Phân loại: đáp ứng điều kiện đã xác minh, cần bổ sung, không đáp ứng, hoặc chưa đủ dữ liệu. Không tự quy đổi GPA nếu chưa có quy tắc của đơn vị tuyển sinh. |
| 5. Lập kế hoạch | `study_plan_save(student_id, scholarship_id, tasks)` | Checklist được lưu với thời hạn, trạng thái, phụ thuộc giữa các việc và tiêu chí hoàn thành. Chỉ thông báo đã lưu khi công cụ trả về thành công. |

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

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG

> ⚠️ **Giới hạn bằng chứng:** Lượt chạy dưới đây dùng `MockOfflineProvider:Offline-Mock-Model-2026`. Cần cấu hình `GEMINI_API_KEY` hoặc `OPENAI_API_KEY` trong `.env` và chạy lại để nghiệm thu với API thật. Không đưa API key vào Git hoặc báo cáo.

### 2.1. Bằng chứng hiện có

File [`trace_waterfall.json`](trace_waterfall.json) chứa **12 sự kiện của 5 test case Scholarship Planning Agent**: 5 `FINAL_ANSWER` và 7 `TOOL_EXECUTION`. Mỗi sự kiện đều ghi provider/model. Không có lời gọi API thật trong trace này.

Đoạn sau trích luồng TC03, cho thấy Agent đọc hồ sơ, lấy điều kiện học bổng, lưu checklist và chỉ phản hồi đã lưu sau khi nhận `SUCCESS`:

```json
[
  {
    "step": 1,
    "query": "Dùng hồ sơ sinh viên SV2026001 và học bổng thử nghiệm HB_TEST_01 đã chọn, hãy tạo checklist chuẩn bị hồ sơ theo deadline của chương trình.",
    "provider": "MockOfflineProvider:Offline-Mock-Model-2026",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "profile_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {"status": "SUCCESS", "student_id": "SV2026001"},
    "latency_ms": 0.01
  },
  {
    "step": 2,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "scholarship_details",
    "arguments": {"scholarship_id": "HB_TEST_01", "intake": "2027"},
    "observation": {"status": "SUCCESS", "scholarship_id": "HB_TEST_01"}
  },
  {
    "step": 3,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "study_plan_save",
    "observation": {"status": "SUCCESS", "plan_id": "PLAN-SV2026001-HB_TEST_01"}
  },
  {
    "step": 4,
    "action_type": "FINAL_ANSWER",
    "output": "Đã lưu checklist và timeline thử nghiệm thành công."
  }
]
```

### 2.2. Nhận xét trace và giới hạn

- **TC01:** Trả lời giới thiệu mà không gọi công cụ, đúng với yêu cầu hỏi khả năng hỗ trợ.
- **TC02:** Gọi `profile_query(SV2026001)` và nhận dữ liệu hồ sơ có trạng thái `SUCCESS` trước khi tổng hợp.
- **TC03:** Thực hiện chuỗi `profile_query → scholarship_details → study_plan_save`; phản hồi cuối chỉ xác nhận lưu sau Observation `SUCCESS`.
- **TC04:** Tìm 2 lựa chọn thử nghiệm, lấy chi tiết `HB_TEST_01`, rồi xác định GPA 3,5/4,0 đạt mức 3,2 còn IELTS 6,0 thiếu 0,5 so với yêu cầu 6,5. Timeline trong phản hồi dùng deadline của dữ liệu thử nghiệm.
- **TC05:** `profile_query(SV9999999)` trả `NOT_FOUND`; Agent yêu cầu dữ liệu tối thiểu và không bịa hồ sơ hoặc lưu kế hoạch.
- **Độ trễ:** Các con số rất nhỏ trong trace là số đo môi trường mock nội bộ; không dùng để suy ra độ trễ của LLM hoặc MCP khi chạy API thật.

### 2.3. Bộ 5 tình huống kiểm thử đã thực thi offline

Năm tình huống đã nằm trong `config/test_cases.json` và được chạy bằng lệnh `LLM_PROVIDER=mock .venv/bin/python src/app.py --all`.

| Mã | Câu hỏi kiểm thử đề xuất | Hành vi và tiêu chí đạt | Trạng thái |
| :--- | :--- | :--- | :--- |
| TC01 — Hỏi đáp trực tiếp | Giới thiệu khả năng của Agent | Không gọi tool. | Đã chạy offline |
| TC02 — Tra cứu hồ sơ | Tra cứu `SV2026001` | `profile_query` trả `SUCCESS`. | Đã chạy offline |
| TC03 — Tạo kế hoạch | Tạo checklist cho `HB_TEST_01` | 3 tool call, lưu `PLAN-SV2026001-HB_TEST_01`. | Đã chạy offline |
| TC04 — Suy luận nhiều bước | Tìm lựa chọn, nêu thiếu hụt và timeline | 2 tool call, xác định IELTS thiếu 0,5. | Đã chạy offline |
| TC05 — Hồ sơ không tồn tại | Tra cứu `SV9999999` | Xử lý `NOT_FOUND`, không bịa dữ liệu. | Đã chạy offline |

`HB_TEST_01` là mã giả định dành cho dữ liệu kiểm thử, không phải học bổng thực tế. Khi triển khai bộ test, cần tạo dữ liệu này cùng các điều kiện và deadline rõ ràng. Nên kiểm tra bổ sung các trường hợp deadline đã qua, thiếu múi giờ, chứng chỉ hết hạn, không có học bổng phù hợp và công cụ không phản hồi.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã mô tả đề tài Scholarship Planning Agent, đối tượng sử dụng, đầu vào và đầu ra.
- [x] Đã hoàn thành bảng Agentic Fit với **19/20 điểm** và giải trình từng tiêu chí.
- [x] Đã triển khai và trình bày 4 công cụ học bổng, checklist, timeline và 5 tình huống kiểm thử.
- [x] Đã chạy 5/5 test case offline và lưu waterfall trace có provider/model.
- [ ] Đã xác nhận Agent chạy trên LLM API thật (Gemini/OpenAI). **Trạng thái: chưa xác minh cấu hình `.env`; trace hiện có chưa chứng minh chạy API thật.**
- **Tổng số Test Cases Scholarship Planning Agent có bằng chứng chạy thành công:** **5 / 5 offline**. Chưa có bằng chứng chạy bằng LLM API thật.
- **Số lượt gọi Tool qua MCP Server chính xác:** **7 lượt**, gồm 6 `SUCCESS` và 1 `NOT_FOUND` được xử lý đúng theo TC05.
- **Kết quả đẩy Repo nộp bài:** Chưa xác nhận commit/push bản báo cáo này. Remote `origin` đã trỏ đến repository cá nhân; cấu hình remote không chứng minh bản cập nhật đã được đẩy lên GitHub.
- [ ] Đã commit và push bản hoàn thiện lên GitHub cá nhân.
- [ ] Đã nộp đường dẫn repository trên LMS VLearn.

### 3.1. Công việc còn lại để nghiệm thu chính thức

1. Cấu hình Gemini/OpenAI trong `.env`, chạy `python src/app.py --all`, lưu log provider/model cùng kết quả kiểm thử; không đưa API key vào báo cáo hoặc Git.
2. Cập nhật Mục 2 bằng trace API thật, tách rõ kết quả API thật và bộ mock.
3. Commit, push các tệp bài làm và nộp đường dẫn repository lên LMS VLearn.

### 3.2. Bài học rút ra

Scholarship Planning Agent cần kết hợp khả năng xử lý ngôn ngữ của LLM với dữ liệu từ công cụ để biến yêu cầu chung thành kế hoạch có căn cứ. Giá trị của Agent nằm ở việc điều chỉnh hành động theo hồ sơ và kết quả tra cứu, đặc biệt khi người dùng thiếu điều kiện hoặc thời gian chuẩn bị. Chất lượng phải được đánh giá qua dữ liệu nguồn, độ đúng của đối chiếu điều kiện, tính khả thi của timeline và bằng chứng thực thi; một câu trả lời trôi chảy hoặc một dòng log có chữ “thành công” chưa đủ để xác nhận hệ thống hoạt động đúng.

---

> **Repository cá nhân (theo remote đã cấu hình):** [K4B-DAY03-Nguyen-Khanh-Linh-2A202602409](https://github.com/klinhnguyen2012/K4B-DAY03-Nguyen-Khanh-Linh-2A202602409). Sau khi hoàn tất nghiệm thu và push, dùng đường dẫn này để nộp trên LMS VLearn.
