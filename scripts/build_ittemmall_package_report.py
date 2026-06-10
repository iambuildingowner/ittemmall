from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path("/Users/oceanblue/Desktop/MONEY/개발/07_웹·서비스 제작/페이크도어")
OUT = ROOT / "피클볼파트" / "패키지자료" / "ITTEMMALL_패키지_보고서_2026-06-03"
IMG = OUT / "images"
COMP = OUT / "competitor_examples"
PDF = OUT / "ITTEMMALL_패키지_리서치_보고서_2026-06-03.pdf"

FONT_REGULAR = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

pdfmetrics.registerFont(TTFont("AppleGothic", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("AppleGothicBold", FONT_BOLD))

MAIN = HexColor("#f5b7c1")
ACCENT = HexColor("#AB4142")
CREAM = HexColor("#F8F8F4")
INK = HexColor("#2E2528")
MUTED = HexColor("#76686C")
LINE = HexColor("#E7D6D9")
SOFT = HexColor("#FFF4F6")


def p(text, style):
    return Paragraph(text, style)


def img_flow(path, max_w, max_h):
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.7)
    canvas.line(doc.leftMargin, 16 * mm, A4[0] - doc.rightMargin, 16 * mm)
    canvas.setFont("AppleGothic", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 10 * mm, "ITTEMMALL package research / 2026-06-03")
    canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, str(canvas.getPageNumber()))
    canvas.restoreState()


def make_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=styles["Normal"],
            fontName="AppleGothicBold",
            fontSize=24,
            leading=31,
            textColor=INK,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=styles["Normal"],
            fontName="AppleGothic",
            fontSize=11,
            leading=17,
            textColor=MUTED,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=styles["Normal"],
            fontName="AppleGothicBold",
            fontSize=16,
            leading=22,
            textColor=ACCENT,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=styles["Normal"],
            fontName="AppleGothicBold",
            fontSize=12,
            leading=17,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=styles["Normal"],
            fontName="AppleGothic",
            fontSize=9.7,
            leading=15,
            textColor=INK,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small",
            parent=styles["Normal"],
            fontName="AppleGothic",
            fontSize=8,
            leading=12,
            textColor=MUTED,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=styles["Normal"],
            fontName="AppleGothic",
            fontSize=8.2,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=4,
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=styles["Normal"],
            fontName="AppleGothicBold",
            fontSize=11,
            leading=17,
            textColor=ACCENT,
            alignment=TA_LEFT,
        ),
        "table": ParagraphStyle(
            "table",
            parent=styles["Normal"],
            fontName="AppleGothic",
            fontSize=8,
            leading=12,
            textColor=INK,
        ),
        "table_bold": ParagraphStyle(
            "table_bold",
            parent=styles["Normal"],
            fontName="AppleGothicBold",
            fontSize=8,
            leading=12,
            textColor=INK,
        ),
    }


def table(data, widths, header=True, font_size=8):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "AppleGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 4),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "AppleGothicBold"),
        ]
    t.setStyle(TableStyle(commands))
    return t


