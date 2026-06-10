from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


DOCROOT = Path(
    "/Users/oceanblue/Desktop/MONEY/[ 사업 ]/운영/피클볼/제조사_디자인_지시서_2026-06-03"
)
DELIVERY = DOCROOT / "03_제조사_전달용"
REF = DELIVERY / "reference_images"
LOGO = DELIVERY / "logo_assets"

MAIN = HexColor("#f5b7c1")
ACCENT = HexColor("#AB4142")
OFFWHITE = HexColor("#F8F8F4")
INK = HexColor("#2D2527")
MUTED = HexColor("#716367")
LINE = HexColor("#E7D1D4")
SOFT = HexColor("#FFF4F6")

FONT = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
pdfmetrics.registerFont(TTFont("AppleGothic", FONT))
pdfmetrics.registerFont(TTFont("AppleGothicBold", FONT))


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Normal"],
            fontName="AppleGothicBold",
            fontSize=22,
            leading=30,
            textColor=INK,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName="AppleGothic",
            fontSize=10,
            leading=15,
            textColor=MUTED,
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Normal"],
            fontName="AppleGothicBold",
            fontSize=15,
            leading=21,
            textColor=ACCENT,
            spaceBefore=8,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Normal"],
            fontName="AppleGothicBold",
            fontSize=11,
            leading=16,
            textColor=INK,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="AppleGothic",
            fontSize=9,
            leading=14,
            textColor=INK,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="AppleGothic",
            fontSize=7.4,
            leading=11,
            textColor=MUTED,
            spaceAfter=3,
        ),
        "table": ParagraphStyle(
            "table",
            parent=base["Normal"],
            fontName="AppleGothic",
            fontSize=8,
            leading=12,
            textColor=INK,
        ),
        "table_bold": ParagraphStyle(
            "table_bold",
            parent=base["Normal"],
            fontName="AppleGothicBold",
            fontSize=8,
            leading=12,
            textColor=INK,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontName="AppleGothic",
            fontSize=7.5,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=3,
        ),
        "mark": ParagraphStyle(
            "mark",
            parent=base["Normal"],
            fontName="AppleGothicBold",
            fontSize=14,
            leading=19,
            textColor=ACCENT,
            alignment=TA_CENTER,
        ),
    }


def p(text, style):
    return Paragraph(text, style)


def img(path, max_w, max_h):
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def table(data, widths, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "AppleGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "AppleGothicBold"),
        ]
    t.setStyle(TableStyle(commands))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 15 * mm, A4[0] - doc.rightMargin, 15 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("AppleGothic", 7.5)
    canvas.drawString(doc.leftMargin, 9.5 * mm, "ITTEMMALL design instruction / updated accent #AB4142")
    canvas.drawRightString(A4[0] - doc.rightMargin, 9.5 * mm, str(canvas.getPageNumber()))
    canvas.restoreState()


