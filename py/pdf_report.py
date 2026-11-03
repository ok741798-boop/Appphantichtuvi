"""Xuất báo cáo lá số ra PDF bằng reportlab.

Font mặc định của reportlab không có đủ dấu tiếng Việt, nên cần dùng một font
TTF của hệ điều hành. Có thể chỉ định font bằng biến môi trường PDF_FONT_PATH
và PDF_FONT_BOLD_PATH.
"""

import os
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_CANDIDATES: List[Tuple[str, str]] = [
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
]

FONT = "TuViFont"
FONT_BOLD = "TuViFontBold"

GOLD = colors.HexColor("#92700c")
RED = colors.HexColor("#b91c1c")
BLUE = colors.HexColor("#1d4ed8")
GREY = colors.HexColor("#6b7280")

DISCLAIMER = ("Kết quả mang tính tham khảo, không thay thế quyết định thực tế. "
              "Tử vi chỉ là một góc nhìn, không phải định mệnh.")

ASPECT_TITLES = [("career", "Sự nghiệp"), ("wealth", "Tài lộc"),
                 ("love", "Tình cảm"), ("health", "Sức khỏe")]

# Vị trí 12 cung trên bảng 4x4, theo thứ tự (hàng, cột) của Địa Chi Tý -> Hợi.
GRID_POSITIONS = [(3, 2), (3, 1), (3, 0), (2, 0), (1, 0), (0, 0),
                  (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3)]


class FontNotFoundError(RuntimeError):
    """Máy chủ không có font TTF hỗ trợ tiếng Việt."""


def _find_fonts() -> Optional[Tuple[str, str]]:
    """Tìm cặp font thường/đậm: ưu tiên biến môi trường, sau đó tới font hệ thống."""
    custom = os.getenv("PDF_FONT_PATH")
    candidates = list(FONT_CANDIDATES)
    if custom:
        candidates.insert(0, (custom, os.getenv("PDF_FONT_BOLD_PATH", custom)))
    for regular, bold in candidates:
        if Path(regular).is_file() and Path(bold).is_file():
            return regular, bold
    return None


def _register_fonts() -> None:
    """Đăng ký font với reportlab, chỉ cần làm một lần."""
    if FONT in pdfmetrics.getRegisteredFontNames():
        return
    fonts = _find_fonts()
    if fonts is None:
        raise FontNotFoundError(
            "Không tìm thấy font tiếng Việt. Hãy đặt PDF_FONT_PATH trỏ tới một file .ttf."
        )
    pdfmetrics.registerFont(TTFont(FONT, fonts[0]))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, fonts[1]))


def _styles() -> Dict[str, ParagraphStyle]:
    """Tạo các kiểu chữ dùng trong báo cáo."""
    return {
        "title": ParagraphStyle("title", fontName=FONT_BOLD, fontSize=20, leading=26,
                                textColor=GOLD, alignment=1),
        "subtitle": ParagraphStyle("subtitle", fontName=FONT, fontSize=10, leading=14,
                                   textColor=GREY, alignment=1),
        "h2": ParagraphStyle("h2", fontName=FONT_BOLD, fontSize=13, leading=18, textColor=GOLD,
                             spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName=FONT_BOLD, fontSize=10.5, leading=14, spaceBefore=6),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=10, leading=15),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=7.5, leading=9.5),
        "center": ParagraphStyle("center", fontName=FONT, fontSize=9, leading=13, alignment=1),
    }


def _font(text: str, color: colors.Color, bold: bool = False) -> str:
    """Bọc văn bản đã escape bằng thẻ màu và font của reportlab."""
    name = FONT_BOLD if bold else FONT
    return f'<font name="{name}" color="{color.hexval().replace("0x", "#")}">{escape(text)}</font>'


