import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = new URL("../output/", import.meta.url);
const mdPath = new URL("../output/runnerwin-running-cap-pilot-image-log.md", import.meta.url);
const md = await fs.readFile(mdPath, "utf8");

const promptMatches = [...md.matchAll(/### (CAP-[^\n]+)\n\n([\s\S]*?)(?=\n### |\n?$)/g)];
const prompts = Object.fromEntries(promptMatches.map((match) => [match[1].trim(), match[2].trim()]));

const rows = [
  {
    section: "01",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/02-human-wearing.jpg",
    role: "사람 착용컷",
    promptKey: "CAP-01-WEARING-HERO",
    output: "assets/images/runnerwin-running-cap-01-wearing-hero.png",
    insert: "상세 첫 착용 히어로",
    status: "ChatGPT Atlas 생성본 삽입 완료",
    notes: "원본 이미지를 ChatGPT Atlas에 업로드해 생성한 결과물로 교체 완료."
  },
  {
    section: "02",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/10-feature-detail.jpg",
    role: "기능/상세 설명컷",
    promptKey: "CAP-02-DETAIL-FEATURE",
    output: "assets/images/runnerwin-running-cap-02-detail-feature.png",
    insert: "기능 설명 섹션",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "03",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/01-product-only.jpg",
    role: "상품 단독컷",
    promptKey: "CAP-03-PRODUCT-SOLO",
    output: "assets/images/runnerwin-running-cap-03-product-solo.png",
    insert: "상품 단독 섹션 및 대표 이미지",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "04",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/17-human-wearing.jpg",
    role: "사람 착용컷",
    promptKey: "CAP-04-WEARING-RUN",
    output: "assets/images/runnerwin-running-cap-04-wearing-run.png",
    insert: "러닝 착용 섹션",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "05",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/19-feature-detail.jpg",
    role: "디테일 컷",
    promptKey: "CAP-05-STRAP-DETAIL",
    output: "assets/images/runnerwin-running-cap-05-strap-detail.png",
    insert: "후면 스트랩 섹션",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "06",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/14-color-option.jpg",
    role: "색상 옵션컷",
    promptKey: "CAP-06-COLOR-OPTION",
    output: "assets/images/runnerwin-running-cap-06-color-option.png",
    insert: "컬러 옵션 섹션",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "07",
    product: "Runnerwin 올라운드 러닝캡",
    input: "output/originals/running-cap/source-sequence/22-human-wearing.jpg",
    role: "사람 착용컷",
    promptKey: "CAP-07-WEARING-LIFESTYLE",
    output: "assets/images/runnerwin-running-cap-07-wearing-lifestyle.png",
    insert: "활용 장면 섹션",
    status: "파일럿 이미지 삽입 완료",
    notes: "로컬 PIL 렌더러로 임시 제작. Atlas 생성 시 교체 대상."
  },
  {
    section: "08",
    product: "Runnerwin 올라운드 러닝캡",
    input: "원본 후기 요약 영역",
    role: "리뷰/활용 가이드",
    promptKey: "CAP-08-REVIEW-GUIDE",
    output: "HTML 텍스트 블록",
    insert: "리뷰 요약 섹션",
    status: "반영 완료",
    notes: "샘플 리뷰 문구로 재작성"
  }
];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Image Log");
sheet.showGridLines = false;

sheet.getRange("A1:J1").merge();
sheet.getRange("A1").values = [["Runnerwin Running Cap - Image Generation Log"]];
sheet.getRange("A2:J2").merge();
sheet.getRange("A2").values = [["기입한 이미지 / 기입한 프롬프트 / 받아낸 이미지를 1:1로 추적하는 파일럿 관리표"]];

sheet.getRange("A4:J4").values = [[
  "섹션",
  "상품명",
  "기입한 이미지",
  "원본 역할",
  "기입한 프롬프트 키",
  "기입한 프롬프트",
  "받아낸 이미지",
  "삽입 위치",
  "상태",
  "비고"
]];

sheet.getRange(`A5:J${rows.length + 4}`).values = rows.map((row) => [
  row.section,
  row.product,
  row.input,
  row.role,
  row.promptKey,
  prompts[row.promptKey] || "",
  row.output,
  row.insert,
  row.status,
  row.notes
]);

sheet.getRange("A1:J1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center"
};
sheet.getRange("A2:J2").format = {
  fill: "#F0F1EA",
  font: { color: "#333333" },
  horizontalAlignment: "center"
};
sheet.getRange("A4:J4").format = {
  fill: "#2F3A33",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center"
};
sheet.getRange(`A5:J${rows.length + 4}`).format = {
  wrapText: true,
  verticalAlignment: "top"
};
sheet.getRange("A:A").format.columnWidthPx = 52;
sheet.getRange("B:B").format.columnWidthPx = 190;
sheet.getRange("C:C").format.columnWidthPx = 310;
sheet.getRange("D:D").format.columnWidthPx = 130;
sheet.getRange("E:E").format.columnWidthPx = 180;
sheet.getRange("F:F").format.columnWidthPx = 620;
sheet.getRange("G:G").format.columnWidthPx = 310;
sheet.getRange("H:H").format.columnWidthPx = 160;
sheet.getRange("I:I").format.columnWidthPx = 96;
sheet.getRange("J:J").format.columnWidthPx = 240;
sheet.getRange("A5:J12").format.rowHeightPx = 136;
sheet.freezePanes.freezeRows(4);

const promptSheet = workbook.worksheets.add("Prompt Blocks");
promptSheet.showGridLines = false;
promptSheet.getRange("A1:C1").values = [["프롬프트 키", "역할", "프롬프트"]];
promptSheet.getRange("A2:C9").values = rows.map((row) => [
  row.promptKey,
  row.role,
  prompts[row.promptKey] || ""
]);
promptSheet.getRange("A1:C1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF" }
};
promptSheet.getRange("A2:C9").format = {
  wrapText: true,
  verticalAlignment: "top"
};
promptSheet.getRange("A:A").format.columnWidthPx = 190;
promptSheet.getRange("B:B").format.columnWidthPx = 140;
promptSheet.getRange("C:C").format.columnWidthPx = 780;
promptSheet.getRange("A2:C9").format.rowHeightPx = 152;
promptSheet.freezePanes.freezeRows(1);

const previewSheet = workbook.worksheets.add("Image Preview");
previewSheet.showGridLines = false;
previewSheet.getRange("A1:F1").merge();
previewSheet.getRange("A1").values = [["기입한 이미지 / 받아낸 이미지 썸네일"]];
previewSheet.getRange("A1:F1").format = {
  fill: "#111111",
  font: { bold: true, color: "#FFFFFF", size: 15 },
  horizontalAlignment: "center"
};
previewSheet.getRange("A3:F3").values = [["섹션", "원본 역할", "기입한 이미지", "프롬프트 키", "받아낸 이미지", "상태"]];
previewSheet.getRange("A3:F3").format = {
  fill: "#2F3A33",
  font: { bold: true, color: "#FFFFFF" }
};
previewSheet.getRange("A:A").format.columnWidthPx = 54;
previewSheet.getRange("B:B").format.columnWidthPx = 140;
previewSheet.getRange("C:C").format.columnWidthPx = 190;
previewSheet.getRange("D:D").format.columnWidthPx = 190;
previewSheet.getRange("E:E").format.columnWidthPx = 190;
previewSheet.getRange("F:F").format.columnWidthPx = 170;
previewSheet.freezePanes.freezeRows(3);

function mimeFor(path) {
  if (path.endsWith(".jpg") || path.endsWith(".jpeg")) return "image/jpeg";
  if (path.endsWith(".webp")) return "image/webp";
  return "image/png";
}

async function dataUrlFor(relativePath) {
  const bytes = await fs.readFile(new URL(`../${relativePath}`, import.meta.url));
  return `data:${mimeFor(relativePath)};base64,${Buffer.from(bytes).toString("base64")}`;
}

for (const [index, row] of rows.entries()) {
  const excelRow = index + 4;
  previewSheet.getRange(`A${excelRow}:F${excelRow}`).values = [[row.section, row.role, row.input, row.promptKey, row.output, row.status]];
  previewSheet.getRange(`A${excelRow}:F${excelRow}`).format = { wrapText: true, verticalAlignment: "top" };
  previewSheet.getRange(`A${excelRow}:F${excelRow}`).format.rowHeightPx = 118;
  if (row.input.startsWith("output/")) {
    previewSheet.images.add({
      dataUrl: await dataUrlFor(row.input),
      anchor: { from: { row: excelRow - 1, col: 2 }, extent: { widthPx: 150, heightPx: 98 } }
    });
  }
  if (row.output.startsWith("assets/")) {
    previewSheet.images.add({
      dataUrl: await dataUrlFor(row.output),
      anchor: { from: { row: excelRow - 1, col: 4 }, extent: { widthPx: 150, heightPx: 98 } }
    });
  }
}

const preview = await workbook.render({
  sheetName: "Image Log",
  range: "A1:J12",
  scale: 1,
  format: "png"
});
await fs.writeFile(new URL("runnerwin-running-cap-pilot-image-log-preview.png", outputDir), new Uint8Array(await preview.arrayBuffer()));

const imagePreview = await workbook.render({
  sheetName: "Image Preview",
  range: "A1:F12",
  scale: 1,
  format: "png"
});
await fs.writeFile(new URL("runnerwin-running-cap-pilot-image-preview-sheet.png", outputDir), new Uint8Array(await imagePreview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(new URL("runnerwin-running-cap-pilot-image-log.xlsx", outputDir));

const inspect = await workbook.inspect({
  kind: "table",
  range: "Image Log!A1:J12",
  include: "values",
  tableMaxRows: 12,
  tableMaxCols: 10
});
console.log(inspect.ndjson);
