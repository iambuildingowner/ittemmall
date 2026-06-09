import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = new URL("../output/", import.meta.url);

const scriptSections = [
  {
    no: "00",
    title: "상품 대표 이미지",
    image: "main.png",
    body: "상품 상세 상단 대표 이미지와 상품 리스트 썸네일에 사용합니다."
  },
  {
    no: "01",
    title: "넓게 막고, 빠르게 비우는 와이드 헤드밴드",
    image: "",
    body: "이마와 헤어라인을 넓게 감싸 러닝 중 흐르는 땀을 받아주고, 얇은 신축 원단으로 장시간 착용 부담을 낮췄습니다."
  },
  {
    no: "02",
    title: "땀이 흐르기 전에 먼저 받아주는 넓은 원단",
    image: "01-feature-detail.jpg",
    extraImage: "02-unclassified.gif",
    body: "와이드 폭의 원단이 운동 중 생기는 수분을 넓게 받아줍니다.\n눈가로 바로 흘러내리는 땀을 줄여 페이스에 더 오래 집중할 수 있습니다."
  },
  {
    no: "03",
    title: "머리부터 이마까지 넓은 면적을 커버하는 스포츠 헤드밴드",
    image: "",
    body: "와이드 폭으로 헤어라인과 이마를 안정적으로 감싸고, 러닝 중 눈가로 내려오는 땀을 줄이는 데 집중한 헤드웨어입니다.\n\n컬러\n블랙 / 화이트 / 딥그린\n\n사이즈\nFREE"
  },
  {
    no: "04",
    title: "와이드 폭이 얼굴 라인에 걸리는 느낌",
    image: "04-human-wearing.jpg",
    body: "넓은 폭이 이마를 안정적으로 덮어주고, 운동 중 머리카락이 내려오는 느낌을 줄여줍니다."
  },
  {
    no: "05",
    title: "운동용이지만 일상에도 무리 없는 실루엣",
    image: "05-human-wearing.jpg",
    body: "과하게 두꺼워 보이지 않는 라인으로 러닝, 헬스, 야외 활동까지 자연스럽게 이어집니다."
  },
  {
    no: "06",
    title: "Runnerwin 와이드 헤드밴드가 필요한 순간",
    image: "",
    body: "운동이나 야외 활동 중 이마를 넓게 커버하고 싶을 때.\n땀이 눈으로 바로 흐르는 불편을 줄이고 싶을 때.\n부드러운 안감으로 피부 자극 부담을 낮추고 싶을 때.\n땀과 수분을 빠르게 받아주는 넓은 흡수 면적이 필요할 때.\n반복 착용 후에도 손쉽게 세탁 관리하고 싶을 때."
  },
  {
    no: "07",
    title: "핵심 기능",
    image: "",
    body: "12cm 와이드 면적\n이마와 헤어라인을 넓게 덮어 땀 흐름을 늦춥니다.\n\n빠른 땀 흡수\n넓은 원단 면적으로 운동 중 수분을 빠르게 받아줍니다.\n\n야외 피부 보호\n햇빛이 강한 날에도 이마 주변 노출 부담을 줄입니다.\n\n시원한 터치감\n얇고 부드러운 원단감으로 여름 훈련에 맞춥니다.\n\n높은 신축성\n머리에 맞게 늘어나며 장시간 착용 압박을 낮춥니다."
  },
  {
    no: "08",
    title: "바깥은 통기성, 안쪽은 흡수감",
    image: "11-product-only.jpg",
    body: "바깥쪽은 열이 답답하게 고이지 않도록 가볍게, 피부에 닿는 안쪽은 땀을 받아주는 촉감에 맞췄습니다."
  },
  {
    no: "09",
    title: "야외 활동에서 이마 주변 노출 부담을 줄이는 폭",
    image: "12-human-wearing.jpg",
    body: "한낮 러닝처럼 햇빛이 강한 환경에서도 이마 주변을 넓게 덮어 야외 활동의 부담을 덜어줍니다."
  },
  {
    no: "10",
    title: "더운 날에도 부담을 낮추는 얇은 터치감",
    image: "14-feature-detail.jpg",
    body: "피부에 닿는 면을 얇고 부드럽게 정리해 땀이 난 뒤에도 무겁게 들러붙는 느낌을 줄였습니다."
  },
  {
    no: "11",
    title: "내 머리에 맞게 늘어나는 부드러운 텐션",
    image: "15-feature-detail.jpg",
    body: "머리 둘레에 맞게 자연스럽게 늘어나며, 오래 착용했을 때의 압박감을 낮추는 탄성 밸런스를 잡았습니다."
  },
  {
    no: "12",
    title: "땀에 젖은 뒤에도 산뜻하게 관리",
    image: "16-feature-detail.jpg",
    body: "땀에 젖은 뒤에도 가볍게 세탁해 관리할 수 있습니다.\n반복 착용을 고려해 매일 쓰기 쉬운 원단감으로 구성했습니다."
  },
  {
    no: "13",
    title: "넓게 쓰거나 접어서 쓰는 폭 조절",
    image: "17-color-option.jpg",
    body: "상황에 따라 넓게 펼쳐 이마를 덮거나, 접어서 좁은 폭으로 착용할 수 있습니다.\n러닝 강도와 스타일에 맞춰 폭을 바꿔보세요."
  },
  {
    no: "14",
    title: "자주 묻는 질문",
    image: "",
    body: "Q. 땀이 많은 사람도 사용할 수 있나요?\nA. 넓은 면적으로 땀을 받아주도록 설계했습니다. 장시간 고강도 운동으로 충분히 젖었을 때는 한 번 짜서 다시 착용하는 방식이 좋습니다.\n\nQ. 머리가 작거나 큰 편이어도 괜찮나요?\nA. FREE 사이즈 기준의 신축 원단입니다. 처음 착용할 때는 머리 둘레에 맞게 가볍게 늘려 텐션을 맞춘 뒤 사용하는 편이 좋습니다."
  },
  {
    no: "15",
    title: "세 가지 컬러 옵션",
    image: "19-feature-detail.jpg",
    extraImages: ["20-color-option.jpg", "21-feature-detail.jpg"],
    body: "블랙\n가장 기본적인 컬러로 운동복과 일상복에 모두 맞추기 쉽습니다.\n\n화이트\n깔끔한 인상으로 밝은 러닝웨어와 잘 어울립니다.\n\n딥그린\n차분한 포인트 컬러로 과하지 않게 스타일을 더합니다."
  },
  {
    no: "16",
    title: "쉬운 길보다, 계속 달릴 수 있는 장비",
    image: "22-human-wearing.jpg",
    body: "Runnerwin은 러너가 훈련 중 덜 신경 쓰게 되는 장비를 기준으로 선택합니다.\n과한 장식보다 필요한 기능, 부담 없는 가격, 오래 쓰는 내구성을 먼저 봅니다."
  },
  {
    no: "17",
    title: "사이즈 정보",
    image: "",
    body: "가로 약 23.5cm\n넓은 폭 약 12cm\n좁은 폭 약 4.5cm\nFREE 사이즈"
  },
  {
    no: "18",
    title: "세탁 주의사항",
    image: "",
    body: "첫 세탁은 단독 세탁을 권장합니다.\n중성세제로 가볍게 손세탁해 주세요.\n표백제와 드라이클리닝은 피해주세요.\n형태 유지를 위해 그늘에서 자연 건조해 주세요."
  },
  {
    no: "19",
    title: "제품 정보",
    image: "",
    body: "상품명: Runnerwin 와이드 쿨핏 헤어밴드\n모델명: RWHB-W01\n소재: 겉감 폴리에스터/스판덱스 혼방, 안감 나일론/스판덱스 혼방\n색상: 블랙, 화이트, 딥그린\n사이즈: FREE / 약 23.5cm, 넓은 폭 약 12cm, 좁은 폭 약 4.5cm\n제조국: 중국 OEM\n관리법: 중성세제 단독 손세탁, 그늘 건조, 표백제/건조기 사용 금지"
  }
];

