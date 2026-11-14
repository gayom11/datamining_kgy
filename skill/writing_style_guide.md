# 보고서 작성 스타일 가이드

## 문체 규칙

### DO (따라야 할 규칙)
- 학술 논문 스타일 (scientific report) 유지
- Passive voice와 active voice를 적절히 혼용
- 구체적 수치 사용: "several databases" ❌ → "nine databases" ✅
- Figure/Table 번호를 본문에서 명시적으로 참조
- 짧은 문단 (3-4문장 이내)
- 결과는 data-driven으로 서술

### DON'T (피해야 할 것)
- "It is interesting to note that..." 같은 불필요한 도입부 ❌
- "Very", "extremely", "significantly" 등의 과도한 수식어 ❌
- 동일 정보의 반복 서술 ❌
- 추측성 표현 최소화 (may, might는 가능하지만 근거 필요)
- AI 특유의 장황한 설명 ❌ → 표/그래프가 설명하는 내용은 다시 풀어쓰지 않기

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