KR = {
    "title": "ITTEMMALL 피클볼 패들 디자인 지시서",
    "subtitle": "제조사 샘플 시안 및 생산 협의용 / 포인트 컬러 업데이트: #AB4142",
    "notice_h": "중요 안내 / 기밀 및 상표권 보호",
    "notice": [
        "ITTEMMALL는 등록된 상표입니다.",
        "본 디자인 지시서, 로고, 이미지 및 관련 자료는 ITTEMMALL의 사전 서면 동의 없이 외부로 유출하거나, 복사하거나, 재사용하거나, 제3자에게 제공할 수 없습니다.",
        "무단 유출, 도용, 복제, 재사용 또는 제3자 제공이 확인될 경우 법적 조치를 취할 수 있습니다.",
    ],
    "colors": [
        ["역할", "색상 코드", "사용 위치"],
        ["대표 컬러", "#f5b7c1", "패들면 배경"],
        ["포인트 색", "#AB4142", "ITTEMMALL 로고, 문구, 버트캡, 엣지가드 문구"],
        ["흰색 계열", "#F8F8F4", "엣지가드, 흰색 마감 부분"],
    ],
    "no_extra": "위 세 가지 색상 외의 다른 제품 색상은 임의로 추가하지 마십시오.",
    "overall": [
        "전체적으로 깨끗하고 부드러운 핑크색 패들 느낌을 원합니다.",
        "패들면은 #f5b7c1 색상을 기준으로 합니다.",
        "ITTEMMALL 로고와 문구는 #AB4142 색상을 사용합니다.",
        "엣지가드는 흰색 계열 #F8F8F4 느낌으로 제작합니다.",
        "그립은 딸기우유 느낌의 무광 핑크 계열을 선호합니다.",
        "전체 디자인은 미니멀하고 깔끔한 방향으로 제작해주십시오. 과한 장식, 추가 색상, 강한 패턴은 넣지 마십시오.",
    ],
    "face": [
        "패들면 전체 색상은 #f5b7c1 입니다.",
        "ITTEMMALL 로고, 브랜드명, 버전명 등 주요 텍스트는 #AB4142 색상을 사용합니다.",
        "로고의 비율을 임의로 변형하지 마십시오.",
        "텍스트 간격과 배치는 참고 이미지의 느낌을 기준으로 하되, 제조사 실제 패들 형태에 맞춰 자연스럽게 조정해주십시오.",
        "실물 샘플 제작 전에 반드시 디지털 목업 또는 시안을 먼저 보내주십시오.",
    ],
    "grip": [
        "그립은 파스텔 핑크 또는 딸기우유 느낌의 색상을 원합니다.",
        "무광 느낌의 그립을 선호합니다.",
        "그립 마감 테이프도 그립과 같거나 매우 가까운 색상을 사용해주십시오.",
        "너무 어둡거나 강한 패턴의 그립은 사용하지 마십시오.",
    ],
    "grip_links": [
        "https://www.kuckrejas.com/product/trident-pickleball-paddle-grip-pastel-pink/",
        "https://www.walmart.com/ip/Yalla-Pickle-Grips-Pickleball-Paddle-Grip-Tape-Overgrip-for-Pickleball-Racket-Easy-Application-Paddle-Grip-Wrap-2-Pack/6361769241",
        "https://bodhiperformance.com/products/bodhi-grips-premium-pickleball-overgrips?variant=51587923050808",
    ],
    "butt": [
        "버트캡 외곽 둘레는 흰색 계열로 마감합니다.",
        "버트캡 중앙 색상은 #AB4142 버건디 색상을 기준으로 합니다.",
        "버트캡에는 아래 문구를 넣습니다.",
    ],
    "edge": [
        "엣지가드는 흰색 계열 #F8F8F4 색상을 기준으로 합니다.",
        "엣지가드에 아래 문구를 인쇄할 수 있는지 확인해주십시오.",
        "ITTEMMALL | PLAY BEAUTIFULLY",
        "문구 색상은 #AB4142 입니다.",
        "엣지가드 문구 인쇄 가능 여부, 최소 글자 크기, 안전 인쇄 영역을 알려주십시오.",
    ],
    "logo": [
        "첨부된 PNG 이미지는 로고 및 텍스트 참고 자료입니다.",
        "PNG 파일로 생산이 가능한지 확인해주십시오.",
        "인쇄 품질을 위해 AI, PDF, SVG 등 벡터 파일이 필요하다면 알려주십시오.",
        "로고의 비율, 자간, 형태를 임의로 변경하지 마십시오.",
    ],
    "checks": [
        "제품에 #f5b7c1, #AB4142, #F8F8F4 세 가지 색상만 사용할 수 있는가?",
        "정확한 패들 외곽 템플릿을 제공할 수 있는가?",
        "손잡이, 목 부분, 엣지가드, 인쇄 가능 안전 영역이 포함된 템플릿을 제공할 수 있는가?",
        "패들면 전체를 #f5b7c1 색상으로 제작할 수 있는가?",
        "ITTEMMALL 로고와 문구를 #AB4142 색상으로 인쇄할 수 있는가?",
        "무광 핑크 그립 제작이 가능한가?",
        "그립 마감 테이프도 같은 계열 색상으로 제작 가능한가?",
        "엣지가드에 ITTEMMALL | PLAY BEAUTIFULLY 문구 인쇄가 가능한가?",
        "실물 샘플 제작 전 디지털 목업 또는 시안을 먼저 제공할 수 있는가?",
        "ITTEMMALL 로고와 디자인 자료를 외부로 유출하거나 제3자에게 공유하지 않을 수 있는가?",
    ],
}