const promptRows = [
  ["대표 이미지 / 썸네일", "main.png", "상품 대표 이미지", "상세 상단 대표 이미지, 상품 리스트 썸네일", "원본 이미지를 참고해서 Runnerwin 와이드 헤드밴드 대표 상품 이미지로 바꿔줘. 로고와 브랜드명은 제거하고, 제품 형태와 컬러는 유지하되 배경색, 조명, 그림자, 제품 각도는 다르게 만들어줘."],
  ["흡수력 데모", "01-feature-detail.jpg", "기능 데모컷", "02. 땀이 흐르기 전에 먼저 받아주는 넓은 원단", "로고는 제거하고 배경 톤과 제품 접힘을 다르게 바꿔줘. 원단 위에 물이 닿고 흡수되는 장면은 유지해줘. 원본과 같은 조명, 같은 접힘, 같은 확대 비율처럼 보이지 않게 해줘."],
  ["흡수력 GIF 대체", "02-unclassified.gif", "기능 데모 GIF 또는 정지컷", "02. 땀이 흐르기 전에 먼저 받아주는 넓은 원단 보조", "로고는 제거하고 배경 톤과 제품 접힘을 다르게 바꿔줘. 물 흡수 장면은 유지하되 원본과 다른 구도와 조명으로 자연스럽게 만들어줘."],
  ["딥그린 착용컷", "04-human-wearing.jpg", "사람 착용컷", "04. 와이드 폭이 얼굴 라인에 걸리는 느낌", "배경을 차분한 파란색 스튜디오 배경으로 바꿔줘. 얼굴은 한국의 잘생긴 배우 느낌으로 바꿔줘. 딥그린 와이드 헤드밴드의 착용 위치와 폭은 유지해줘. 원본 인물, 원본 배경, 원본 조명과 다르게 만들어줘."],
  ["화이트 착용컷", "05-human-wearing.jpg", "사람 착용컷", "05. 운동용이지만 일상에도 무리 없는 실루엣", "배경을 차분한 파란색 스튜디오 배경으로 바꿔줘. 얼굴은 한국의 잘생긴 배우 느낌으로 바꿔줘. 화이트 와이드 헤드밴드의 착용 위치와 폭은 유지해줘. 원본과 다른 인물, 다른 얼굴 각도, 다른 조명으로 만들어줘."],
  ["소재 디테일", "11-product-only.jpg", "제품/원단 확대컷", "08. 바깥은 통기성, 안쪽은 흡수감", "로고와 문구는 제거해줘. 제품 바깥면과 안쪽면, 원단 확대 디테일이 잘 보이게 유지하되 원단 확대 구도, 배경, 조명은 다르게 바꿔줘."],
  ["UV 커버 착용컷", "12-human-wearing.jpg", "사람 착용컷 + 기능 설명컷", "09. 야외 활동에서 이마 주변 노출 부담을 줄이는 폭", "UV 아이콘과 문구는 제거해줘. 인물은 한국 남성 광고 모델 느낌으로 바꿔줘. 헤드밴드 착용 상태와 와이드 폭은 유지하고, 배경과 조명은 원본과 다르게 만들어줘."],
  ["쿨링 원단", "14-feature-detail.jpg", "원단 확대컷", "10. 더운 날에도 부담을 낮추는 얇은 터치감", "이미지 안의 문구는 제거해줘. 원단 질감은 유지하되 확대 비율, 조명, 배경색은 다르게 바꿔줘. 시원하고 얇은 소재감이 느껴지게 만들어줘."],
  ["신축성 데모", "15-feature-detail.jpg", "손으로 늘리는 제품 데모컷", "11. 내 머리에 맞게 늘어나는 부드러운 텐션", "손 위치와 배경을 다르게 바꿔줘. 로고는 제거해줘. 제품이 자연스럽게 늘어나는 장면은 유지하되 원본과 같은 손 모양, 같은 조명, 같은 배치는 피해서 만들어줘."],
  ["위생/냄새 관리", "16-feature-detail.jpg", "원단 클로즈업", "12. 땀에 젖은 뒤에도 산뜻하게 관리", "아이콘과 문구는 제거해줘. 원단 클로즈업 느낌은 유지하되 배경과 조명을 다르게 바꿔줘. 깨끗하고 관리가 쉬운 소재 느낌으로 만들어줘."],
  ["폭 조절", "17-color-option.jpg", "접은/펼친 제품컷", "13. 넓게 쓰거나 접어서 쓰는 폭 조절", "로고는 제거해줘. 접은 상태와 펼친 상태가 모두 보이게 유지하되 제품 배치, 그림자, 배경은 다르게 바꿔줘."],
  ["블랙 컬러 옵션", "19-feature-detail.jpg", "색상 옵션컷", "15. 세 가지 컬러 옵션 - 블랙", "로고는 제거하고 제품 배치와 그림자를 다르게 바꿔줘. 블랙 컬러는 명확하게 유지하되 원본과 같은 각도, 같은 배경, 같은 그림자는 피해서 만들어줘."],
  ["화이트 컬러 옵션", "20-color-option.jpg", "색상 옵션컷", "15. 세 가지 컬러 옵션 - 화이트", "로고는 제거하고 제품 배치와 그림자를 다르게 바꿔줘. 화이트 컬러는 명확하게 유지하되 원본과 같은 각도, 같은 배경, 같은 그림자는 피해서 만들어줘."],
  ["딥그린 컬러 옵션", "21-feature-detail.jpg", "색상 옵션컷", "15. 세 가지 컬러 옵션 - 딥그린", "로고는 제거하고 제품 배치와 그림자를 다르게 바꿔줘. 딥그린 컬러는 명확하게 유지하되 원본과 같은 각도, 같은 배경, 같은 그림자는 피해서 만들어줘."],
  ["브랜드 무드컷", "22-human-wearing.jpg", "러너 무드컷", "16. 쉬운 길보다, 계속 달릴 수 있는 장비", "문구와 로고는 모두 제거해줘. 인물과 배경을 다르게 바꿔줘. 러닝 브랜드 광고 느낌은 유지하되 원본 인물, 원본 포즈, 원본 배경과 다르게 만들어줘."]
];

