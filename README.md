# POP Assistant

<p align="center">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square" alt="Status">
</p>

<p align="center">
  <b>AI Desktop Companion</b> — Trợ lý AI chạy hoàn toàn nội bộ, bảo mật tuyệt đối.<br>
  Điều khiển bằng giọng nói · Multi-Agent · Mã nguồn mở · Không cần internet
</p>

---

## Tổng quan

POP Assistant là trợ lý AI cá nhân chạy trực tiếp trên desktop, được xây dựng bằng **Python** và **PyQt6**. Không phí thuê bao, không thu thập dữ liệu, không cần internet — mọi thứ vận hành ngay trên máy của bạn.

Dự án tích hợp:
- **Nhận diện giọng nói** với Parakeet-CTC-0.6B-VI (NVIDIA NeMo)
- **Tổng hợp giọng nói** với Magpie-TTS giọng Sophia
- **Multi-Agent System** với Planner, Memory, và Workflow Engine
- **AI nội bộ** qua Gemma 4 e4B QAT 7B 
- **Giám sát hệ thống** theo thời gian thực
- **Web Dashboard** qua FastAPI

---

## Tính năng

### Trợ lý giọng nói
- **Speech-to-Text**: Parakeet-CTC-0.6B-VI — nhận diện tiếng Việt chính xác cao
- **Text-to-Speech**: Magpie-TTS giọng Sophia — giọng nói tự nhiên
- **Wake Word**: Nhận diện từ khóa kích hoạt
- **Intent Parsing**: Phân tích ý định người dùng
- **Thực thi lệnh**: mở ứng dụng, tìm kiếm, điều khiển hệ thống
- **Lịch sử hội thoại**: lưu trữ qua SQLite

```text
Mở Chrome
Mở Calculator
Tìm Google
Mở YouTube
CPU hiện tại bao nhiêu?
RAM đang sử dụng bao nhiêu?
Pin còn bao nhiêu?
```

### Multi-Agent System

Hệ thống agent phân tán với Planner trung tâm:

| Agent | Vai trò |
|---|---|
| Voice Agent | Xử lý giọng nói (STT + TTS) |
| System Agent | Giám sát & điều khiển hệ thống |
| File Agent | Quản lý tệp tin |
| Browser Agent | Tự động duyệt web |
| Desktop Agent | Điều khiển ứng dụng desktop |
| Memory Agent | Lưu trữ & truy xuất ngữ cảnh |
| Code Agent | Hỗ trợ lập trình |

### Giám sát hệ thống

Theo dõi tài nguyên phần cứng theo thời gian thực:
- CPU, RAM, ổ đĩa
- Nhiệt độ GPU, CPU
- Trạng thái pin
- Cảnh báo khi vượt ngưỡng

### Gợi ý thói quen

Theo dõi quá trình sử dụng ứng dụng và đưa ra gợi ý dựa trên tần suất, thời điểm và điểm đánh giá hàng tuần.

### Bảng quản trị

- Quản lý người dùng
- Quản lý lịch sử hội thoại
- Dashboard theo dõi hệ thống
- Thống kê sử dụng

Kích hoạt bằng cách nhấn **Alt** ba lần trong hai giây tại màn hình đăng nhập.

---

## Cài đặt

### Yêu cầu

- Python 3.10+
- pip
- Git
- CUDA Toolkit (Khuyến khích để chạy AI nội bộ)

### Linux

```bash
# Clone dự án
git clone https://github.com/MADGE-petter/Virtual-Assistantpop.git
cd Virtual-Assistantpop

# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate

# Cài đặt PyTorch (Yêu cầu cho Parakeet-CTC)
# Cho CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# Hoặc cho CPU:
# pip install torch torchvision torchaudio

# Cài đặt dependencies chính
pip install -r requirements.txt

# Cài đặt NVIDIA NeMo cho STT
pip install nemo_toolkit[all]

# Chạy ứng dụng
python login.py
```

### Windows

