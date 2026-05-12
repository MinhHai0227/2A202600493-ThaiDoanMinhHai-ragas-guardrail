# Judge Bias Report

## Mục tiêu
Đo lường các bias trong pipeline LLM-as-Judge và ghi nhận hiệu quả của biện pháp giảm bias.

## Kết quả tổng hợp
- Số câu đánh giá pairwise: 20
- Kappa human vs judge: 1.0000 (Questions compared: 10)
- Phân bố winner cuối cùng:
  - tie: 12/20 (60%)
  - a: 6/20 (30%)
  - b: 2/20 (10%)

## Bias 1: Position Bias
- Metric:
  - Run1 (A trước B): `a=6, b=4, tie=10`
  - Run2 (đã swap và flip lại): `a=10, b=2, tie=8`
  - Chênh lệch A-win giữa run2 và run1: +4 mẫu
- Evidence:
  - Tỷ lệ chọn A thay đổi theo thứ tự hiển thị, cho thấy judge bị ảnh hưởng bởi vị trí câu trả lời.
- Mitigation:
  - Áp dụng `swap-and-average` (chạy 2 lần với thứ tự đảo) và chỉ giữ winner khi 2 lượt nhất quán.
  - Nếu bất đồng giữa 2 lượt thì trả về `tie`.
- Outcome:
  - Sau mitigation, winner_final ổn định hơn và giảm rủi ro thiên vị vị trí.

## Bias 2: Tie / Conservatism Bias
- Metric:
  - `winner_final=tie` chiếm 12/20 (60%)
- Evidence:
  - Tỷ lệ tie cao cho thấy judge có xu hướng bảo thủ khi khác biệt giữa 2 đáp án không rõ ràng hoặc cả hai cùng yếu.
- Mitigation:
  - Giữ tie làm trạng thái hợp lệ để tránh quyết định cưỡng bức.
  - Kết hợp thêm absolute scoring để có trục đánh giá độc lập ngoài pairwise winner.
- Outcome:
  - Pipeline tránh chọn winner sai trong các case mơ hồ, đổi lại tỷ lệ tie cao cần được ghi nhận trong báo cáo.

## Bias 3: A/B Imbalance ở winner cuối
- Metric:
  - Trong 8 mẫu có winner rõ ràng: A thắng 6 (75%), B thắng 2 (25%)
- Evidence:
  - Có xu hướng nghiêng về A trên tập hiện tại.
- Mitigation:
  - Giữ chuẩn hóa nhãn (`a/b/tie`) nhất quán.
  - Đối chiếu định kỳ với human labels (Cohen’s kappa).
  - Tăng kích thước tập calibration để giảm nhiễu thống kê.

## Kết luận
- Pipeline judge đã có biện pháp giảm position bias (swap-and-average) và có tín hiệu tốt về độ nhất quán với nhãn người (`kappa=1.0000` trên 10 mẫu).
- Tuy nhiên tie-rate cao (60%) và mất cân bằng A/B ở winner rõ ràng vẫn là điểm cần theo dõi khi mở rộng tập đánh giá.