function imageMarker(section) {
  if (!section.image) return "";
  if (section.extraImages) {
    return [section.image, ...section.extraImages].map((image) => `(이미지, ${image})`).join("\n");
  }
  if (section.extraImage) return `(이미지, ${section.image})\n(이미지, ${section.extraImage})`;
  return `(이미지, ${section.image})`;
}

const mdLines = [
  "# Runnerwin 와이드 쿨핏 헤어밴드 상세페이지 텍스트",
  "",
  "상품명",
  "Runnerwin 와이드 쿨핏 헤어밴드",
  ""
];

for (const section of scriptSections) {
  mdLines.push(`${section.no}. ${section.title}`);
  const marker = imageMarker(section);
  if (marker) mdLines.push(marker);
  mdLines.push(section.body, "");
}

await fs.writeFile(new URL("runnerwin-wide-headband-detail-script.md", outputDir), mdLines.join("\n"), "utf8");

const workbook = Workbook.create();
const scriptSheet = workbook.worksheets.add("Detail Script");
scriptSheet.showGridLines = false;
scriptSheet.getRange("A1:E1").merge();
scriptSheet.getRange("A1").values = [["Runnerwin 와이드 쿨핏 헤어밴드 상세페이지 스크립트"]];
scriptSheet.getRange("A2:E2").merge();
scriptSheet.getRange("A2").values = [["이미지 삽입 위치는 (이미지, 원본사진이름) 형식으로 표시"]];
scriptSheet.getRange("A4:E4").values = [["순서", "섹션 제목", "이미지 표기", "텍스트", "처리 방식"]];
scriptSheet.getRange(`A5:E${scriptSections.length + 4}`).values = scriptSections.map((section) => [
  section.no,
  section.title,
  imageMarker(section),
  section.body,
  section.image ? "이미지는 Atlas 변환 결과로 교체 / 텍스트는 HTML" : "HTML 텍스트"
]);

