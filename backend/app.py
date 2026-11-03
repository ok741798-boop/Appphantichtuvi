"""Flask app của TuVi Analyzer: API lập lá số, luận giải và phục vụ frontend."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Dict, Tuple

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from ai_narrator import ASPECT_LABELS, generate_narrative
from calendar_utils import solar_to_lunar
from chart_builder import build_chart
from destiny_predictor import compare_charts
from forecast import forecast_10_years
from interpreter import analyze_current
from marriage_analyzer import analyze_marriage
from pdf_report import FontNotFoundError, build_pdf

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
MIN_BIRTH_DATE = date(1900, 1, 1)
MAX_NAME_LENGTH = 100
ADULT_AGE = 18

load_dotenv(BASE_DIR / ".env")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*").split(",")}})

# Lá số lưu trong bộ nhớ: khởi động lại server là mất, frontend sẽ báo lập lại.
charts: Dict[str, Dict] = {}


class ApiError(Exception):
    """Lỗi nghiệp vụ, được trả về client kèm mã HTTP."""

    def __init__(self, message: str, status: int = 400) -> None:
        """Lưu thông báo lỗi và mã HTTP trả về."""
        super().__init__(message)
        self.message = message
        self.status = status


@app.after_request
def revalidate_frontend(response: Response) -> Response:
    """Buộc trình duyệt kiểm tra lại HTML, CSS, JS để không chạy bản cũ sau khi cập nhật."""
    if not request.path.startswith("/api/"):
        response.cache_control.no_cache = True
    return response


@app.errorhandler(ApiError)
def handle_api_error(error: ApiError) -> Tuple[Response, int]:
    """Trả lỗi nghiệp vụ dưới dạng JSON."""
    return jsonify({"error": error.message}), error.status


@app.errorhandler(Exception)
def handle_exception(error: Exception) -> Tuple[Response, int]:
    """Global handler: mọi lỗi đều trả JSON, không lộ chi tiết nội bộ."""
    if isinstance(error, HTTPException):
        return jsonify({"error": error.description}), error.code or 500
    logger.exception("Lỗi không xử lý được")
    return jsonify({"error": "Lỗi hệ thống, vui lòng thử lại sau."}), 500


def _json_body() -> Dict:
    """Đọc body JSON, báo lỗi 400 nếu không hợp lệ."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError("Dữ liệu gửi lên phải là JSON hợp lệ.")
    return body


def _int_field(body: Dict, field: str) -> int:
    """Lấy một trường số nguyên từ body."""
    value = body.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ApiError(f"Trường {field} phải là số nguyên.")
    return value


def _validate_birth_info(body: Dict) -> Dict:
    """Kiểm tra thông tin sinh và chuẩn hóa về dict dùng cho build_chart."""
    full_name = body.get("full_name")
    if not isinstance(full_name, str) or not full_name.strip():
        raise ApiError("Vui lòng nhập họ tên.")
    if len(full_name) > MAX_NAME_LENGTH:
        raise ApiError(f"Họ tên không được dài quá {MAX_NAME_LENGTH} ký tự.")
    gender = body.get("gender")
    if gender not in ("Nam", "Nữ"):
        raise ApiError("Giới tính phải là Nam hoặc Nữ.")
    hour = _int_field(body, "hour")
    if not 0 <= hour <= 23:
        raise ApiError("Giờ sinh phải từ 0 đến 23.")
    year, month, day = (_int_field(body, f) for f in ("year", "month", "day"))
    try:
        birth_date = date(year, month, day)
    except ValueError:
        raise ApiError("Ngày sinh không hợp lệ.") from None
    if not MIN_BIRTH_DATE <= birth_date <= date.today():
        raise ApiError("Ngày sinh phải từ 01/01/1900 đến hôm nay.")
    place = body.get("birth_place")
    return {
        "full_name": full_name.strip(),
        "gender": gender,
        "day": day,
        "month": month,
        "year": year,
        "hour": hour,
        "birth_place": place.strip()[:MAX_NAME_LENGTH] if isinstance(place, str) else "",
    }


def _get_chart(chart_id: object) -> Dict:
    """Lấy lá số đã lưu, báo 404 nếu không có."""
    chart = charts.get(chart_id) if isinstance(chart_id, str) else None
    if chart is None:
        raise ApiError("Không tìm thấy lá số, vui lòng lập lại.", 404)
    return chart


def _current_lunar_year() -> int:
    """Năm âm lịch hiện tại, dùng làm năm xem hạn."""
    today = date.today()
    return solar_to_lunar(today.year, today.month, today.day)["lunar_year"]


def _require_adult(info: Dict, message: str) -> None:
    """Chặn nội dung hôn nhân với người chưa đủ tuổi, báo 403."""
    today = date.today()
    birthday_passed = (today.month, today.day) >= (info["month"], info["day"])
    if today.year - info["year"] - (0 if birthday_passed else 1) < ADULT_AGE:
        raise ApiError(message, 403)


