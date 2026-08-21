# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Lăng Nhật Minh |
| MSSV | 2A202601482 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/Minhmaxxx/K4-Track2-Day21-CI-CD-for-AI-Systems-2A202601482-LangNhatMinh |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ siêu tham số này đem lại giá trị `f1_score` cao nhất (0.7149), vượt xa ngưỡng chất lượng tối thiểu 0.65 của bài lab. Điểm đáng chú ý là lần chạy 1 đạt accuracy cao hơn lần chạy 3 (0.8780 so với 0.8740), nhưng `f1_score` lại thấp hơn (0.7109 so với 0.7149). Điều này chứng minh accuracy cao có thể gây ảo giác khi mô hình thiên vị lớp đa số, trong khi cấu hình của lần chạy 3 giúp mô hình cân bằng tốt hơn giữa precision và recall cho lớp thiểu số. Việc tăng `n_estimators` lên 200 kết hợp với `max_depth=5` cho phép mô hình học được các quan hệ phi tuyến phức tạp mà không bị underfitting như ở lần chạy 2.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult Census Income có sự mất cân bằng phân phối lớp rõ rệt: lớp dương (thu nhập > 50K USD/năm) chỉ chiếm 24.8%, trong khi lớp âm (thu nhập <= 50K USD/năm) chiếm tới 75.2%. 

Nếu sử dụng độ đo Accuracy, một mô hình vô dụng luôn dự đoán mặc định nhãn "thu nhập thấp" cho mọi mẫu dữ liệu vẫn dễ dàng đạt được accuracy lên tới 75.2% (0.752), dù hoàn toàn không nhận diện được bất kỳ người có thu nhập cao nào ($F1 = 0.000$). Do đó, Accuracy tạo ra ảo tưởng về hiệu năng và hoàn toàn không thể dùng làm tiêu chí đánh giá cho bài toán này.

Chỉ số `f1_score` tính toán trung bình điều hòa giữa Precision và Recall riêng cho lớp dương (thu nhập cao), phản ánh chính xác năng lực thực tế của mô hình trong việc phát hiện nhóm đối tượng mục tiêu. Chúng ta không sử dụng `average="weighted"` hay `average="macro"` vì các cách tính trung bình này sẽ bị chi phối bởi kích thước áp đảo của lớp âm, làm sai lệch và suy giảm ý nghĩa của ngưỡng kiểm tra chất lượng (Quality Gate).

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lỗi Bad permissions khi SSH vào EC2 trên Windows | Windows tự động kế thừa quyền truy cập cho nhiều user lên file `.pem`. | Sử dụng công cụ `icacls` để hủy kế thừa quyền và chỉ cấp quyền đọc duy nhất cho user hiện tại. |
| Dịch vụ API trên EC2 không thể nạp model (`AttributeError` unpickle) | Lệch phiên bản `scikit-learn` giữa môi trường huấn luyện của CI và máy ảo EC2. | Đồng bộ phiên bản `scikit-learn` trong `requirements.txt` và thêm import hook tương thích cho Python trên EC2. |
| DVC push bị từ chối quyền truy cập S3 | IAM User ban đầu chưa được cấp chính sách tạo và ghi bucket S3. | Gán thêm chính sách `AmazonS3FullAccess` cho IAM user trên AWS Console. |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu mới (`train_batch2`), chỉ số `f1_score` tăng nhẹ từ 0.7149 lên 0.7354 (+0.0205) và `accuracy` tăng từ 0.8740 lên 0.8820. Do tập dữ liệu mới có cùng phân phối với tập ban đầu, sự cải thiện phản ánh việc mô hình có thêm các mẫu biên giúp tối ưu hóa ranh giới quyết định cho lớp thiểu số. Quan trọng nhất, toàn bộ pipeline Continuous Training đã tự động kích hoạt và tái triển khai thành công mà không cần can thiệp thủ công.