scriptSheet.getRange("A1:E1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center"
};
scriptSheet.getRange("A2:E2").format = {
  fill: "#EEF1F4",
  font: { color: "#333333" },
  horizontalAlignment: "center"
};
scriptSheet.getRange("A4:E4").format = {
  fill: "#26352E",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center"
};
scriptSheet.getRange(`A5:E${scriptSections.length + 4}`).format = {
  wrapText: true,
  verticalAlignment: "top"
};
scriptSheet.getRange("A:A").format.columnWidthPx = 56;
scriptSheet.getRange("B:B").format.columnWidthPx = 260;
scriptSheet.getRange("C:C").format.columnWidthPx = 240;
scriptSheet.getRange("D:D").format.columnWidthPx = 620;
scriptSheet.getRange("E:E").format.columnWidthPx = 180;
scriptSheet.getRange(`A5:E${scriptSections.length + 4}`).format.rowHeightPx = 104;
scriptSheet.freezePanes.freezeRows(4);

const promptSheet = workbook.worksheets.add("Atlas Prompt Plan");
promptSheet.showGridLines = false;
promptSheet.getRange("A1:F1").merge();
promptSheet.getRange("A1").values = [["Runnerwin 와이드 헤드밴드 - 원본사진별 Atlas 프롬프트"]];
promptSheet.getRange("A3:F3").values = [["삽입 위치", "원본사진 이름", "이미지 역할", "상세페이지 위치", "Atlas 입력 프롬프트", "받아낸 이미지 파일명"]];
promptSheet.getRange(`A4:F${promptRows.length + 3}`).values = promptRows.map((row) => [...row, ""]);
promptSheet.getRange("A1:F1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center"
};
promptSheet.getRange("A3:F3").format = {
  fill: "#26352E",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center"
};
promptSheet.getRange(`A4:F${promptRows.length + 3}`).format = {
  wrapText: true,
  verticalAlignment: "top"
};
promptSheet.getRange("A:A").format.columnWidthPx = 180;
promptSheet.getRange("B:B").format.columnWidthPx = 190;
promptSheet.getRange("C:C").format.columnWidthPx = 170;
promptSheet.getRange("D:D").format.columnWidthPx = 260;
promptSheet.getRange("E:E").format.columnWidthPx = 620;
promptSheet.getRange("F:F").format.columnWidthPx = 220;
promptSheet.getRange(`A4:F${promptRows.length + 3}`).format.rowHeightPx = 116;
promptSheet.freezePanes.freezeRows(3);

