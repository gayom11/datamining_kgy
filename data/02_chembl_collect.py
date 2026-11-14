"""
ChEMBL 데이터 수집 스크립트
- 화학물질별 bioactivity 데이터, 타겟 단백질, 메커니즘 수집
"""
import requests
import pandas as pd
import time
import os

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

CHEMICALS = {
    "Methamphetamine": "CHEMBL1201202",
    "MDMA": "CHEMBL47766",
    "Cocaine": "CHEMBL370805",
    "Morphine": "CHEMBL70",
    "Fentanyl": "CHEMBL596",
    "Diazepam": "CHEMBL12",
    "Ketamine": "CHEMBL742",
    "THC": "CHEMBL465",  # Dronabinol
}

def search_chembl_id(name):
    """ChEMBL ID 검색"""
    url = f"{BASE_URL}/molecule/search.json?q={name}&limit=5"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if data.get("molecules"):
            return data["molecules"][0]["molecule_chembl_id"]
    return None

def get_activities(chembl_id, limit=300):
    """화합물의 bioactivity 데이터 수집"""
    url = f"{BASE_URL}/activity.json?molecule_chembl_id={chembl_id}&limit={limit}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data.get("activities", [])
    return []

def get_mechanisms(chembl_id):
    """약물 작용 메커니즘 수집"""
    url = f"{BASE_URL}/mechanism.json?molecule_chembl_id={chembl_id}&limit=100"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data.get("mechanisms", [])
    return []

def get_target_info(target_chembl_id):
    """타겟 상세 정보"""
    url = f"{BASE_URL}/target/{target_chembl_id}.json"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return {}

def main():
    os.makedirs("chembl", exist_ok=True)
    
    # 1. Bioactivity 데이터 수집
    print("=== Step 1: ChEMBL Bioactivity 수집 ===")
    all_activities = []
    for name, chembl_id in CHEMICALS.items():
        print(f"  {name} ({chembl_id}) 처리 중...")
        activities = get_activities(chembl_id)
        for act in activities:
            all_activities.append({
                "Chemical": name,
                "ChEMBL_ID": chembl_id,
                "Target_ChEMBL": act.get("target_chembl_id", ""),
                "Target_Name": act.get("target_pref_name", ""),
                "Target_Organism": act.get("target_organism", ""),
                "Activity_Type": act.get("standard_type", ""),
                "Activity_Value": act.get("standard_value", ""),
                "Activity_Units": act.get("standard_units", ""),
                "Activity_Relation": act.get("standard_relation", ""),
                "Assay_Type": act.get("assay_type", ""),
                "pChEMBL": act.get("pchembl_value", ""),
            })
        print(f"    Activity records: {len(activities)}")
        time.sleep(0.5)
    
    act_df = pd.DataFrame(all_activities)
    act_df.to_csv("chembl/bioactivities.csv", index=False)
    
    # 2. 작용 메커니즘 수집
    print("\n=== Step 2: Drug Mechanisms 수집 ===")
    all_mechs = []
    for name, chembl_id in CHEMICALS.items():
        mechs = get_mechanisms(chembl_id)
        for m in mechs:
            all_mechs.append({
                "Chemical": name,
                "ChEMBL_ID": chembl_id,
                "Mechanism": m.get("mechanism_of_action", ""),
                "Action_Type": m.get("action_type", ""),
                "Target_ChEMBL": m.get("target_chembl_id", ""),
                "Target_Name": m.get("target_name", ""),  
            })
        print(f"  {name}: {len(mechs)} mechanisms")
        time.sleep(0.5)
    
    mech_df = pd.DataFrame(all_mechs)
    mech_df.to_csv("chembl/mechanisms.csv", index=False)
    
    # 3. 고유 타겟 리스트 + 상세정보
    print("\n=== Step 3: Target 상세 정보 ===")
    unique_targets = set()
    for act in all_activities:
        if act["Target_ChEMBL"]:
            unique_targets.add(act["Target_ChEMBL"])
    
    target_details = []
    for i, tid in enumerate(list(unique_targets)[:100]):  # 상위 100개
        info = get_target_info(tid)
        if info:
            components = info.get("target_components", [])
            gene_name = ""
            uniprot_id = ""
            if components:
                for comp in components:
                    accessions = comp.get("target_component_xrefs", [])
                    for xref in accessions:
                        if xref.get("xref_src_db") == "UniProt":
                            uniprot_id = xref.get("xref_id", "")
                    gene_name = comp.get("target_component_synonyms", [{}])
                    
            target_details.append({
                "Target_ChEMBL": tid,
                "Target_Name": info.get("pref_name", ""),
                "Target_Type": info.get("target_type", ""),
                "Organism": info.get("organism", ""),
                "UniProt": uniprot_id,
            })
        if i % 10 == 0:
            print(f"  처리: {i+1}/{min(len(unique_targets), 100)}")
        time.sleep(0.3)
    
    target_df = pd.DataFrame(target_details)
    target_df.to_csv("chembl/targets.csv", index=False)
    
    # 4. 물질별 타겟 요약
    print("\n=== Step 4: Chemical-Target Summary ===")
    if not act_df.empty:
        # Human targets만 필터
        human_acts = act_df[act_df["Target_Organism"] == "Homo sapiens"].copy()
        summary = human_acts.groupby(["Chemical", "Target_Name"]).agg(
            n_activities=("Activity_Type", "count"),
            avg_pChEMBL=("pChEMBL", lambda x: pd.to_numeric(x, errors="coerce").mean()),
        ).reset_index()
        summary = summary.sort_values(["Chemical", "n_activities"], ascending=[True, False])
        summary.to_csv("chembl/chemical_target_summary.csv", index=False)
    
    print("\n=== ChEMBL 데이터 수집 완료 ===")
    for f in os.listdir("chembl"):
        size = os.path.getsize(f"chembl/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
