# Pop Assistant

Pop Assistant là một trợ lý ảo dành cho Windows được phát triển bằng Python và PyQt6.

Ứng dụng kết hợp điều khiển bằng giọng nói, giám sát tài nguyên hệ thống và phân tích thói quen sử dụng ứng dụng trong một nền tảng thống nhất. Dự án được thực hiện trong khuôn khổ đồ án tốt nghiệp và được xây dựng theo mô hình **MVC (Model–View–Controller)** nhằm tăng khả năng bảo trì và mở rộng.

---

## Demo

### Video

<video controls src="1783873363106_66381167024278951_516732694922087015.mp4" title="Pop Assistant Demo"></video>

### Ảnh giao diện

#### Màn hình chính

![Thông tin cá nhân](<Ảnh chụp màn hình 2026-07-12 224918.png>)

#### Giám sát hệ thống

![Thông tin phần cứng](<Ảnh chụp màn hình 2026-07-12 224924.png>)

#### Gợi ý ứng dụng

![Gợi ý](<Ảnh chụp màn hình 2026-07-12 224936.png>)

---

## Tính năng

### Trợ lý giọng nói

- Chuyển giọng nói thành văn bản (Speech-to-Text)
- Chuyển văn bản thành giọng nói (Text-to-Speech)
- Nhận diện từ khóa kích hoạt (Wake Word)
- Phân tích ý định người dùng (Intent Parsing)
- Thực thi lệnh trên hệ điều hành
- Lưu trữ lịch sử hội thoại

Ví dụ câu lệnh

```text
Mở Chrome
Mở Calculator
Tìm Google
Mở YouTube
CPU hiện tại bao nhiêu?
RAM đang sử dụng bao nhiêu?
Pin còn bao nhiêu?
```

### Giám sát hệ thống

Theo dõi tài nguyên phần cứng theo thời gian thực.

- Mức sử dụng CPU
- Mức sử dụng RAM
- Dung lượng ổ đĩa
- Nhiệt độ GPU
- Nhiệt độ CPU
- Trạng thái pin

Khi phát hiện CPU quá tải, bộ nhớ gần đầy hoặc nhiệt độ vượt ngưỡng cho phép, hệ thống sẽ đưa ra cảnh báo và gợi ý người dùng thực hiện các biện pháp tối ưu.

### Gợi ý thói quen sử dụng

Theo dõi quá trình sử dụng ứng dụng và đưa ra gợi ý dựa trên:

- Tần suất sử dụng
- Thời điểm sử dụng gần nhất
- Điểm đánh giá theo chu kỳ hàng tuần

### Bảng quản trị (Admin Panel)

Hệ thống quản trị cung cấp các chức năng:

- Quản lý người dùng
- Quản lý lịch sử hội thoại
- Quản lý cơ sở dữ liệu
- Dashboard theo dõi tài nguyên hệ thống
- Thống kê sử dụng

Chế độ quản trị được kích hoạt bằng cách nhấn **Alt** ba lần liên tiếp trong vòng hai giây tại màn hình đăng nhập.

---

## Cài đặt

Clone dự án

```bash
git clone https://github.com/MADGE-petter/Pop-Assistant.git
```

Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Chạy chương trình

```bash
python main.py
```

---

## Hướng dẫn sử dụng

### Điều khiển bằng giọng nói

```text
Mở Chrome
Mở Calculator
Mở Notepad
Tìm Google
Mở YouTube
```

### Kiểm tra thông tin hệ thống

```text
CPU hiện tại
RAM đang sử dụng
Nhiệt độ GPU
Trạng thái pin
```

---

## Kiến trúc hệ thống

Dự án được xây dựng theo mô hình **MVC (Model–View–Controller)** nhằm tách biệt giao diện, xử lý nghiệp vụ và tầng dữ liệu.

```text
                 Người dùng
                      │
                      ▼
               Giao diện PyQt6
                      │
                      ▼
                 Controller
                      │
                      ▼
                   Services
           ┌──────────┴──────────┐
           ▼                     ▼
       SQLite DB          Windows API
                                 │
                                 ▼
                        Cảm biến phần cứng
```

### Luồng xử lý giọng nói

```text
Microphone
      │
      ▼
Nhận diện giọng nói
      │
      ▼
Phân tích ý định
      │
      ▼
Thực thi lệnh
      │
      ▼
Windows API
      │
      ▼
Chuyển văn bản thành giọng nói
      │
      ▼
Loa
```

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Ngôn ngữ | Python |
| Giao diện | PyQt6 |
| Cơ sở dữ liệu | SQLite |
| Nhận diện giọng nói | SpeechRecognition, Whisper |
| Chuyển văn bản thành giọng nói | gTTS |
| Giám sát hệ thống | psutil, pynvml |
| Đọc nhiệt độ phần cứng | LibreHardwareMonitor |
| Kiến trúc | MVC |
| Quản lý mã nguồn | Git |

---

## Cấu trúc dự án

```text
Pop-Assistant
│
├── admin/
├── controller/
├── database/
├── model/
├── service/
├── tests/
├── tools/
├── view/
│
├── main.py
└── login.py
```

---

## Điểm nổi bật

- Thiết kế theo mô hình MVC giúp tách biệt giao diện, xử lý nghiệp vụ và truy cập dữ liệu.
- Xây dựng quy trình xử lý giọng nói gồm Speech-to-Text → Phân tích ý định → Thực thi lệnh → Text-to-Speech.
- Thu thập thông tin phần cứng theo thời gian thực bằng psutil, NVML và LibreHardwareMonitor.
- Lưu trữ lịch sử hội thoại và dữ liệu người dùng bằng SQLite.
- Sử dụng đa luồng để xử lý giọng nói và giám sát hệ thống, giúp giao diện luôn phản hồi mượt mà.
- Xây dựng bảng quản trị ẩn hỗ trợ quản lý người dùng, cơ sở dữ liệu và theo dõi hệ thống.
