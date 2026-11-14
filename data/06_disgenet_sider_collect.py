"""
DisGeNET + SIDER 데이터 수집
- DisGeNET: 유전자-질환 연관 (신경/정신 질환 관련)
- SIDER: 약물 부작용 데이터
"""
import requests
import pandas as pd
import time
import os

# ============================================================
# DisGeNET - 질환-유전자 연관
# 공개 데이터셋 사용 (API는 등록 필요하므로 대안 접근)
# ============================================================

# 신경/정신질환 관련 DisGeNET disease IDs (UMLS CUI)
NEURO_DISEASES = {
    "Neurotoxicity": "C0235032",
    "Drug-Induced Neurotoxicity": "C0860207",
    "Seizures": "C0036572",
    "Serotonin Syndrome": "C0699828",
    "Substance Withdrawal Syndrome": "C0085605",
    "Psychotic Disorders": "C0033975",
    "Depressive Disorder": "C0011581",
    "Schizophrenia": "C0036341",
    "Anxiety Disorders": "C0003469",
    "Neurodegenerative Diseases": "C0524851",
    "Parkinson Disease": "C0030567",
    "Alzheimer Disease": "C0002395",
    "Drug Dependence": "C1510472",
    "Substance Use Disorder": "C0038586",
}

def get_disgenet_disease_genes_open(disease_name):
    """
    DisGeNET 공개 API로 질환-유전자 연관 조회
    (등록 없이 사용 가능한 범위)
    """
    # DisGeNET REST API (public)
    url = "https://www.disgenet.org/api/gda/disease"
    # 무료 API는 제한적이므로 대안: NCBI Gene에서 질환 관련 유전자 검색
    pass

def collect_disgenet_via_ncbi(disease_name):
    """NCBI Gene에서 질환 관련 유전자 검색 (DisGeNET 대안)"""
    # E-utilities 사용
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "gene",
        "term": f'"{disease_name}"[All Fields] AND "Homo sapiens"[Organism] AND alive[prop]',
        "retmax": 200,
        "retmode": "json",
    }
    r = requests.get(search_url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        gene_ids = data.get("esearchresult", {}).get("idlist", [])
        return gene_ids
    return []

def get_gene_info_batch(gene_ids):
    """NCBI Gene 배치 정보 조회"""
    if not gene_ids:
        return []
    
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    # 배치 크기 제한
    batch = gene_ids[:100]
    params = {
        "db": "gene",
        "id": ",".join(batch),
        "retmode": "json",
    }
    r = requests.get(summary_url, params=params, timeout=30)
    records = []
    if r.status_code == 200:
        data = r.json()
        result = data.get("result", {})
        for gid in batch:
            if gid in result:
                info = result[gid]
                records.append({
                    "Gene_ID": gid,
                    "Gene_Symbol": info.get("name", ""),
                    "Gene_Description": info.get("description", ""),
                    "Chromosome": info.get("chromosome", ""),
                })
    return records

# ============================================================
# SIDER - 약물 부작용
# ============================================================

def collect_sider_effects():
    """
    SIDER 데이터 수집 - 약물 부작용 정보
    SIDER는 직접 다운로드 형식이므로, 타겟 약물에 대해 
    OFFSIDES/SIDER 공개 데이터 활용
    대안: OpenFDA API에서 부작용 데이터 수집
    """
    pass

def collect_openfda_adverse_events(drug_name, limit=100):
    """OpenFDA API로 약물 부작용 보고 수집"""
    url = "https://api.fda.gov/drug/event.json"
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": limit,
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get("results", [])
    return []

CHEMICALS_FDA = {
    "Methamphetamine": "methamphetamine",
    "MDMA": "MDMA",
    "Cocaine": "cocaine",
    "Morphine": "morphine",
    "Fentanyl": "fentanyl",
    "Diazepam": "diazepam",
    "Ketamine": "ketamine",
    "THC": "dronabinol",
}

# 신경계 부작용 필터 키워드
NEURO_SIDE_EFFECTS = [
    "seizure", "convulsion", "tremor", "hallucination", "psychosis",
    "anxiety", "depression", "insomnia", "somnolence", "dizziness",
    "headache", "confusion", "agitation", "delirium", "paranoia",
    "serotonin syndrome", "neuroleptic malignant", "ataxia", "dyskinesia",
    "neuropathy", "cognitive", "memory", "euphoria", "dysphoria",
    "suicidal", "mania", "panic", "sedation", "coma", "stupor",
]

def main():
    os.makedirs("disgenet", exist_ok=True)
    os.makedirs("sider_fda", exist_ok=True)
    
    # 1. 질환-유전자 연관 (NCBI Gene 경유)
    print("=== Step 1: Disease-Gene Associations (via NCBI) ===")
    all_disease_genes = []
    
    for disease_name, cui in NEURO_DISEASES.items():
        print(f"  {disease_name} 처리 중...")
        gene_ids = collect_disgenet_via_ncbi(disease_name)
        if gene_ids:
            gene_info = get_gene_info_batch(gene_ids)
            for g in gene_info:
                g["Disease"] = disease_name
                g["Disease_CUI"] = cui
                all_disease_genes.append(g)
            print(f"    관련 유전자: {len(gene_info)}")
        else:
            print(f"    유전자 없음")
        time.sleep(0.5)
    
    if all_disease_genes:
        dg_df = pd.DataFrame(all_disease_genes)
        dg_df.to_csv("disgenet/disease_gene_associations.csv", index=False)
        print(f"  총 {len(dg_df)} disease-gene associations 저장")
    
    # 2. OpenFDA 부작용 데이터
    print("\n=== Step 2: Drug Adverse Events (OpenFDA) ===")
    all_adverse = []
    
    for name, fda_name in CHEMICALS_FDA.items():
        print(f"  {name} 부작용 조회 중...")
        events = collect_openfda_adverse_events(fda_name)
        for ev in events:
            term = ev.get("term", "").lower()
            is_neuro = any(kw in term for kw in NEURO_SIDE_EFFECTS)
            all_adverse.append({
                "Chemical": name,
                "Adverse_Event": ev.get("term", ""),
                "Count": ev.get("count", 0),
                "Is_Neurological": is_neuro,
            })
        print(f"    부작용 종류: {len(events)}")
        time.sleep(0.5)
    
    if all_adverse:
        ae_df = pd.DataFrame(all_adverse)
        ae_df.to_csv("sider_fda/adverse_events.csv", index=False)
        
        # 신경계 부작용만 필터
        neuro_ae = ae_df[ae_df["Is_Neurological"] == True]
        neuro_ae.to_csv("sider_fda/neuro_adverse_events.csv", index=False)
        print(f"  총 {len(ae_df)} adverse events, 신경계: {len(neuro_ae)}")
    
    print("\n=== DisGeNET/SIDER(FDA) 데이터 수집 완료 ===")
    for folder in ["disgenet", "sider_fda"]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                size = os.path.getsize(f"{folder}/{f}")
                print(f"  {folder}/{f}: {size:,} bytes")

if __name__ == "__main__":
    main()
