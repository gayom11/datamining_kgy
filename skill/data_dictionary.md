# Data Dictionary (데이터 사전)

## 분석 대상 화학물질

| Chemical | Category | Primary Mechanism | CID (PubChem) |
|---|---|---|---|
| Methamphetamine | Amphetamine-type stimulant | DA/NE releaser, TAAR1 agonist | 10836 |
| MDMA (Ecstasy) | Amphetamine-type stimulant | 5-HT/DA/NE releaser | 1615 |
| Cocaine | Tropane alkaloid stimulant | DAT/SERT/NET reuptake inhibitor | 446220 |
| Morphine | Opioid agonist | μ-opioid receptor agonist | 5288826 |
| Fentanyl | Synthetic opioid | μ-opioid receptor agonist (potent) | 3345 |
| Diazepam | Benzodiazepine | GABA-A receptor positive allosteric modulator | 3016 |
| Ketamine | Arylcyclohexylamine | NMDA receptor antagonist | 3821 |
| THC (Dronabinol) | Cannabinoid | CB1/CB2 receptor agonist | 16078 |

## 데이터베이스별 수집 데이터

### 1. PubChem (data/pubchem/)
- **chemical_cids.csv**: 물질별 PubChem CID 매핑
- **compound_properties.csv**: 분자식, 분자량, SMILES, InChIKey
- **bioassay_gene_targets.csv**: bioassay에서 추출한 유전자 타겟 (Gene ID)
- **active_assays.csv**: Active 판정된 assay 상세 결과

### 2. ChEMBL (data/chembl/)
- **bioactivities.csv**: 약물-타겟 bioactivity 데이터 (IC50, Ki, EC50 등)
- **targets.csv**: 고유 타겟 단백질 상세정보
- **mechanisms.csv**: 약물 작용 메커니즘
- **chemical_target_summary.csv**: 약물별 Human 타겟 요약

### 3. KEGG (data/kegg/)
- **neuro_pathway_genes.csv**: 16개 신경계/대사 pathway의 유전자 목록
- **drug_targets.csv**: KEGG Drug 타겟 정보
- **pathway_summary.csv**: Pathway별 유전자 수 요약
- **cyp_metabolism_genes.csv**: CYP 대사 관련 유전자 112개

### 4. STRING (data/string/)
- **ppi_network.csv**: 478개 단백질-단백질 상호작용 (score > 400)
- **functional_enrichment.csv**: 기능 enrichment 분석 (GO, KEGG 등)

### 5. UniProt (data/uniprot/)
- **protein_info.csv**: 53개 핵심 단백질의 기능, UniProt ID

### 6. Open Targets (data/opentargets/)
- **disease_target_associations.csv**: 10개 신경/정신질환의 타겟 유전자 (association score 포함)

### 7. NCBI Gene (data/ncbi_gene/)
- **chemical_gene_associations.csv**: 388개 화학물질-유전자 연관

### 8. OpenFDA (data/sider_fda/)
- **adverse_events.csv**: 800개 부작용 보고 (FDA FAERS)
- **neuro_adverse_events.csv**: 110개 신경계 부작용만 필터

### 9. Pharmacogenomics (data/pharmacogenomics/)
- **cyp_drug_metabolism_matrix.csv**: 약물-CYP 대사 관계 매트릭스
- **cyp_polymorphisms.csv**: CYP 유전자 다형성 정보
- **drug_cyp_interactions.csv**: 약물의 CYP 억제/유도 효과
- **dangerous_combinations.csv**: 19개 위험 약물 조합
- **high_risk_combinations.csv**: 4개 HIGH risk 조합

## 교차 분석 결과 (experiment/)
- **shared_drug_targets.csv**: 약물 쌍별 공유 타겟 수 + Jaccard index
- **drug_disease_gene_overlap.csv**: 약물 타겟 ∩ 신경질환 유전자 교차
- **drug_pathway_hits.csv**: 약물 타겟의 pathway 분포
- **ppi_hub_proteins.csv**: PPI 네트워크 허브 단백질 top 30
- **database_summary.csv**: 데이터베이스별 레코드 수 요약

## 핵심 용어
- **CYP (Cytochrome P450)**: 약물 대사의 핵심 효소 패밀리
- **PPI (Protein-Protein Interaction)**: 단백질 간 물리적/기능적 상호작용
- **FAERS**: FDA Adverse Event Reporting System
- **MeSH**: Medical Subject Headings (의학 주제어)
- **EFO**: Experimental Factor Ontology (Open Targets에서 사용)
- **pChEMBL**: -log10(활성값), 높을수록 강한 활성
- **Jaccard Index**: 두 집합의 유사도 지표 (교집합/합집합)
- **PM (Poor Metabolizer)**: CYP 효소 활성이 낮은 유전형
- **UM (Ultra-rapid Metabolizer)**: CYP 효소 활성이 높은 유전형