def _palace_cell(palace: Dict, style: ParagraphStyle) -> Paragraph:
    """Dựng nội dung một ô cung trên bảng lá số."""
    hoa_by_star = {h["star"]: h["hoa"] for h in palace["tu_hoa"]}

    def star_label(name: str) -> str:
        """Ghép tên sao với Hóa của sao đó nếu có."""
        return f"{name} ({hoa_by_star[name]})" if name in hoa_by_star else name

    marks = ["THÂN"] if palace["is_than"] else []
    marks += [mark for mark, on in (("Tuần", palace["tuan"]), ("Triệt", palace["triet"])) if on]
    header = f"{palace['name'].upper()} · {palace['can']} {palace['position']}"
    lines = [_font(header, GOLD, bold=True)]
    if palace["chinh_tinh"]:
        lines.append(_font(", ".join(star_label(s) for s in palace["chinh_tinh"]), RED, bold=True))
    if palace["phu_tinh"]:
        lines.append(_font(", ".join(star_label(s) for s in palace["phu_tinh"]), BLUE))
    footer = f"Đại vận {palace['dai_van_age']}"
    if marks:
        footer += " · " + ", ".join(marks)
    lines.append(_font(footer, GREY))
    return Paragraph("<br/>".join(lines), style)


def _chart_table(chart: Dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """Dựng bảng lá số 4x4, ô giữa 2x2 chứa thông tin chung."""
    grid: List[List[object]] = [["" for _ in range(4)] for _ in range(4)]
    for palace in chart["cung"]:
        row, col = GRID_POSITIONS[palace["position_index"]]
        grid[row][col] = _palace_cell(palace, styles["cell"])

    center_lines = [
        chart["am_duong"],
        f"Bản mệnh: {chart['ban_menh']}",
        chart["cuc"]["name"],
        f"Mệnh chủ: {chart['menh_chu']}",
        f"Thân chủ: {chart['than_chu']}",
        f"Thân cư {chart['than_cu']}",
    ]
    grid[1][1] = Paragraph("<br/>".join(escape(line) for line in center_lines), styles["center"])

    table = Table(grid, colWidths=[44 * mm] * 4, rowHeights=[42 * mm] * 4)
    table.setStyle(TableStyle([
        ("SPAN", (1, 1), (2, 2)),
        ("GRID", (0, 0), (-1, -1), 0.6, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("VALIGN", (1, 1), (2, 2), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _lunar_label(chart: Dict) -> str:
    """Mô tả ngày sinh âm lịch."""
    lunar = chart["lunar"]
    leap = " nhuận" if lunar["is_leap"] else ""
    return (f"{lunar['lunar_day']}/{lunar['lunar_month']}{leap} năm {chart['can_chi']['year']}, "
            f"giờ {chart['can_chi']['hour']}")


def _draw_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    """Vẽ disclaimer ở chân mọi trang."""
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0] / 2, 8 * mm, DISCLAIMER)
    canvas.restoreState()


def build_pdf(chart: Dict, current: Dict, forecast: List[Dict]) -> bytes:
    """Tạo báo cáo PDF gồm lá số, vận hạn năm nay và dự đoán 10 năm."""
    _register_fonts()
    styles = _styles()
    info = chart["info"]
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                                 topMargin=14 * mm, bottomMargin=16 * mm,
                                 title=f"Lá số tử vi - {info['full_name']}")

    story: List[object] = [
        Paragraph("Lá Số Tử Vi", styles["title"]),
        Paragraph(escape(f"{info['full_name']} · {info['gender']} · "
                         f"{info['day']:02d}/{info['month']:02d}/{info['year']}"),
                  styles["subtitle"]),
        Paragraph(escape(f"Âm lịch: {_lunar_label(chart)}"), styles["subtitle"]),
        Spacer(1, 6 * mm),
        _chart_table(chart, styles),
        PageBreak(),
        Paragraph(f"Vận hạn năm {current['year']} ({current['can_chi']})", styles["h2"]),
        Paragraph(escape(current["summary"]), styles["body"]),
    ]
    for key, title in ASPECT_TITLES:
        story.append(Paragraph(title, styles["h3"]))
        story.append(Paragraph(escape(current[key]), styles["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Dự đoán 10 năm", styles["h2"]))
    for item in forecast:
        story.append(Paragraph(f"{item['year']} · {item['can_chi']} · {item['rating']}/10",
                               styles["h3"]))
        story.append(Paragraph(escape(item["summary"]), styles["body"]))

    document.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()
