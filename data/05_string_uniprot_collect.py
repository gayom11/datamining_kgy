"""
STRING DB + UniProt 데이터 수집
- STRING: 단백질-단백질 상호작용 네트워크
- UniProt: 단백질 기능 정보, GO annotation
"""
import requests
import pandas as pd
import time
import os
import json

STRING_API = "https://string-db.org/api"
UNIPROT_API = "https://rest.uniprot.org"

# 주요 신경계 타겟 유전자 (약물 타겟 + 신경전달물질 수용체)
# 이 리스트는 PubChem/ChEMBL/CTDbase 수집 후 업데이트
KEY_GENES = [
    # 도파민 시스템
    "DRD1", "DRD2", "DRD3", "DRD4", "DRD5", "SLC6A3",  # DAT
    "TH", "DDC", "COMT", "MAOA", "MAOB",
    # 세로토닌 시스템  
    "HTR1A", "HTR1B", "HTR2A", "HTR2B", "HTR2C", "HTR3A", "SLC6A4",  # SERT
    "TPH1", "TPH2",
    # GABA 시스템
    "GABRA1", "GABRA2", "GABRB1", "GABRB2", "GABRG2",
    # 오피오이드 시스템
    "OPRM1", "OPRD1", "OPRK1",
    # 글루타메이트 시스템
    "GRIN1", "GRIN2A", "GRIN2B", "GRM1", "GRM5",
    # 카나비노이드 시스템
    "CNR1", "CNR2", "FAAH",
    # CYP 대사 효소
    "CYP2D6", "CYP3A4", "CYP2B6", "CYP2C19", "CYP1A2", "CYP2C9",
    # 신경독성 관련
    "BDNF", "NTRK2", "CASP3", "BAX", "BCL2", "TNF", "IL6", "IL1B",
    # 약물 수송체
    "ABCB1", "SLC22A1", "SLC22A2",
]

def get_string_interactions(genes, species=9606, score_threshold=400):
    """STRING에서 단백질 상호작용 네트워크 조회"""
    url = f"{STRING_API}/json/network"
    params = {
        "identifiers": "%0d".join(genes),
        "species": species,
        "required_score": score_threshold,
        "caller_identity": "neurotoxicity_project",
    }
    r = requests.post(url, data=params, timeout=60)
    if r.status_code == 200:
        return r.json()
    return []

def get_string_enrichment(genes, species=9606):
    """STRING functional enrichment (GO, KEGG)"""
    url = f"{STRING_API}/json/enrichment"
    params = {
        "identifiers": "%0d".join(genes),
        "species": species,
        "caller_identity": "neurotoxicity_project",
    }
    r = requests.post(url, data=params, timeout=60)
    if r.status_code == 200:
        return r.json()
    return []

def get_uniprot_info(gene_name, organism="human"):
    """UniProt에서 단백질 기능 정보 조회"""
    url = f"{UNIPROT_API}/uniprotkb/search"
    params = {
        "query": f"gene_exact:{gene_name} AND organism_name:{organism} AND reviewed:true",
        "format": "json",
        "size": 1,
        "fields": "accession,gene_names,protein_name,cc_function,cc_subcellular_location,go_p,go_f,go_c,xref_string",
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        if data.get("results"):
            return data["results"][0]
    return None

def main():
    os.makedirs("string", exist_ok=True)
    os.makedirs("uniprot", exist_ok=True)
    
    # 1. STRING PPI 네트워크
    print("=== Step 1: STRING PPI Network ===")
    # 유전자를 배치로 나눠서 조회 (API 제한)
    batch_size = 20
    all_interactions = []
    
    for i in range(0, len(KEY_GENES), batch_size):
        batch = KEY_GENES[i:i+batch_size]
        print(f"  Batch {i//batch_size + 1}: {batch[:3]}... ({len(batch)} genes)")
        interactions = get_string_interactions(batch)
        all_interactions.extend(interactions)
        time.sleep(1)
    
    # 전체 유전자로 한 번 더 (inter-batch 상호작용 포착)
    print("  전체 네트워크 조회...")
    full_interactions = get_string_interactions(KEY_GENES[:50])  # API 제한
    all_interactions.extend(full_interactions)
    
    # 중복 제거
    seen = set()
    unique_interactions = []
    for inter in all_interactions:
        key = tuple(sorted([inter.get("preferredName_A", ""), inter.get("preferredName_B", "")]))
        if key not in seen:
            seen.add(key)
            unique_interactions.append({
                "Protein_A": inter.get("preferredName_A", ""),
                "Protein_B": inter.get("preferredName_B", ""),
                "Score": inter.get("score", 0),
                "Nscore": inter.get("nscore", 0),
                "Fscore": inter.get("fscore", 0),
                "Pscore": inter.get("pscore", 0),
                "Ascore": inter.get("ascore", 0),
                "Escore": inter.get("escore", 0),
                "Dscore": inter.get("dscore", 0),
                "Tscore": inter.get("tscore", 0),
            })
    
    ppi_df = pd.DataFrame(unique_interactions)
    ppi_df.to_csv("string/ppi_network.csv", index=False)
    print(f"  PPI interactions: {len(ppi_df)}")
    
    # 2. Functional Enrichment
    print("\n=== Step 2: Functional Enrichment ===")
    enrichment = get_string_enrichment(KEY_GENES[:50])
    enrich_records = []
    for e in enrichment:
        enrich_records.append({
            "Category": e.get("category", ""),
            "Term": e.get("term", ""),
            "Description": e.get("description", ""),
            "Count": e.get("number_of_genes", 0),
            "Strength": e.get("strength", 0),
            "FDR": e.get("fdr", 1),
            "Genes": ",".join(e.get("preferredNames", [])),
        })
    
    enrich_df = pd.DataFrame(enrich_records)
    enrich_df.to_csv("string/functional_enrichment.csv", index=False)
    print(f"  Enrichment terms: {len(enrich_df)}")
    
    # 3. UniProt 단백질 정보
    print("\n=== Step 3: UniProt Protein Info ===")
    uniprot_records = []
    for i, gene in enumerate(KEY_GENES):
        info = get_uniprot_info(gene)
        if info:
            # Extract function text
            func_text = ""
            if "comments" in info:
                for comment in info.get("comments", []):
                    if comment.get("commentType") == "FUNCTION":
                        texts = comment.get("texts", [])
                        if texts:
                            func_text = texts[0].get("value", "")
            
            uniprot_records.append({
                "Gene": gene,
                "UniProt_ID": info.get("primaryAccession", ""),
                "Protein_Name": info.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
                "Function": func_text[:500],  # 500자 제한
            })
        if (i+1) % 10 == 0:
            print(f"  처리: {i+1}/{len(KEY_GENES)}")
        time.sleep(0.5)
    
    uniprot_df = pd.DataFrame(uniprot_records)
    uniprot_df.to_csv("uniprot/protein_info.csv", index=False)
    print(f"  UniProt records: {len(uniprot_df)}")
    
    print("\n=== STRING/UniProt 데이터 수집 완료 ===")
    for folder in ["string", "uniprot"]:
        for f in os.listdir(folder):
            size = os.path.getsize(f"{folder}/{f}")
            print(f"  {folder}/{f}: {size:,} bytes")

if __name__ == "__main__":
    main()
