# Testset Review Notes

## Manual Review Sample (10 questions)

### 1) Q: Dữ liệu cá nhân nhạy cảm bao gồm những loại nào theo Nghị định 13/2023?
- Issue found: Câu hỏi rõ ràng nhưng ground truth quá dài, khó đối chiếu nhanh.
- Edit applied: Chuẩn hóa checklist các nhóm dữ liệu nhạy cảm theo bullet.
- Why this improves eval quality: Dễ đánh giá factual coverage của answer hơn.

### 2) Q: Tổ chức nước ngoài chuyển dữ liệu cá nhân ra khỏi Việt Nam cần điều kiện gì?
- Issue found: Thiếu nhấn mạnh yêu cầu đánh giá tác động và thông báo cơ quan quản lý.
- Edit applied: Thêm cụm “đánh giá tác động + thông báo Bộ Công an”.
- Why this improves eval quality: Tăng độ chính xác cho phần compliance requirement.

### 3) Q: Khác biệt giữa bên kiểm soát và bên xử lý dữ liệu là gì?
- Issue found: Dễ mơ hồ nếu không nêu rõ “mục đích/phương tiện” và “xử lý thay mặt”.
- Edit applied: Bổ sung tiêu chí phân biệt theo định nghĩa pháp lý.
- Why this improves eval quality: Giảm ambiguity khi chấm answer_relevancy.

### 4) Q: Chủ thể dữ liệu cá nhân có các quyền gì?
- Issue found: Cần đối chiếu nhiều điều khoản nên answer có thể thiếu mục.
- Edit applied: Nhóm quyền theo cụm: biết, đồng ý, truy cập/chỉnh sửa, xóa, khiếu nại.
- Why this improves eval quality: Dễ phát hiện thiếu sót của answer.

### 5) Q: Nguyên tắc xử lý dữ liệu cá nhân là gì?
- Issue found: Một số câu trả lời chỉ nêu 1-2 nguyên tắc.
- Edit applied: Chuẩn hóa danh sách nguyên tắc cốt lõi theo Nghị định.
- Why this improves eval quality: Faithfulness và completeness được chấm sát hơn.

### 6) Q: Quy trình đánh giá tác động xử lý dữ liệu gồm những bước nào?
- Issue found: Câu hỏi cần multi-step, dễ trả lời chung chung.
- Edit applied: Bổ sung gợi ý 3 bước: thu thập thông tin, phân tích rủi ro, lưu hồ sơ.
- Why this improves eval quality: Tăng khả năng phân biệt answer tốt/yếu.

### 7) Q: Điều kiện xử lý dữ liệu không cần sự đồng ý?
- Issue found: Dễ nhầm với các trường hợp ngoại lệ không cùng phạm vi.
- Edit applied: Làm rõ “trường hợp ngoại lệ theo pháp luật hiện hành”.
- Why this improves eval quality: Giảm false positive khi judge chấm correctness.

### 8) Q: Nghĩa vụ bên kiểm soát khi lộ lọt dữ liệu cá nhân?
- Issue found: Nhiều answer thiếu phần thông báo và khắc phục hậu quả.
- Edit applied: Nhấn mạnh nghĩa vụ thông báo + giảm thiểu thiệt hại.
- Why this improves eval quality: Chấm groundedness nhất quán hơn.

### 9) Q: Quy định đặc biệt cho dữ liệu cá nhân của trẻ em?
- Issue found: Cần nêu rõ yêu cầu đồng ý của người đại diện hợp pháp.
- Edit applied: Bổ sung điều kiện liên quan người giám hộ/đại diện.
- Why this improves eval quality: Tăng độ bám luật cho các câu trả lời.

### 10) Q: Cơ quan Nhà nước có trách nhiệm gì trong bảo vệ dữ liệu cá nhân?
- Issue found: Câu trả lời có thể quá chung, thiếu vai trò cụ thể.
- Edit applied: Chuẩn hóa theo nhóm trách nhiệm quản lý, hướng dẫn, giám sát.
- Why this improves eval quality: Dễ đối chiếu phạm vi trách nhiệm trong answer.

## Example of edited test item
- Original question style: “Quyền của chủ thể dữ liệu?”
- Edited question style: “Chủ thể dữ liệu cá nhân có những quyền gì theo Nghị định 13/2023?”
- Reason: Cụ thể hóa ngữ cảnh pháp lý, tránh câu quá ngắn gây mơ hồ.
