"""
PharmGKB 약물유전체학 데이터 수집
- 약물-유전자 관계 (약물 대사, 약물 반응)
- 개인별 유전체 변이에 따른 약물 반응 차이
"""
import requests
import pandas as pd
import time
import os
import json

PHARMGKB_API = "https://api.pharmgkb.org/v1/data"

CHEMICALS_PHARMGKB = {
    "Methamphetamine": "PA450464",
    "Cocaine": "PA449195",
    "Morphine": "PA450550",
    "Fentanyl": "PA449599",
    "Diazepam": "PA449283",
    "Ketamine": "PA450102",
    "THC": "PA451578",  # Dronabinol
    "Codeine": "PA449088",  # 참고용 - morphine 대사 관련
}

def search_pharmgkb_drug(drug_name):
    """PharmGKB에서 약물 검색"""
    url = f"{PHARMGKB_API}/chemical"
    params = {"name": drug_name}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        if data.get("data"):
            return data["data"]
    return []

def get_drug_relationships(pharmgkb_id):
    """약물 관련 관계 정보 (유전자, 질환, pathway)"""
    url = f"{PHARMGKB_API}/relationship"
    params = {
        "entity1Id": pharmgkb_id,
        "view": "min",
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get("data", [])
    return []

def get_drug_labels(drug_name):
    """FDA drug label annotations"""
    url = f"{PHARMGKB_API}/drugLabel"
    params = {"relatedChemicals.name": drug_name}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get("data", [])
    return []

def get_clinical_annotations(drug_name):
    """임상 주석 정보"""
    url = f"{PHARMGKB_API}/clinicalAnnotation"
    params = {"relatedChemicals.name": drug_name}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get("data", [])
    return []

def main():
    os.makedirs("pharmgkb", exist_ok=True)
    
    # 1. 약물 기본 정보 수집
    print("=== Step 1: PharmGKB Drug Search ===")
    drug_info = []
    for name in CHEMICALS_PHARMGKB:
        results = search_pharmgkb_drug(name)
        if results:
            for r in results[:1]:  # 첫 번째 결과
                drug_info.append({
                    "Chemical": name,
                    "PharmGKB_ID": r.get("id", ""),
                    "Name": r.get("name", ""),
                    "Type": r.get("type", ""),
                })
                print(f"  {name}: {r.get('id', 'N/A')}")
        else:
            print(f"  {name}: not found")
        time.sleep(0.5)
    
    pd.DataFrame(drug_info).to_csv("pharmgkb/drug_info.csv", index=False)
    
    # 2. 약물-유전자 관계
    print("\n=== Step 2: Drug-Gene Relationships ===")
    all_relationships = []
    for name, pgkb_id in CHEMICALS_PHARMGKB.items():
        print(f"  {name} ({pgkb_id}) 관계 조회 중...")
        rels = get_drug_relationships(pgkb_id)
        for rel in rels:
            entity2 = rel.get("entity2", {})
            all_relationships.append({
                "Chemical": name,
                "PharmGKB_ID": pgkb_id,
                "Related_Entity": entity2.get("name", ""),
                "Related_Type": entity2.get("type", ""),
                "Related_ID": entity2.get("id", ""),
                "Relationship_Type": rel.get("type", ""),
                "Evidence": rel.get("evidence", ""),
            })
        print(f"    관계: {len(rels)}")
        time.sleep(0.5)
    
    if all_relationships:
        rel_df = pd.DataFrame(all_relationships)
        rel_df.to_csv("pharmgkb/drug_relationships.csv", index=False)
        
        # 유전자 관계만 필터
        gene_rels = rel_df[rel_df["Related_Type"] == "Gene"]
        if not gene_rels.empty:
            gene_rels.to_csv("pharmgkb/drug_gene_relationships.csv", index=False)
            print(f"  유전자 관계: {len(gene_rels)}")
    
    # 3. 임상 주석
    print("\n=== Step 3: Clinical Annotations ===")
    all_clinical = []
    for name in CHEMICALS_PHARMGKB:
        annotations = get_clinical_annotations(name)
        for ann in annotations:
            genes = [g.get("name", "") for g in ann.get("relatedGenes", [])]
            all_clinical.append({
                "Chemical": name,
                "Level_of_Evidence": ann.get("evidenceLevel", ""),
                "Phenotype": ann.get("phenotypes", [{}])[0].get("name", "") if ann.get("phenotypes") else "",
                "Related_Genes": "; ".join(genes),
                "Score": ann.get("score", ""),
            })
        print(f"  {name}: {len(annotations)} annotations")
        time.sleep(0.5)
    
    if all_clinical:
        clin_df = pd.DataFrame(all_clinical)
        clin_df.to_csv("pharmgkb/clinical_annotations.csv", index=False)
    
    # 4. CYP 유전자 약물대사 상호작용 매트릭스
    print("\n=== Step 4: CYP-Drug Metabolism Matrix ===")
    cyp_genes = ["CYP2D6", "CYP3A4", "CYP2B6", "CYP2C19", "CYP1A2", "CYP2C9", "CYP2E1"]
    
    # 이미 수집한 relationship에서 CYP 관련 추출
    if all_relationships:
        rel_df = pd.DataFrame(all_relationships)
        cyp_matrix = []
        for name in CHEMICALS_PHARMGKB:
            drug_rels = rel_df[rel_df["Chemical"] == name]
            for cyp in cyp_genes:
                has_relation = any(cyp.lower() in str(r).lower() for _, r in drug_rels.iterrows())
                cyp_matrix.append({
                    "Chemical": name,
                    "CYP_Gene": cyp,
                    "Has_Interaction": has_relation,
                })
        
        cyp_df = pd.DataFrame(cyp_matrix)
        cyp_df.to_csv("pharmgkb/cyp_drug_matrix.csv", index=False)
    
    print("\n=== PharmGKB 데이터 수집 완료 ===")
    for f in os.listdir("pharmgkb"):
        size = os.path.getsize(f"pharmgkb/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
