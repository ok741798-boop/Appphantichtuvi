# TuVi Analyzer

Web app phân tích tử vi phương Đông cho người Việt Nam. Nhập ngày giờ sinh dương lịch để nhận lá số 12 cung, luận giải năm hiện tại và dự đoán 10 năm tới.

⚠️ Kết quả mang tính tham khảo, không thay thế quyết định thực tế. Tử vi chỉ là một góc nhìn, không phải định mệnh.

## Cách chạy

Cần Python 3.10 trở lên.

Trên Windows, bấm đúp `run.bat`: script tự cài thư viện, chạy server và mở trình duyệt. Giữ cửa sổ đó mở trong khi dùng app.

Hoặc chạy bằng tay:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Mở <http://localhost:5057>. Dùng macOS, Linux hoặc Git Bash thì có thể chạy `./run.sh`, script tự tạo môi trường ảo và cài thư viện.

Cũng có thể mở thẳng `frontend/index.html` hoặc dùng Live Server (cổng 5500) để chỉnh giao diện. Khi đó trang vẫn hiện đủ CSS, còn việc lập lá số cần backend đang chạy ở `127.0.0.1:5057`.

## Cấu hình (không bắt buộc)

App chạy được ngay mà không cần cấu hình. Muốn đổi thiết lập, chép `backend/.env.example` thành `backend/.env`:

| Biến | Tác dụng |
|---|---|
| `OPENAI_API_KEY` | Bật lời luận bằng AI. Để trống thì dùng lời luận rule-based |
| `OPENAI_MODEL` | Mô hình OpenAI, mặc định `gpt-4o-mini` |
| `HOST`, `PORT` | Địa chỉ server, mặc định `127.0.0.1:5057` |
| `CORS_ORIGINS` | Các origin được gọi API |
| `PDF_FONT_PATH`, `PDF_FONT_BOLD_PATH` | Font `.ttf` tiếng Việt, chỉ cần khi máy không có Arial hoặc DejaVu Sans |

Khi bật AI, chỉ dữ liệu sao và năm xem được gửi lên OpenAI. Họ tên và ngày sinh không được gửi.

## API

| Phương thức | Đường dẫn | Mô tả |
|---|---|---|
| POST | `/api/chart/build` | Lập lá số từ `full_name`, `gender`, `day`, `month`, `year`, `hour`, `birth_place` |
| GET | `/api/chart/<chart_id>` | Lấy lá số đã lập |
| POST | `/api/analysis/current` | Phân tích năm hiện tại, body `{"chart_id": "..."}` |
| POST | `/api/analysis/forecast` | Dự đoán 10 năm, body `{"chart_id": "..."}` |
| POST | `/api/marriage/analyze` | Phân tích Duyên Số Định Mệnh, body `{"chart_id": "..."}`, từ 18 tuổi |
| POST | `/api/marriage/compare` | So sánh 2 lá số, body `{"chart_id": "...", "partner": {...}}`, lá số người ấy không được lưu |
| GET | `/api/chart/<chart_id>/pdf` | Tải báo cáo PDF |
| GET | `/api/health` | Kiểm tra server |

## Cấu trúc

```
tuvi-analyzer/
├── backend/
│   ├── app.py              Flask app và các route
│   ├── calendar_utils.py   Âm lịch GMT+7, Can Chi, nạp âm
│   ├── chart_builder.py    An 12 cung, 14 chính tinh, phụ tinh, Tứ Hóa, Tuần, Triệt
│   ├── stars_data.py       Dữ liệu sao và ý nghĩa
│   ├── interpreter.py      Chấm điểm và luận giải rule-based
│   ├── forecast.py         Dự đoán 10 năm
│   ├── marriage_analyzer.py    Phân tích cung Phu Thê
│   ├── destiny_predictor.py    Dự đoán duyên số, so sánh 2 lá số
│   ├── marriage_templates.py   Dữ liệu luận giải duyên số
│   ├── ai_narrator.py      Lời luận OpenAI, có fallback
│   ├── pdf_report.py       Xuất PDF
│   ├── tests/              Test bằng pytest
│   └── requirements.txt
├── frontend/               HTML, CSS, JavaScript thuần
├── tuvi-frontend/          Bản xem trước giao diện, mở index.html là chạy, dùng dữ liệu mẫu
├── run.sh
└── README.md
```

Chạy test:

```bash
cd backend
pip install pytest
python -m pytest tests
```

## Giới hạn cần biết

- **Dữ liệu lưu trong bộ nhớ.** Khởi động lại server là mất lá số, nhưng trình duyệt có lưu thông tin sinh nên sẽ tự lập lại khi tải trang.
- **Âm lịch tính theo GMT+7 cho mọi năm.** Trước năm 1968, lịch dùng ở Việt Nam theo múi giờ khác, nên một số người sinh sát ngày đầu tháng âm trong giai đoạn đó có thể lệch một ngày so với lịch thời ấy.
- **Thang điểm là quy ước của app**, chỉ để so sánh tương đối giữa các năm, và chưa xét độ miếu, vượng, hãm của sao.
- **Duyên Số Định Mệnh là luận giải theo quy ước**, các điểm phần trăm không phải xác suất thật. App không biết người xem đã kết hôn hay chưa.
- **Có 37 sao được an và luận giải** (14 chính tinh, 23 phụ tinh), kèm Tứ Hóa, Tuần, Triệt, chưa đủ 108 sao như một số lá số đầy đủ.
- **Các trường phái tử vi khác nhau ở vài quy tắc**, ví dụ Tứ Hóa của một số Can. App dùng bảng thông dụng ở Việt Nam, xem chú thích trong `stars_data.py`.
