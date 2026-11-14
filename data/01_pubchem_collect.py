"""
PubChem 데이터 수집 스크립트
- 타겟 화학물질의 CID, 기본 정보, bioassay 정보, 유전자 타겟 수집
"""
import requests
import pandas as pd
import time
import json
import os

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# 타겟 물질 리스트
CHEMICALS = {
    "Methamphetamine": None,
    "MDMA": None,
    "Cocaine": None,
    "Morphine": None,
    "Fentanyl": None,
    "Diazepam": None,
    "Ketamine": None,
    "THC": None,  # Delta-9-THC
}

def get_cid(name):
    """화학물질 이름으로 PubChem CID 검색"""
    url = f"{BASE_URL}/compound/name/{name}/cids/JSON"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data["IdentifierList"]["CID"][0]
    return None

def get_compound_properties(cid):
    """화합물 기본 물성 정보"""
    props = "MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,InChIKey"
    url = f"{BASE_URL}/compound/cid/{cid}/property/{props}/JSON"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()["PropertyTable"]["Properties"][0]
    return {}

def get_gene_targets(cid):
    """PubChem에서 화합물 관련 유전자 타겟 수집"""
    url = f"{BASE_URL}/compound/cid/{cid}/assaysummary/JSON"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if "Table" in data:
            columns = data["Table"]["Columns"]["Column"]
            rows = data["Table"]["Row"]
            records = []
            for row in rows[:500]:  # 최대 500개
                cell = row["Cell"]
                record = dict(zip(columns, cell))
                records.append(record)
            return records
    return []

def get_bioassay_targets(cid):
    """화합물 관련 bioassay에서 유전자/단백질 타겟 추출"""
    url = f"{BASE_URL}/compound/cid/{cid}/assaysummary/JSON"
    r = requests.get(url)
    genes = set()
    proteins = set()
    if r.status_code == 200:
        data = r.json()
        if "Table" in data:
            columns = data["Table"]["Columns"]["Column"]
            rows = data["Table"]["Row"]
            for row in rows:
                cell = row["Cell"]
                record = dict(zip(columns, cell))
                if "Target GeneID" in record and record["Target GeneID"]:
                    genes.add(record["Target GeneID"])
                if "Target Name" in record and record["Target Name"]:
                    proteins.add(record["Target Name"])
    return list(genes), list(proteins)

def main():
    os.makedirs("pubchem", exist_ok=True)
    
    # 1. CID 수집
    print("=== Step 1: CID 수집 ===")
    for name in CHEMICALS:
        cid = get_cid(name)
        CHEMICALS[name] = cid
        print(f"  {name}: CID={cid}")
        time.sleep(0.3)
    
    # CID 매핑 저장
    cid_df = pd.DataFrame([
        {"Chemical": k, "CID": v} for k, v in CHEMICALS.items()
    ])
    cid_df.to_csv("pubchem/chemical_cids.csv", index=False)
    
    # 2. 화합물 물성 정보
    print("\n=== Step 2: 화합물 물성 정보 ===")
    props_list = []
    for name, cid in CHEMICALS.items():
        if cid:
            props = get_compound_properties(cid)
            props["Chemical"] = name
            props_list.append(props)
            print(f"  {name}: MW={props.get('MolecularWeight', 'N/A')}")
            time.sleep(0.3)
    
    props_df = pd.DataFrame(props_list)
    props_df.to_csv("pubchem/compound_properties.csv", index=False)
    
    # 3. 유전자 타겟 수집
    print("\n=== Step 3: Bioassay 타겟 수집 ===")
    all_targets = []
    for name, cid in CHEMICALS.items():
        if cid:
            print(f"  {name} (CID={cid}) 처리 중...")
            genes, proteins = get_bioassay_targets(cid)
            for g in genes:
                all_targets.append({
                    "Chemical": name,
                    "CID": cid,
                    "GeneID": g,
                    "Type": "Gene"
                })
            print(f"    유전자 {len(genes)}개, 단백질 {len(proteins)}개")
            time.sleep(1)  # rate limit
    
    targets_df = pd.DataFrame(all_targets)
    targets_df.to_csv("pubchem/bioassay_gene_targets.csv", index=False)
    
    # 4. Assay summary 상세 (active 결과만)
    print("\n=== Step 4: Active Assay 결과 수집 ===")
    all_assays = []
    for name, cid in CHEMICALS.items():
        if cid:
            print(f"  {name} assay 수집 중...")
            records = get_gene_targets(cid)
            active_records = [r for r in records if r.get("Activity Outcome", "") == "Active"]
            for r in active_records:
                r["Chemical"] = name
                all_assays.append(r)
            print(f"    Active assay: {len(active_records)}개 (전체 {len(records)}개)")
            time.sleep(1)
    
    if all_assays:
        assay_df = pd.DataFrame(all_assays)
        assay_df.to_csv("pubchem/active_assays.csv", index=False)
    
    print("\n=== PubChem 데이터 수집 완료 ===")
    print(f"저장 위치: pubchem/")
    for f in os.listdir("pubchem"):
        size = os.path.getsize(f"pubchem/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