# ==================== API ====================

@app.get("/api/health")
def health() -> Response:
    """Kiểm tra server còn sống."""
    # Trả kèm tên app để frontend phân biệt với server khác đang chiếm cùng cổng.
    return jsonify({"status": "ok", "app": "tuvi-analyzer", "charts_loaded": len(charts)})


@app.post("/api/chart/build")
def chart_build() -> Response:
    """Lập lá số từ thông tin sinh."""
    chart = build_chart(_validate_birth_info(_json_body()))
    charts[chart["chart_id"]] = chart
    return jsonify(chart)


@app.get("/api/chart/<chart_id>")
def chart_get(chart_id: str) -> Response:
    """Lấy lá số đã lưu."""
    return jsonify(_get_chart(chart_id))


def _current_analysis(chart: Dict, year: int) -> Dict:
    """Phân tích năm hiện tại; lời luận lấy từ AI nếu có cấu hình."""
    result = analyze_current(chart, year)
    # Gọi song song vì mỗi khía cạnh là một request OpenAI riêng.
    with ThreadPoolExecutor(max_workers=len(ASPECT_LABELS)) as pool:
        narratives = pool.map(lambda aspect: (aspect, generate_narrative(chart, aspect, year)),
                              ASPECT_LABELS)
        result.update(dict(narratives))
    return result


@app.post("/api/analysis/current")
def analysis_current() -> Response:
    """Trả về phân tích năm hiện tại cho tab Hiện tại."""
    chart = _get_chart(_json_body().get("chart_id"))
    return jsonify(_current_analysis(chart, _current_lunar_year()))


@app.post("/api/analysis/forecast")
def analysis_forecast() -> Response:
    """Dự đoán 10 năm, bắt đầu từ năm hiện tại."""
    chart = _get_chart(_json_body().get("chart_id"))
    return jsonify({"forecast": forecast_10_years(chart, _current_lunar_year())})


@app.post("/api/marriage/analyze")
def marriage_analyze() -> Response:
    """Phân tích Duyên Số Định Mệnh của một lá số."""
    chart = _get_chart(_json_body().get("chart_id"))
    _require_adult(chart["info"], f"Tính năng Duyên Số dành cho người từ {ADULT_AGE} tuổi.")
    return jsonify(analyze_marriage(chart, _current_lunar_year()))


@app.post("/api/marriage/compare")
def marriage_compare() -> Response:
    """So sánh lá số với người ấy; lá số người ấy không được lưu lại."""
    body = _json_body()
    chart = _get_chart(body.get("chart_id"))
    _require_adult(chart["info"], f"Tính năng Duyên Số dành cho người từ {ADULT_AGE} tuổi.")
    partner = body.get("partner")
    if not isinstance(partner, dict):
        raise ApiError("Vui lòng nhập thông tin của người ấy.")
    info = _validate_birth_info(partner)
    _require_adult(info, f"Người được so sánh cần từ {ADULT_AGE} tuổi trở lên.")
    return jsonify(compare_charts(chart, build_chart(info)))


@app.get("/api/chart/<chart_id>/pdf")
def chart_pdf(chart_id: str) -> Response:
    """Xuất báo cáo PDF của lá số."""
    chart = _get_chart(chart_id)
    year = _current_lunar_year()
    try:
        pdf = build_pdf(chart, _current_analysis(chart, year), forecast_10_years(chart, year))
    except FontNotFoundError as error:
        raise ApiError(str(error), 503) from None
    return send_file(BytesIO(pdf), mimetype="application/pdf", as_attachment=True,
                     download_name="la-so-tu-vi.pdf")


# ==================== FRONTEND ====================

@app.get("/")
@app.get("/index.html")
def index() -> Response:
    """Trang nhập thông tin."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/result")
@app.get("/result.html")
def result() -> Response:
    """Trang kết quả."""
    return send_from_directory(FRONTEND_DIR, "result.html")


@app.get("/marriage")
@app.get("/marriage.html")
def marriage() -> Response:
    """Trang Duyên Số Định Mệnh."""
    return send_from_directory(FRONTEND_DIR, "marriage.html")


@app.get("/css/<path:filename>")
def css(filename: str) -> Response:
    """Phục vụ file CSS."""
    return send_from_directory(FRONTEND_DIR / "css", filename)


@app.get("/js/<path:filename>")
def js(filename: str) -> Response:
    """Phục vụ file JavaScript."""
    return send_from_directory(FRONTEND_DIR / "js", filename)


@app.get("/assets/<path:filename>")
def assets(filename: str) -> Response:
    """Phục vụ ảnh và tài nguyên tĩnh."""
    return send_from_directory(FRONTEND_DIR / "assets", filename)


if __name__ == "__main__":
    # Chỉ nghe trên máy cục bộ và tắt debug mặc định vì lá số có thông tin cá nhân.
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5057")),
            debug=os.getenv("FLASK_DEBUG") == "1")