const checklistSheet = workbook.worksheets.add("Checklist");
checklistSheet.showGridLines = false;
checklistSheet.getRange("A1:D1").merge();
checklistSheet.getRange("A1").values = [["작업 체크리스트"]];
checklistSheet.getRange("A3:D3").values = [["체크", "항목", "기준", "비고"]];
checklistSheet.getRange("A4:D11").values = [
  ["", "원본사진 추출", "엑셀 B열 파일명 기준으로 원본 이미지 확보", ""],
  ["", "Atlas 입력", "원본사진 + E열 프롬프트 입력", ""],
  ["", "결과 저장", "받아낸 이미지 파일명을 F열에 기록", ""],
  ["", "사이트 삽입", "Detail Script의 이미지 표기 위치에 삽입", ""],
  ["", "원본 문구 제거", "이미지 안 문구/로고 제거 확인", ""],
  ["", "HTML 텍스트 반영", "D열 텍스트를 상세페이지 HTML로 반영", ""],
  ["", "모바일 검수", "텍스트 잘림/이미지 비율/CTA 위치 확인", ""],
  ["", "최종 잔존 검사", "원본 브랜드명/로고/후기/파일명 노출 확인", ""]
];
checklistSheet.getRange("A1:D1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center"
};
checklistSheet.getRange("A3:D3").format = {
  fill: "#26352E",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center"
};
checklistSheet.getRange("A4:D11").format = {
  wrapText: true,
  verticalAlignment: "top"
};
checklistSheet.getRange("A:A").format.columnWidthPx = 62;
checklistSheet.getRange("B:B").format.columnWidthPx = 180;
checklistSheet.getRange("C:C").format.columnWidthPx = 380;
checklistSheet.getRange("D:D").format.columnWidthPx = 260;
checklistSheet.freezePanes.freezeRows(3);

const preview = await workbook.render({
  sheetName: "Detail Script",
  range: "A1:E24",
  scale: 1,
  format: "png"
});
await fs.writeFile(new URL("runnerwin-wide-headband-detail-script-preview.png", outputDir), new Uint8Array(await preview.arrayBuffer()));

const promptPreview = await workbook.render({
  sheetName: "Atlas Prompt Plan",
  range: "A1:F18",
  scale: 1,
  format: "png"
});
await fs.writeFile(new URL("runnerwin-wide-headband-prompt-plan-preview.png", outputDir), new Uint8Array(await promptPreview.arrayBuffer()));

const inspect = await workbook.inspect({
  kind: "table",
  range: "Atlas Prompt Plan!A1:F18",
  include: "values",
  tableMaxRows: 18,
  tableMaxCols: 6
});
console.log(inspect.ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(new URL("runnerwin-wide-headband-detail-script-prompts.xlsx", outputDir));