EN = {
    "title": "ITTEMMALL Pickleball Paddle Design Instructions",
    "subtitle": "For manufacturer sample proof and production discussion / Accent color update: #AB4142",
    "notice_h": "Important Notice / Confidentiality and Trademark Protection",
    "notice": [
        "ITTEMMALL is a registered trademark.",
        "This design instruction, logo, images, and related materials must not be disclosed externally, copied, reused, or provided to any third party without ITTEMMALL's prior written consent.",
        "If unauthorized disclosure, misuse, copying, reuse, or third-party sharing is confirmed, legal action may be taken.",
    ],
    "colors": [
        ["Role", "Color Code", "Usage"],
        ["Main color", "#f5b7c1", "Paddle face background"],
        ["Accent color", "#AB4142", "ITTEMMALL logo, text, butt cap, edge guard text"],
        ["Off-white", "#F8F8F4", "Edge guard and white trim areas"],
    ],
    "no_extra": "Do not add any other product colors beyond these three colors.",
    "overall": [
        "We want a clean, soft pink paddle look overall.",
        "The paddle face should be based on #f5b7c1.",
        "The ITTEMMALL logo and text should use #AB4142.",
        "The edge guard should have an off-white #F8F8F4 feel.",
        "The grip should be a matte pink tone with a strawberry-milk feel.",
        "Please keep the overall design minimal and clean. Do not add excessive decoration, additional colors, or strong patterns.",
    ],
    "face": [
        "The full paddle face color is #f5b7c1.",
        "The ITTEMMALL logo, brand name, version name, and other main text should use #AB4142.",
        "Do not distort or alter the logo proportions.",
        "Use the reference image as the direction for spacing and placement, but adjust naturally to fit the manufacturer's actual paddle shape.",
        "Please send a digital mockup or proof before producing the physical sample.",
    ],
    "grip": [
        "The grip should be pastel pink or a strawberry-milk pink tone.",
        "A matte grip feel is preferred.",
        "The grip finishing tape should use the same or a very similar color as the grip.",
        "Do not use a grip that is too dark or has a visually strong pattern.",
    ],
    "grip_links": KR["grip_links"],
    "butt": [
        "The outer ring of the butt cap should be finished in an off-white tone.",
        "The center color of the butt cap should be based on #AB4142 burgundy.",
        "Please place the following text on the butt cap:",
    ],
    "edge": [
        "The edge guard should be based on the off-white #F8F8F4 color.",
        "Please confirm whether the following text can be printed on the edge guard:",
        "ITTEMMALL | PLAY BEAUTIFULLY",
        "The text color is #AB4142.",
        "Please let us know whether edge guard text printing is possible, the minimum printable text size, and the safe print area.",
    ],
    "logo": [
        "The attached PNG images are logo and text reference assets.",
        "Please confirm whether production is possible with the PNG files.",
        "If AI, PDF, SVG, or another vector file is required for print quality, please let us know.",
        "Do not alter the logo proportions, letter spacing, or shape.",
    ],
    "checks": [
        "Can the product use only the three colors #f5b7c1, #AB4142, and #F8F8F4?",
        "Can you provide the exact paddle outline template?",
        "Can you provide a template including the handle, throat area, edge guard, and printable safe area?",
        "Can the full paddle face be produced in #f5b7c1?",
        "Can the ITTEMMALL logo and text be printed in #AB4142?",
        "Can you produce a matte pink grip?",
        "Can the grip finishing tape also be produced in a similar color tone?",
        "Can ITTEMMALL | PLAY BEAUTIFULLY be printed on the edge guard?",
        "Can you provide a digital mockup or proof before producing the physical sample?",
        "Can you keep the ITTEMMALL logo and design materials confidential and not disclose or share them with any third party?",
    ],
}


def add_paragraphs(story, items, style):
    for item in items:
        story.append(p(item, style))


