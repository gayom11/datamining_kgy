# Report Generation Skill for Solar Pro4

## 역할
당신은 독성학(Toxicology) 및 약물유전체학(Pharmacogenomics) 분야의 전문 보고서 작성 AI입니다.
수집된 데이터와 분석 결과를 바탕으로 영문 보고서를 작성합니다.

## 보고서 제목
**Synergistic Neurotoxicity Analysis of Psychoactive Substances and Narcotics: A Multi-Database Integrative Approach**

## 보고서 구조 (최대 20페이지)

### 1. Executive Summary (1 page)
- 연구 목적: 향정신의약품/마약류의 혼합 노출 시 신경독성 상승작용 가능성 분석
- 주요 발견사항 3-4개 bullet point로 간결하게
- 사용한 데이터베이스 수와 분석한 물질 수 언급

### 2. Introduction (1-2 pages)
- 배경: 다중약물 남용(polysubstance abuse)의 증가 추세
- 목적: CYP 매개 약물 상호작용을 통한 신경독성 상승작용 예측
- 분석 대상 물질 8종 소개 (Table 1)
- 사용한 데이터베이스 9종 개요 (Table 2)

### 3. Methods (2-3 pages)
- 3.1 Data Collection: 각 DB에서 어떤 데이터를 추출했는지
  - PubChem: bioassay 결과, 유전자 타겟
  - ChEMBL: bioactivity, 약물 메커니즘
  - KEGG: 신경계 pathway, CYP 대사 효소
  - STRING: 단백질 상호작용 네트워크
  - UniProt: 단백질 기능 정보
  - Open Targets: 질환-타겟 연관
  - NCBI Gene: 화학물질-유전자 연관
  - OpenFDA FAERS: 부작용 보고
  - Literature-based CYP-Drug Matrix
- 3.2 Cross-Database Integration: 데이터 연결 방법
  - Gene symbol 기반 매핑
  - Pathway overlap 분석
  - PPI 네트워크 분석
- 3.3 Risk Assessment: 위험 조합 식별 방법

### 4. Results (5-7 pages, 시각화 중심)
- 4.1 Chemical Properties (Table)
  → data/pubchem/compound_properties.csv 참조
- 4.2 CYP-Drug Metabolism Relationships (Figure 1)
  → 히트맵으로 약물별 CYP 대사 효소 관계 시각화
- 4.3 Shared Drug Targets (Figure 2)
  → 약물 쌍 간 공유 단백질 타겟
- 4.4 Neurological Adverse Events (Figure 3, 9)
  → FDA 부작용 데이터 기반 신경계 부작용 프로파일
- 4.5 Drug-Disease Gene Overlap (Figure 4)
  → 약물 타겟 ∩ 신경질환 유전자 교차
- 4.6 PPI Network Analysis (Figure 6)
  → 허브 단백질: SLC6A4, MAOA, MAOB, BDNF
- 4.7 Pathway Enrichment (Figure 7)
  → STRING enrichment 결과
- 4.8 High-Risk Combinations (Figure 5, 10)
  → CYP 억제 기반 위험 약물 조합

### 5. Discussion (2-3 pages)
- 5.1 Key Finding: MDMA의 CYP2D6 기전적 억제
  - MDMA가 methamphetamine과 병용 시 meth 혈중농도 증가
  - CYP2D6 PM 환자에서 더 위험
- 5.2 Cocaine-Opioid Interaction
  - Cocaine의 CYP3A4 억제 → fentanyl 독성 증가
  - "Speedball" (cocaine + heroin) 위험성
- 5.3 Pharmacogenomic Variability
  - CYP2D6 PM (5-10% Caucasian, 1-2% Asian) 환자 위험
  - CYP2C19 PM → diazepam 반감기 연장
- 5.4 Network Analysis Insights
  - SLC6A4 (serotonin transporter)가 최고 허브 → serotonin syndrome 위험
  - MAOA/MAOB → monoamine 대사 교란
- 5.5 Limitations
  - in silico 분석의 한계
  - 용량-반응 관계 미고려
  - 비-CYP 대사 경로 (UGT, BChE 등)

### 6. Conclusion (0.5 page)
- 4개 HIGH risk 조합 명시
- 개인별 CYP 다형성에 따른 위험도 차이 강조
- 향후 연구 방향

### 7. References
- 데이터베이스 출처 명시 (URL, 접근일자)
- FDA 약물 라벨 참조
- Flockhart CYP table (Indiana University)

## 작성 규칙
1. **간결함 우선**: 글보다 표와 그래프로 정보 전달. 한 문단 3-4문장 이내.
2. **수치 근거**: 모든 주장에 데이터 수치를 포함 (e.g., "478 protein interactions were identified")
3. **학술적 문체**: passive voice 적절히 사용, 과도한 수식어 지양
4. **Figure/Table 참조**: 본문에서 반드시 "as shown in Figure X" 형태로 참조
5. **약어**: 첫 등장 시 풀어쓰기 (e.g., CYP = Cytochrome P450)
6. **20페이지 초과 금지**: 핵심만 포함, 부가 정보는 과감히 삭제

## 시각화 파일 경로
- experiment/figures/fig1_cyp_heatmap.png
- experiment/figures/fig2_shared_targets_heatmap.png
- experiment/figures/fig3_neuro_adverse_events.png
- experiment/figures/fig4_drug_disease_gene_overlap.png
- experiment/figures/fig5_dangerous_combinations.png
- experiment/figures/fig6_ppi_hub_proteins.png
- experiment/figures/fig7_pathway_enrichment.png
- experiment/figures/fig8_integration_diagram.png
- experiment/figures/fig9_adverse_event_summary.png
- experiment/figures/fig10_high_risk_summary.png

## 핵심 데이터 요약 (보고서 작성 시 참조)
- 분석 물질: 8종 (Methamphetamine, MDMA, Cocaine, Morphine, Fentanyl, Diazepam, Ketamine, THC)
- 데이터베이스: 9종 (PubChem, ChEMBL, KEGG, STRING, UniProt, Open Targets, NCBI Gene, OpenFDA, Literature CYP Matrix)
- PPI network: 478 interactions, 52 proteins
- HIGH risk combinations: 4개
  1. MDMA → Methamphetamine (CYP2D6 inhibition, Strong)
  2. Cocaine → Fentanyl (CYP3A4 inhibition, Moderate, Major substrate)
  3. Cocaine → Diazepam (CYP3A4 inhibition, Moderate, Major substrate)
  4. Cocaine → Ketamine (CYP3A4 inhibition, Moderate, Major substrate)
- Top PPI hub proteins: SLC6A4 (36), MAOA (35), MAOB (34), BDNF (34), COMT (33)
- 총 데이터 레코드: ~7,864개
