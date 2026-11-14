# 보고서 작성 스타일 가이드

## 문체 규칙

### MOST IMPORTANT RULE: BREVITY
- 전체 보고서 본문 텍스트는 1,500 words 이내
- Figure/Table이 정보를 전달하고, 글은 Figure/Table을 연결하는 역할만
- 한 섹션에 한 문단, 한 문단에 2-3문장
- Figure가 보여주는 내용을 글로 반복하면 절대 안 됨
- "As shown in Figure X, [key number]" 패턴만 사용

### DO
- 수치 중심: "478 PPI interactions" not "many interactions"
- 표/그래프 참조 후 핵심 1개 수치만 언급
- Passive voice + active voice 혼용

### DON'T
- "It is interesting to note that..." 같은 filler ❌
- "Very", "extremely", "significantly" ❌
- 동일 정보 반복 ❌
- AI 특유의 장황한 설명 ❌

### 문장 예시
❌ "It is very interesting to note that our analysis revealed that there are many shared targets between the drugs we studied."
✅ "Cross-database analysis identified 24 shared protein targets between morphine and diazepam (Jaccard index = 0.089), the highest overlap among all drug pairs (Figure 2)."

❌ "The results show that MDMA is a very strong inhibitor of the CYP2D6 enzyme, which is extremely important for drug metabolism."
✅ "MDMA irreversibly inhibits CYP2D6 via mechanism-based inactivation, reducing methamphetamine clearance by an estimated 30–50% in co-administration scenarios (Table 4)."

## 표 작성 규칙
- Table은 self-explanatory해야 함 (본문 없이도 이해 가능)
- column header는 명확하게, 단위 포함
- 주요 발견은 bold 처리
- Source/Note를 table 하단에 명시

## Figure 캡션 규칙
- Figure 번호 + 제목 + 간단한 설명 (1-2문장)
- 데이터 출처 명시
- 예: "Figure 1. CYP Enzyme-Drug Metabolism Heatmap. Color intensity indicates the degree of metabolic dependency (Major: primary substrate; Minor: secondary pathway). Data compiled from FDA drug labels and Flockhart Drug Interaction Table."

## 분량 조절 가이드
- 전체 20페이지 이내 (그래프/표 포함)
- 그래프가 전달하는 정보를 본문에서 반복하지 않기
- "As shown in Figure X, [핵심 수치 1-2개만 언급]" 패턴 사용
- Discussion에서 모든 결과를 다시 나열하지 않고, 의미 해석에 집중

## 레퍼런스 형식
보고서 내 데이터베이스 인용 형식:
- PubChem (Kim et al., 2023. Nucleic Acids Research)
- ChEMBL (Zdrazil et al., 2024. Nucleic Acids Research)
- KEGG (Kanehisa et al., 2023. Nucleic Acids Research)
- STRING (Szklarczyk et al., 2023. Nucleic Acids Research)
- UniProt (The UniProt Consortium, 2023. Nucleic Acids Research)
- Open Targets Platform (Ochoa et al., 2023. Nucleic Acids Research)
- OpenFDA (U.S. FDA. openFDA API, https://open.fda.gov/)
- Flockhart DA. Drug Interactions: Cytochrome P450 Drug Interaction Table. Indiana University School of Medicine.