def build_pdf(content, out_path):
    s = make_styles()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=23 * mm,
        title=content["title"],
        author="ITTEMMALL",
    )
    story = []
    story += [p(content["title"], s["title"]), p(content["subtitle"], s["subtitle"])]
    story += [p(content["notice_h"], s["h1"])]
    notice_table = Table([[p("<br/>".join(content["notice"]), s["body"])]], colWidths=[159 * mm])
    notice_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story += [notice_table, Spacer(1, 8), p("1. Core Colors" if content is EN else "1. 핵심 색상", s["h1"])]
    color_rows = [[p(cell, s["table_bold"] if i == 0 else s["table"]) for cell in row] for i, row in enumerate(content["colors"])]
    story += [table(color_rows, [34 * mm, 35 * mm, 90 * mm]), p(content["no_extra"], s["body"])]

    story += [PageBreak()]
    story += [p("2. Overall Design Direction" if content is EN else "2. 전체 디자인 방향", s["h1"])]
    story += [img(REF / "reference_01_full_example.png", 154 * mm, 115 * mm)]
    add_paragraphs(story, content["overall"], s["body"])

    story += [PageBreak()]
    story += [p("3. Paddle Face" if content is EN else "3. 패들면", s["h1"])]
    story += [img(REF / "reference_02_face_color_logo.png", 154 * mm, 115 * mm)]
    add_paragraphs(story, content["face"], s["body"])

    story += [PageBreak()]
    story += [p("4. Handle / Grip" if content is EN else "4. 손잡이 / 그립", s["h1"])]
    story += [img(REF / "reference_03_grip.png", 154 * mm, 95 * mm)]
    add_paragraphs(story, content["grip"], s["body"])
    story += [p("Grip reference sites:" if content is EN else "그립 참고 사이트:", s["h2"])]
    for link in content["grip_links"]:
        story.append(p(link, s["small"]))

    story += [PageBreak()]
    story += [p("5. Butt Cap" if content is EN else "5. 버트캡", s["h1"])]
    story += [img(REF / "reference_04_butt_cap.png", 154 * mm, 82 * mm)]
    add_paragraphs(story, content["butt"], s["body"])
    story += [Spacer(1, 5), p("M A R C E", s["mark"])]
    story += [Spacer(1, 12), p("6. Edge Guard" if content is EN else "6. 엣지가드", s["h1"])]
    story += [img(REF / "reference_05_edge_guard_text.png", 154 * mm, 72 * mm)]
    add_paragraphs(story, content["edge"], s["body"])

    story += [PageBreak()]
    story += [p("7. Logo / Text Image Assets" if content is EN else "7. 로고 / 텍스트 이미지 자료", s["h1"])]
    logo_grid = Table(
        [
            [img(LOGO / "logo_01.png", 45 * mm, 32 * mm), img(LOGO / "logo_02.png", 45 * mm, 32 * mm), img(LOGO / "logo_03.png", 45 * mm, 32 * mm)],
            [p("Logo image 1" if content is EN else "로고 이미지 1", s["caption"]), p("Logo image 2" if content is EN else "로고 이미지 2", s["caption"]), p("Logo image 3" if content is EN else "로고 이미지 3", s["caption"])],
        ],
        colWidths=[53 * mm, 53 * mm, 53 * mm],
        hAlign="LEFT",
    )
    logo_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story += [logo_grid, Spacer(1, 8)]
    add_paragraphs(story, content["logo"], s["body"])

    story += [PageBreak()]
    story += [p("8. Manufacturer Confirmation Request" if content is EN else "8. 제조사 확인 요청", s["h1"])]
    rows = [[p("[ ] " + item if content is EN else "□ " + item, s["table"])] for item in content["checks"]]
    story += [table(rows, [159 * mm], header=False)]

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(out_path)


def main():
    build_pdf(KR, DELIVERY / "ITTEMMALL_Pickleball_Paddle_Design_Instructions_KR_Final.pdf")
    build_pdf(EN, DELIVERY / "ITTEMMALL_Pickleball_Paddle_Design_Instructions_EN_Final.pdf")
    package_dir = DELIVERY / "ITTEMMALL_Manufacturer_EN_Package_2026-06-03"
    if package_dir.exists():
        build_pdf(EN, package_dir / "ITTEMMALL_Pickleball_Paddle_Design_Instructions_EN_Final.pdf")


if __name__ == "__main__":
    main()
