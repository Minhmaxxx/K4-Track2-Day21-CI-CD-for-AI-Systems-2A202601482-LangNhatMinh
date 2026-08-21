# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

<!--
HƯỚNG DẪN - đọc rồi XÓA TOÀN BỘ các khối chú thích này sau khi điền xong:

  - Giới hạn: KHÔNG QUÁ 1 TRANG A4, tương đương khoảng 450 - 550 từ nội dung.
  - Chỉ điền vào các chỗ ___ và các ô trong bảng. Không thêm mục mới.
  - Viết bằng câu hoàn chỉnh, không gạch đầu dòng cụt lủn.
  - Kiểm tra độ dài sau khi đã xóa hết chú thích:
        wc -w nop-bai/bao-cao.md
    và xem trước bản in bằng cách mở file trên GitHub rồi Ctrl+P / Cmd+P.
-->

| | |
|---|---|
| Họ và tên | ___ |
| MSSV | ___ |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/___/___ |
| Ngày nộp | ___ |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

<!-- Khoảng 120 - 150 từ. Điền kết quả thật từ MLflow UI ở Bước 1, tối thiểu 3 lần chạy. -->

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

<!-- Nêu 2 - 3 khó khăn thật, mỗi ô một câu ngắn. -->

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lỗi Bad permissions khi SSH vào EC2 trên Windows | Windows tự động kế thừa quyền truy cập cho nhiều user lên file `.pem`. | Sử dụng công cụ `icacls` để hủy kế thừa quyền và chỉ cấp quyền đọc duy nhất cho user hiện tại. |
| Dịch vụ API trên EC2 không thể nạp model (`AttributeError` unpickle) | Lệch phiên bản `scikit-learn` giữa môi trường huấn luyện của CI và máy ảo EC2. | Đồng bộ phiên bản `scikit-learn` trong `requirements.txt` và nâng cấp runner Python của GitHub Actions. |
| DVC push bị từ chối quyền truy cập S3 | IAM User ban đầu chưa được cấp chính sách tạo và ghi bucket S3. | Gán thêm chính sách `AmazonS3FullAccess` cho IAM user trên AWS Console. |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

<!-- Lấy số liệu từ bảng ở mục 3.6 của tasks/buoc-3.md. -->

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | ___ | ___ |
| Bước 3 (thêm `train_batch2`) | ___ | ___ |

**Nhận xét:** ___

<!--
Một câu trả lời trung thực kiểu "f1 giảm 0,01 vì dữ liệu mới cùng phân phối, không mang
thêm thông tin mới" được đánh giá cao hơn kết luận sai rằng thêm dữ liệu luôn tốt hơn.
-->

---

## 5. Phần Bonus Đã Thực Hiện (nếu có)

<!-- Xóa cả mục 5 nếu không làm bonus. Mỗi bonus tối đa 1 dòng. -->

- [ ] Bonus 1 - Tracking MLflow từ xa với DagsHub: ___
- [ ] Bonus 2 - Điều chỉnh ngưỡng quyết định: ___
- [ ] Bonus 3 - Báo cáo precision / recall tự động: ___
- [ ] Bonus 4 - Hoàn trả về phiên bản trước: ___
- [ ] Bonus 5 - Cảnh báo lệch lạc dữ liệu: ___