```bash
# Clone dự án
git clone https://github.com/MADGE-petter/Virtual-Assistantpop.git
cd Virtual-Assistantpop

# Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate

# Cài đặt PyTorch (Yêu cầu cho Parakeet-CTC)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Cài đặt dependencies chính
pip install -r requirements.txt

# Cài đặt NVIDIA NeMo cho STT
pip install nemo_toolkit[all]

# Chạy ứng dụng
python login.py
```

---

## Kiến trúc hệ thống

Dự án được xây dựng theo mô hình **MVC (Model–View–Controller)** kết hợp **Multi-Agent Architecture**.

```text
┌──────────────────────────────────────────────┐
│ Người dùng                                   │
│                                               │
│  ┌──────────┐    ┌──────────┐                │
│  │ Giao diện │    │ Controller│                │
│  │  PyQt6   │◄───│  Layer   │                │
│  └────┬─────┘    └────┬─────┘                │
│       │               │                       │
│       ▼               ▼                       │
│  ┌─────────────────────────────────────┐     │
│  │         Multi-Agent System           │     │
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ │     │
│  │  │ Planner │ │ Memory  │ │Workflow│ │     │
│  │  └────┬────┘ └─────────┘ │Engine │ │     │
│  │       └────────┬─────────┴───┬────┘     │
│  │                ▼             │           │
│  │  ┌─────────────────────────┐ │           │
│  │  │   Agent Orchestrator    │ │           │
│  │  └───────────┬─────────────┘ │           │
│  │              ▼               │           │
│  │  ┌─────────┐ ┌─────────┐ ┌──┴───────┐  │
│  │  │ Voice   │ │ System  │ │ Browser  │  │
│  │  │ Agent   │ │ Agent   │ │ Agent    │  │
│  │  └─────────┘ └─────────┘ └──────────┘  │
│  └─────────────────────────────────────┘     │
│                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ SQLite   │ │   LLM    │ │ System   │     │
│  │   DB     │ │ (Gemma)  │ │  APIs    │     │
│  └──────────┘ └──────────┘ └──────────┘     │
└──────────────────────────────────────────────┘
```

### Luồng xử lý giọng nói

```text
Microphone → Parakeet-CTC (STT) → Intent Parser → Agent → Magpie-TTS → Loa
```

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
| Gemma 4 e4B QAT 7B   |
| Ngôn ngữ | Python 3.10+ |
| Giao diện | PyQt6 |
| Cơ sở dữ liệu | SQLite |
| STT | Parakeet-CTC-0.6B-VI (NVIDIA NeMo) |
| TTS | Magpie-TTS (giọng Sophia) |
| LLM | Gemma 4B (llama.cpp) |
| Web Server | FastAPI + Uvicorn |
| Giám sát hệ thống | psutil, pynvml |
| Đọc nhiệt độ | LibreHardwareMonitor |
| Kiến trúc | MVC + Multi-Agent |

---

## Cấu trúc dự án

```text
Virtual-Assistantpop/
├── agent_gemma/          # Model Gemma 4B (GGUF)
├── assets/               # Icon & assets
├── cache/                # TTS cache
├── controller/           # MVC Controllers
│   └── handlers/         # Intent handlers
├── database/             # Database layer
├── memory/               # Memory system
├── model/                # Data models
├── service/              # Business logic
│   └── agent/            # Multi-agent system
├── tools/                # External tools
├── utils/                # Utilities
├── view/                 # PyQt6 UI
│   └── widgets/          # Custom widgets
├── web/                  # Web dashboard
│   ├── pop-landing/      # Landing page
│   ├── static/           # Static files
│   └── templates/        # HTML templates
├── login.py              # Entry point
├── main.py               # Main window
├── requirements.txt      # Dependencies
└── README.md
```

---

## Điểm nổi bật

- **AI nội bộ 100%** — Parakeet-CTC + Magpie-TTS + Gemma 4 e4B chạy local, không cần internet
- **Multi-Agent** — Planner + Workflow Engine + 7 chuyên gia Agent
- **Giọng nói tiếng Việt** — STT chính xác cao, TTS giọng Sophia tự nhiên
- **MVC + Plugin** — kiến trúc module, dễ mở rộng
- **Web Dashboard** — theo dõi & quản lý từ xa qua FastAPI
- **Mã nguồn mở** — MIT License, tự do sử dụng & đóng góp

---

