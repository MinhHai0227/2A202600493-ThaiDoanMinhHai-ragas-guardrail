# Failure Cluster Analysis

## Bottom 10 Questions

| # | Question | Worst Metric | Score | Avg | Diagnosis | Suggested Fix |
|---|---|---|---:|---:|---|---|
| 1 | Công ty thực hiện chính sách kế toán nào đối với hàng tồn kho và phương pháp tính giá vốn hàng bán? | faithfulness | 0.0000 | 0.0000 | LLM hallucinating — trả lời không dựa trên context | Tighten system prompt: 'Chỉ trả lời dựa trên context được cung cấp.' Lower temperature. |
| 2 | Quy trình đánh giá tác động xử lý dữ liệu cá nhân bao gồm những bước nào? | faithfulness | 0.0000 | 0.1889 | LLM hallucinating — trả lời không dựa trên context | Tighten system prompt: 'Chỉ trả lời dựa trên context được cung cấp.' Lower temperature. |
| 3 | Các khoản nợ phải trả dài hạn của công ty bao gồm những gì và tổng giá trị là bao nhiêu? | context_precision | 0.0000 | 0.3538 | Too many irrelevant chunks — context chứa noise | Add reranking (bge-reranker-v2-m3) để lọc top-3 relevant chunks trước khi đưa vào LLM. |
| 4 | Điều kiện hợp pháp để xử lý dữ liệu cá nhân mà không cần sự đồng ý của chủ thể là gì? | faithfulness | 0.0000 | 0.3625 | LLM hallucinating — trả lời không dựa trên context | Tighten system prompt: 'Chỉ trả lời dựa trên context được cung cấp.' Lower temperature. |
| 5 | Sự khác biệt giữa bên kiểm soát dữ liệu và bên xử lý dữ liệu trong Nghị định 13/2023 là gì? | faithfulness | 0.0000 | 0.3750 | LLM hallucinating — trả lời không dựa trên context | Tighten system prompt: 'Chỉ trả lời dựa trên context được cung cấp.' Lower temperature. |
| 6 | Doanh thu thuần từ bán hàng và cung cấp dịch vụ của công ty là bao nhiêu trong kỳ báo cáo? | context_precision | 0.0000 | 0.5184 | Too many irrelevant chunks — context chứa noise | Add reranking (bge-reranker-v2-m3) để lọc top-3 relevant chunks trước khi đưa vào LLM. |
| 7 | Vốn chủ sở hữu của công ty tại cuối kỳ báo cáo là bao nhiêu và cơ cấu gồm những khoản mục nào? | context_recall | 0.0000 | 0.5554 | Missing relevant chunks — context thiếu thông tin cần thiết | Improve chunking strategy (hierarchical) hoặc tăng top-k retrieval, thêm BM25 hybrid. |
| 8 | Dữ liệu cá nhân nhạy cảm bao gồm những loại nào theo Nghị định 13/2023? | answer_relevancy | 0.0000 | 0.5833 | Answer doesn't match question intent | Improve prompt template: thêm few-shot examples, rõ ràng hóa format output. |
| 9 | Lợi nhuận sau thuế thu nhập doanh nghiệp của công ty trong kỳ là bao nhiêu? | context_precision | 0.0000 | 0.6215 | Too many irrelevant chunks — context chứa noise | Add reranking (bge-reranker-v2-m3) để lọc top-3 relevant chunks trước khi đưa vào LLM. |
| 10 | Nguyên tắc xử lý dữ liệu cá nhân theo Nghị định 13/2023 là gì? | context_recall | 0.1429 | 0.6521 | Missing relevant chunks — context thiếu thông tin cần thiết | Improve chunking strategy (hierarchical) hoặc tăng top-k retrieval, thêm BM25 hybrid. |
