# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đặng Hồ Hải
- **Student ID**: 2A202600020
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

Trong bài Lab này, tôi đã tham gia xây dựng và hoàn thiện hệ thống công cụ (Tools) và logic điều phối cho Agent.

- **Modules Implementated**: 
    - `src/tools/inventory.py`: Triển khai hàm `check_stock` để kiểm tra tồn kho thời gian thực.
    - `src/tools/logistics.py`: Xây dựng hàm `calc_shipping` tính phí vận chuyển theo công thức: $$Cost = 5.0 + (Weight \times 2.0)$$.
    - `src/agent/agent.py`: Phát triển vòng lặp ReAct (Reasoning + Acting) để xử lý các yêu cầu đa bước.
    - `src/tools/tools.py`: Hỗ trợ chỉnh sửa prompts.
- **Code Highlights**:
    - Triển khai cơ chế xử lý tham số động bằng `**kwargs` để Agent có thể truyền dữ liệu linh hoạt từ LLM vào các hàm Python.
    - Xây dựng hệ thống Logging chi tiết để capture các sự kiện `TOOL_EXECUTED` và `AGENT_END`.
    - Sử dụng Callable để ánh xạ trực tiếp mô tả công cụ với hàm thực thi. Đặc biệt là thiết kế "hướng dẫn sử dụng" (Description) cực kỳ chi tiết để LLM không gọi sai định dạng.
    - Công thức Logistics: Shipping\_Cost = 5.0 + (Weight \times 2.0)


---

## II. Debugging Case Study (10 Points)

Hệ thống đã gặp lỗi thực thi nghiêm trọng trong quá trình kiểm thử đơn hàng.

- **Problem Description**: Agent không thể tính phí vận chuyển và bị kẹt trong vòng lặp lỗi `TypeError`.
- **Log Source**: `2026-04-06T13:39:59.592148`
- **Diagnosis**: 
    - LLM nhận diện đúng công cụ `calc_shipping` nhưng trích xuất thiếu tham số `destination` từ câu hỏi của người dùng.
    - Do hàm `calc_shipping` yêu cầu 2 tham số bắt buộc (`weight_kg` và `destination`), việc thiếu 1 tham số khiến Python ném ra lỗi `TypeError: missing 1 required positional argument`.
- **Solution**: Tôi đã thực hiện hai bước sửa lỗi:
    1. Cập nhật func `get_tool_descriptions` để mô tả rõ ràng các tham số `required`.
    2. Điều chỉnh `System Prompt` để yêu cầu Agent luôn kiểm tra đủ thông tin trước khi gọi Action. Kết quả là ở lần chạy lúc `13:42:33`, Agent đã gọi thành công với phí ship là $9.0.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối `Thought` giúp Agent hoạt động như một quan sát viên có ý thức. Thay vì trả lời ngay lập tức như Chatbot Baseline, Agent biết tự hỏi: "Mình đã có đủ thông tin để tính tiền chưa?". Điều này giúp xử lý các bài toán logic phức tạp như tính toán chiết khấu kết hợp phí ship.
2. **Reliability**: Chatbot Baseline có độ ổn định cao hơn (không bao giờ crash code) nhưng độ tin cậy thấp vì hay "chém gió" (Hallucination) về phí ship ($10-$20). Agent ngược lại, có độ chính xác tuyệt đối khi tool chạy đúng, nhưng dễ bị "gãy" quy trình nếu logic code hoặc prompt không chặt chẽ.
3. **Observation**: `Observation` đóng vai trò là dữ liệu thực tế (Ground Truth). Trong log, khi nhận được `Observation: {"quantity": 5}`, Agent ngay lập tức xác nhận hàng còn và chuyển sang bước tiếp theo thay vì đoán mò.

---

## IV. Future Improvements (5 Points)

Để đưa hệ thống lên mức Production, tôi đề xuất các hướng cải tiến:

- **Scalability**: Sử dụng kiến trúc **Asynchronous** cho các tool call để giảm Latency khi phải gọi nhiều API cùng lúc.
- **Safety**: Thiết lập **Input Guardrails** và **Transaction Guardrails** để kiểm tra tính hợp lệ của tham số (ví dụ: không cho phép cân nặng âm) trước khi thực thi hàm. Thiết lập . Agent chỉ được phép báo "Thành công" sau khi đã xác nhận đồng thời cả Tồn kho (check_stock) và Thanh toán (calculator).
- **Performance**: Triển khai Parallel Processing. Agent có thể vừa kiểm tra mã giảm giá (`get_discount`), vừa tính phí ship (`calc_shipping`) cùng lúc để giảm thời gian chờ đợi (Latency) cho khách hàng.