def build():
    s = make_styles()
    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=23 * mm,
        title="ITTEMMALL 패키지 리서치 보고서",
        author="Codex",
    )

    story = []

    selected = IMG / "concept_02_selected_court_flatlay.png"
    c1 = IMG / "concept_01_unboxing_box.png"
    c3 = IMG / "concept_03_premium_rigid_box.png"
    comp_sheet = COMP / "competitor_examples_contact_sheet.jpg"

    story += [
        p("ITTEMMALL 패키지 리서치 보고서", s["title"]),
        p("피클볼 패들 초도 패키지 방향 제안 / 제조사 협의 전 내부 판단 자료", s["subtitle"]),
    ]

    lead = Table(
        [
            [
                p("최종 추천", s["callout"]),
                p(
                    "2안: 오프화이트 배송 박스 + 핑크 티슈 + 버건디 스티커 + 인서트 카드 + 재사용 가능한 핑크 패들 커버",
                    s["body"],
                ),
            ],
            [
                p("브랜드 기준", s["callout"]),
                p(
                    "LA clean girl, Alo/Lululemon 감성, 20대 후반~30대 초반 여성 타깃. 예쁜 물건을 통해 운동하고 싶은 마음을 만드는 방향.",
                    s["body"],
                ),
            ],
        ],
        colWidths=[31 * mm, 128 * mm],
        hAlign="LEFT",
    )
    lead.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story += [lead, Spacer(1, 9)]
    story += [img_flow(selected, 159 * mm, 125 * mm), p("선정 이미지: 2안. 실제 고객이 받을 수 있는 배송/언박싱 구조와 브랜드 감성이 가장 잘 맞습니다.", s["caption"])]

    story += [
        Spacer(1, 8),
        p("1. 브랜드와 패키지의 역할", s["h1"]),
        p(
            "ITTEMMALL의 사명은 “아름다움을 통해 운동하고 싶은 마음을 만들고, 그 움직임으로 건강한 몸과 삶을 만든다”입니다. 따라서 패키지는 단순히 제품을 싸는 박스가 아니라, 고객이 제품을 받은 순간 ‘운동하러 나가고 싶다’는 감정을 만들어야 합니다.",
            s["body"],
        ),
        p(
            "현재 브랜드 초입에서는 과한 프리미엄 선물박스보다, 비용과 배송 안정성을 지키면서도 고객이 계속 들고 다니는 재사용 커버를 브랜드 자산으로 만드는 것이 더 효율적입니다.",
            s["body"],
        ),
    ]

    color_data = [
        [p("구분", s["table_bold"]), p("색상", s["table_bold"]), p("사용 위치", s["table_bold"])],
        [p("대표 컬러", s["table"]), p("#f5b7c1", s["table"]), p("패들면, 티슈, 커버 안감 또는 포인트 면", s["table"])],
        [p("포인트 색", s["table"]), p("#AB4142", s["table"]), p("로고, 스티커, 카드 문구, 작은 장식선", s["table"])],
        [p("흰색 계열", s["table"]), p("#F8F8F4", s["table"]), p("배송 박스, 엣지가드, 외부 패키지 바탕", s["table"])],
    ]
    story += [Spacer(1, 6), table(color_data, [30 * mm, 31 * mm, 98 * mm])]

    principle_data = [
        [p("원칙", s["table_bold"]), p("적용 방향", s["table_bold"])],
        [
            p("버리는 박스보다<br/>들고 다니는 자산", s["table_bold"]),
            p("고객이 한 번 열고 버리는 박스보다, 코트에 반복적으로 들고 다니는 패들 커버/백을 더 중요하게 봅니다.", s["table"]),
        ],
        [
            p("핑크는 스포츠 맥락 안에서", s["table_bold"]),
            p("핑크만 과하게 쓰면 유치해질 수 있으므로, 블루 코트·오프화이트·버건디를 함께 써서 운동성과 세련됨을 유지합니다.", s["table"]),
        ],
        [
            p("초도는 가볍고 빠르게", s["table_bold"]),
            p("초도 MOQ 50~100개에서는 리지드 박스보다 배송 박스, 티슈, 스티커, 카드, 커버의 조합이 더 합리적입니다.", s["table"]),
        ],
        [
            p("브랜드 언어는 짧게", s["table_bold"]),
            p("문구는 Beauty makes you move. / PLAY BEAUTIFULLY처럼 짧고 선명하게 가져갑니다.", s["table"]),
        ],
    ]
    story += [Spacer(1, 10), p("패키지 설계 원칙", s["h2"]), table(principle_data, [38 * mm, 121 * mm])]

    story += [PageBreak()]
    story += [p("2. 타사 패키징 예시 6개", s["h1"])]
    story += [
        p(
            "타사 사례를 보면, 좋은 패키지는 박스 하나로 끝나지 않습니다. 초급 세트는 ‘바로 시작 가능한 구성’을 팔고, 감성 브랜드는 컬러와 세트감을 팔며, 퍼포먼스 브랜드는 보호 케이스를 강조합니다.",
            s["body"],
        ),
        img_flow(comp_sheet, 158 * mm, 170 * mm),
        p("타사 참고 예시 6개. 왼쪽부터 Nettie 세트, Recess 핑크 세트, Recess Weekend Set, Nettie Sport Tote, JOOLA Pro Case, Selkirk SLK Case.", s["caption"]),
        Spacer(1, 8),
    ]

    comp_table = [
        [p("브랜드/제품", s["table_bold"]), p("패키징 방식", s["table_bold"]), p("ITTEMMALL 적용 판단", s["table_bold"])],
        [
            p("Nettie<br/>Recreation Set", s["table_bold"]),
            p("2개 패들, 2개 공, 2개 손목밴드를 한 세트로 구성. 상자를 여는 순간 컬러감과 세트감이 강합니다.", s["table"]),
            p("가장 참고 가치가 높습니다. ITTEMMALL도 ‘받자마자 예쁜 운동 세트’처럼 보여야 합니다.", s["table"]),
        ],
        [
            p("Recess<br/>Pink Rec Set", s["table_bold"]),
            p("입문자를 위한 2개 패들 + 3개 공 세트. 핑크 컬러 자체가 구매 이유가 되도록 구성합니다.", s["table"]),
            p("ITTEMMALL의 첫 진입 고객과 잘 맞습니다. 핑크 패들 단품도 충분히 강한 상품이 될 수 있습니다.", s["table"]),
        ],
        [
            p("Recess<br/>Weekend Set", s["table_bold"]),
            p("4개 패들, 코트백, 공, 패들 커버까지 묶은 번들형 구성입니다.", s["table"]),
            p("초도에는 과합니다. 다만 이후 ITTEMMALL 세트 상품, 커플/친구용 세트로 확장하기 좋습니다.", s["table"]),
        ],
        [
            p("Nettie<br/>Sport Tote", s["table_bold"]),
            p("패들 6개와 물병, 공, 수건 등을 넣는 스포츠 토트. 패키지를 넘어 ‘들고 다니는 브랜드 자산’입니다.", s["table"]),
            p("장기적으로 매우 중요합니다. ITTEMMALL는 패들 다음 상품으로 토트/백 라인을 고려해야 합니다.", s["table"]),
        ],
        [
            p("JOOLA<br/>Pro Case", s["table_bold"]),
            p("하드쉘 케이스로 패들 면과 손잡이 전체를 보호하는 퍼포먼스 중심 패키징입니다.", s["table"]),
            p("기능 참고용입니다. ITTEMMALL 감성과는 다소 거칠지만, 보호 구조는 배울 만합니다.", s["table"]),
        ],
        [
            p("Selkirk<br/>SLK Case", s["table_bold"]),
            p("비교적 단순한 보호 케이스. 고가 박스보다 실사용 보호에 집중합니다.", s["table"]),
            p("초도 패들 커버 설계 참고에 좋습니다. 단, ITTEMMALL는 컬러와 촉감을 더 예쁘게 잡아야 합니다.", s["table"]),
        ],
    ]
    story += [table(comp_table, [34 * mm, 67 * mm, 58 * mm])]

    story += [
        Spacer(1, 10),
        p("ITTEMMALL에 가장 좋은 방향성", s["h2"]),
        p(
            "ITTEMMALL는 Nettie/Recess 쪽의 감성 세트 전략을 가져오되, JOOLA/Selkirk의 보호 기능을 최소한으로 흡수하는 방향이 좋습니다. 즉 ‘예쁜 상자’보다 ‘오프화이트 배송 박스 + 핑크 언박싱 + 재사용 패들 커버’가 정답에 가깝습니다.",
            s["body"],
        ),
        p(
            "초도 50~100개 기준에서는 리지드 선물박스보다 얇은 보호 커버가 훨씬 합리적입니다. 커버는 고객이 버리지 않고 코트에 들고 다니기 때문에, 광고비를 쓰지 않아도 반복 노출되는 브랜드 자산이 됩니다.",
            s["body"],
        ),
    ]

    story += [PageBreak()]
    story += [p("3. 생성 후보 비교", s["h1"])]

    thumbs = [
        [
            img_flow(c1, 49 * mm, 51 * mm),
            img_flow(selected, 49 * mm, 51 * mm),
            img_flow(c3, 49 * mm, 51 * mm),
        ],
        [
            p("1안: 언박싱 박스형", s["caption"]),
            p("2안: 코트 플랫레이형 / 최종 추천", s["caption"]),
            p("3안: 프리미엄 리지드 박스형", s["caption"]),
        ],
    ]
    image_grid = Table(thumbs, colWidths=[53 * mm, 53 * mm, 53 * mm], hAlign="LEFT")
    image_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [image_grid, Spacer(1, 10)]

    compare = [
        [p("안", s["table_bold"]), p("장점", s["table_bold"]), p("보류/선정 판단", s["table_bold"])],
        [
            p("1안", s["table_bold"]),
            p("감성적인 언박싱 분위기와 제품의 부드러운 핑크 톤이 잘 보입니다.", s["table"]),
            p("실제 배송 보호와 재사용 자산이 약합니다. 화보용 보조 컷으로 적합합니다.", s["table"]),
        ],
        [
            p("2안", s["table_bold"]),
            p("배송 박스, 티슈, 스티커, 카드, 패들 커버가 모두 보입니다. 코트 배경이 핑크를 유치하게 만들지 않고 스포츠 맥락을 살립니다.", s["table"]),
            p("초도 MOQ 50~100개 기준에서 가장 현실적입니다. 최종 추천안입니다.", s["table"]),
        ],
        [
            p("3안", s["table_bold"]),
            p("선물용으로 고급스럽고 프리미엄 인상이 강합니다.", s["table"]),
            p("리지드 박스는 단가와 부피 배송비 부담이 큽니다. 첫 물량보다는 기프트 에디션으로 보류가 좋습니다.", s["table"]),
        ],
    ]
    story += [table(compare, [16 * mm, 70 * mm, 73 * mm])]

    story += [
        Spacer(1, 9),
        p("판단", s["h2"]),
        p(
            "고객이 실제로 오래 보관하고 반복적으로 노출하는 것은 박스보다 패들 커버입니다. 그래서 초도 패키지는 박스를 비싸게 만드는 것보다, 오프화이트 배송 박스와 핑크 커버의 완성도를 높이는 방향이 더 좋습니다.",
            s["body"],
        ),
    ]

    story += [PageBreak()]
    story += [p("4. 추천 패키지 구성", s["h1"])]
    spec = [
        [p("구성품", s["table_bold"]), p("권장 사양", s["table_bold"]), p("이유", s["table_bold"])],
        [
            p("외부 박스", s["table_bold"]),
            p("무광 오프화이트 골판 배송 박스. 중앙에 작은 M A R C E 로고만 배치.", s["table"]),
            p("첫인상은 깨끗하게, 배송 보호는 현실적으로 가져갑니다.", s["table"]),
        ],
        [
            p("내부 티슈", s["table_bold"]),
            p("#f5b7c1 핑크 티슈 + #AB4142 원형 또는 타원형 스티커.", s["table"]),
            p("상자를 열었을 때 브랜드 컬러가 바로 들어옵니다.", s["table"]),
        ],
        [
            p("인서트 카드", s["table_bold"]),
            p("앞면: Beauty makes you move. / 뒷면: 브랜드 사명, 관리 안내, 첫 사용 안내.", s["table"]),
            p("브랜드 사명을 말로 설명하되, 과하게 장황하지 않게 정리합니다.", s["table"]),
        ],
        [
            p("패들 커버", s["table_bold"]),
            p("파스텔 핑크 또는 오프화이트 원단, 버건디 로고, 지퍼 또는 슬림 슬리브 형태.", s["table"]),
            p("고객이 코트에 들고 다니는 지속 노출 자산입니다. 가장 중요합니다.", s["table"]),
        ],
        [
            p("주의", s["table_bold"]),
            p("USA Pickleball Approved 마크 또는 인증 문구는 인증 전 사용하지 않습니다.", s["table"]),
            p("법적/인증 리스크를 줄입니다.", s["table"]),
        ],
    ]
    story += [table(spec, [28 * mm, 82 * mm, 49 * mm])]

    story += [
        Spacer(1, 10),
        p("권장 문구", s["h2"]),
        p("박스 외부: M A R C E", s["body"]),
        p("인서트 카드 앞면: Beauty makes you move.", s["body"]),
        p("인서트 카드 뒷면: 아름다움을 통해 운동하고 싶은 마음을 만들고, 그 움직임으로 건강한 몸과 삶을 만듭니다.", s["body"]),
        p("스티커: PLAY BEAUTIFULLY 또는 ITTEMMALL", s["body"]),
    ]

    cost = [
        [p("항목", s["table_bold"]), p("대략 단가 범위", s["table_bold"]), p("메모", s["table_bold"])],
        [p("배송 박스", s["table"]), p("700~1,800원", s["table"]), p("규격/인쇄 방식에 따라 변동", s["table"])],
        [p("티슈 + 스티커", s["table"]), p("300~700원", s["table"]), p("스티커는 소량 제작 가능성 높음", s["table"])],
        [p("인서트 카드", s["table"]), p("150~500원", s["table"]), p("양면 인쇄 기준", s["table"])],
        [p("패들 커버", s["table"]), p("2,000~4,500원", s["table"]), p("원단/지퍼/인쇄에 따라 가장 크게 변동", s["table"])],
        [p("합계", s["table_bold"]), p("약 3,000~7,500원", s["table_bold"]), p("초도 패키지 권장 범위", s["table_bold"])],
        [p("리지드 박스", s["table"]), p("5,000~12,000원+", s["table"]), p("부피 배송비까지 고려하면 초도에는 부담", s["table"])],
    ]
    story += [Spacer(1, 10), p("5. 예상 비용 감각", s["h1"]), table(cost, [40 * mm, 38 * mm, 81 * mm])]

    story += [PageBreak()]
    story += [p("6. 제조사 협의 체크리스트", s["h1"])]
    checklist = [
        [p("확인 항목", s["table_bold"]), p("질문", s["table_bold"])],
        [p("패들 커버", s["table_bold"]), p("핑크 또는 오프화이트 커버 제작 가능 여부, 원단 종류, 지퍼/슬리브 방식, MOQ, 단가", s["table"])],
        [p("박스", s["table_bold"]), p("패들 1개 기준 안전 배송 가능한 박스 규격, 오프화이트 인쇄 가능 여부, MOQ, 단가", s["table"])],
        [p("티슈/스티커", s["table_bold"]), p("#f5b7c1 티슈와 #AB4142 스티커 색상 매칭 가능 여부", s["table"])],
        [p("인서트 카드", s["table_bold"]), p("카드 동봉 가능 여부, 별도 인쇄/동봉 비용, 샘플 제작 가능 여부", s["table"])],
        [p("샘플", s["table_bold"]), p("패들 샘플과 패키지 샘플을 함께 받을 수 있는지, 가장 빠른 리드타임", s["table"])],
        [p("보안", s["table_bold"]), p("ITTEMMALL 로고/디자인 자료 외부 유출 및 제3자 공유 금지 확인", s["table"])],
    ]
    story += [table(checklist, [35 * mm, 124 * mm])]

    story += [
        Spacer(1, 10),
        p("진행 순서", s["h2"]),
        p("1. 제조사에 패들 정확한 템플릿과 패키지 제작 가능 범위를 요청합니다.", s["body"]),
        p("2. 패들 색상과 커버 소재를 먼저 확정합니다.", s["body"]),
        p("3. 오프화이트 배송 박스, 핑크 티슈, 버건디 스티커, 인서트 카드 샘플 견적을 받습니다.", s["body"]),
        p("4. 실물 샘플 수령 후 언박싱 사진과 영상 기준으로 최종 수정합니다.", s["body"]),
        p("5. 리지드 박스는 초도 반응 이후 기프트 세트 또는 프리미엄 에디션으로 검토합니다.", s["body"]),
        Spacer(1, 10),
        p("참고 및 생성 정보", s["h1"]),
        p("• Pinterest ITTEMMALL 보드 검토: https://kr.pinterest.com/staysiaofficial/%ED%94%BC%ED%81%B4%EB%B3%BC/", s["small"]),
        p("• Pinterest의 자동 추천 영역인 ‘이 보드를 위한 아이디어’는 사용자 저장 자료가 아니므로 판단에서 제외했습니다.", s["small"]),
        p("• 타사 참고: Nettie Recreation Pickleball Set 2-Pack, Nettie Sport Tote, Recess Pink Rec Set, Recess Weekend Set, JOOLA Pro Pickleball Paddle Case, Selkirk SLK Paddle Protective Case.", s["small"]),
        p("• 참고 URL: https://playnettie.com/products/the-nettie-set / https://playnettie.com/products/pickleball-tote-bag / https://clubrecess.com/products/pink-starter-set / https://clubrecess.com/products/sunday-set / https://joola.com/products/pro-pickleball-paddle-case / https://www.selkirk.com/products/slk-paddle-case", s["small"]),
        p("• 패키지 후보 이미지는 Codex 내부 image_gen 도구로 2026-06-03 생성했습니다.", s["small"]),
        p("• 최종 선택 이미지는 concept_02_selected_court_flatlay.png 입니다.", s["small"]),
    ]

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(PDF)


if __name__ == "__main__":
    build()
