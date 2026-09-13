# Scholarship dashboard redesign

## Mục tiêu

Chuyển prototype từ landing page sang dashboard hướng tác vụ, giúp người dùng thấy rõ hành trình từ hồ sơ đến kế hoạch nộp học bổng.

## Bố cục

1. Hero ngắn với thương hiệu tím và minh họa học bổng hiện có ở bên phải.
2. Thanh flow năm bước: Profile, Agent Analysis, Scholarship Matches, Gap Analysis, Application Plan.
3. Profile và Agent Analysis đặt đầu dashboard. Agent Analysis thể hiện bốn quan sát đã thực hiện: phân tích hồ sơ, tìm cơ hội, kiểm tra yêu cầu và phát hiện khoảng thiếu.
4. Scholarship Matches có card cho từng lựa chọn, gồm match score, trường/quốc gia, funding, điều kiện GPA/IELTS, gap, deadline và các thao tác xem chi tiết, so sánh, tạo kế hoạch.
5. Gap Analysis tách GPA, IELTS, hoạt động ngoại khóa và chứng chỉ, với trạng thái đạt/cần bổ sung và giải thích ngắn.
6. Application Plan chỉ render khi người dùng chọn một scholarship bằng CTA. Nội dung gồm checklist, timeline, deadline/reminder và trạng thái task có thể đổi bằng checkbox.

## Tương tác và dữ liệu

- Trạng thái `selectedScholarship` khởi tạo rỗng. Nút tạo kế hoạch đặt scholarship được chọn, cuộn đến Application Plan và hiển thị phần này.
- Nút xem chi tiết cập nhật khu vực tóm tắt của scholarship. Nút so sánh bật trạng thái so sánh để làm nổi bật cả hai card.
- Chat nhận câu hỏi tự do và thêm phản hồi dựa trên các dữ liệu hồ sơ đã hiển thị. Không hiển thị mã nội bộ hoặc nhãn mock/debug.
- Checklist thay đổi tiến độ và trạng thái task ngay trên giao diện.

## Thiết kế

- Dùng Plus Jakarta Sans cho heading và DM Sans cho nội dung; đặt line-height và khoảng cách rõ ràng để tiếng Việt không dính chữ.
- Card nền trắng, viền lavender nhẹ, status chip và CTA gọn; nền dashboard lavender nhạt, hero tím đậm.
- Breakpoint 1024px chuyển grids sang hai cột; dưới 720px chuyển một cột, hero chỉ giữ copy và illustration thu gọn.

## Kiểm chứng

- `npm run build` phải hoàn tất.
- `npm run test:sites` phải hoàn tất.
- Kiểm tra localhost có HTTP 200 và asset illustration được tải.
- Kiểm tra thủ công: Application Plan không xuất hiện trước khi chọn scholarship, sau khi chọn thì các task cập nhật tiến độ.
