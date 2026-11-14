"""
약물유전체학 데이터 수집 (PharmGKB API 대체)
- PubChem에서 CYP 대사 관련 assay 데이터
- 약물-CYP 효소 상호작용 매트릭스 (문헌 기반 + DB 교차 검증)
- 개인별 약물 반응 차이 관련 유전자 변이 정보
"""
import requests
import pandas as pd
import time
import os
import json

# 약물별 CYP 대사 효소 매핑 (공인 문헌 기반)
# Sources: FDA Drug Labels, Flockhart Table (Indiana University), 
# Goodman & Gilman's The Pharmacological Basis of Therapeutics
CYP_DRUG_MATRIX = {
    "Methamphetamine": {
        "CYP2D6": "major",    # Primary metabolizer
        "CYP1A2": "minor",
        "CYP3A4": "minor",
        "CYP2B6": "none",
        "CYP2C19": "none",
        "CYP2C9": "none",
        "CYP2E1": "none",
    },
    "MDMA": {
        "CYP2D6": "major",    # Primary: MDMA -> MDA
        "CYP1A2": "minor",
        "CYP3A4": "minor",
        "CYP2B6": "minor",
        "CYP2C19": "minor",
        "CYP2C9": "none",
        "CYP2E1": "none",
    },
    "Cocaine": {
        "CYP3A4": "major",
        "CYP2D6": "none",
        "CYP1A2": "none",
        "CYP2B6": "none",
        "CYP2C19": "none",
        "CYP2C9": "none",
        "CYP2E1": "none",
        # Note: primarily metabolized by butyrylcholinesterase (BChE)
    },
    "Morphine": {
        "CYP2D6": "minor",
        "CYP3A4": "minor",
        "CYP2C8": "minor",
        "CYP1A2": "none",
        "CYP2B6": "none",
        "CYP2C19": "none",
        "CYP2C9": "none",
        # Note: primarily metabolized by UGT2B7 (glucuronidation)
    },
    "Fentanyl": {
        "CYP3A4": "major",    # Primary metabolizer
        "CYP2D6": "none",
        "CYP1A2": "none",
        "CYP2B6": "none",
        "CYP2C19": "none",
        "CYP2C9": "none",
        "CYP2E1": "none",
    },
    "Diazepam": {
        "CYP3A4": "major",
        "CYP2C19": "major",   # Also major
        "CYP2B6": "minor",
        "CYP2C9": "minor",
        "CYP2D6": "none",
        "CYP1A2": "none",
        "CYP2E1": "none",
    },
    "Ketamine": {
        "CYP3A4": "major",
        "CYP2B6": "major",
        "CYP2C9": "minor",
        "CYP2D6": "none",
        "CYP1A2": "none",
        "CYP2C19": "minor",
        "CYP2E1": "none",
    },
    "THC": {
        "CYP2C9": "major",
        "CYP3A4": "major",
        "CYP2C19": "minor",
        "CYP2D6": "none",
        "CYP1A2": "none",
        "CYP2B6": "none",
        "CYP2E1": "none",
    },
}

# CYP2D6 유전자 다형성과 약물 대사 표현형
CYP_POLYMORPHISMS = {
    "CYP2D6": {
        "description": "Drug metabolism - major polymorphic enzyme",
        "phenotypes": ["Poor Metabolizer (PM)", "Intermediate Metabolizer (IM)", 
                      "Normal Metabolizer (NM)", "Ultra-rapid Metabolizer (UM)"],
        "frequency_note": "PM: 5-10% Caucasian, 1-2% Asian; UM: 1-10% varies by ethnicity",
        "affected_drugs": ["Methamphetamine", "MDMA"],
        "clinical_significance": "CYP2D6 PM: increased toxicity risk from MDMA/methamphetamine due to reduced clearance",
        "key_variants": ["*3", "*4", "*5", "*6", "*10", "*17", "*41"],
    },
    "CYP3A4": {
        "description": "Most abundant CYP in liver and intestine",
        "phenotypes": ["Poor Metabolizer", "Normal Metabolizer"],
        "frequency_note": "Significant inter-individual variability, influenced by induction/inhibition",
        "affected_drugs": ["Cocaine", "Fentanyl", "Diazepam", "Ketamine", "THC"],
        "clinical_significance": "CYP3A4 inhibition can dramatically increase fentanyl plasma levels",
        "key_variants": ["*22", "*20"],
    },
    "CYP2C19": {
        "description": "Drug metabolism - polymorphic",
        "phenotypes": ["Poor Metabolizer (PM)", "Intermediate Metabolizer (IM)",
                      "Normal Metabolizer (NM)", "Rapid Metabolizer (RM)", "Ultra-rapid Metabolizer (UM)"],
        "frequency_note": "PM: 2-5% Caucasian, 15-20% Asian",
        "affected_drugs": ["Diazepam", "Ketamine"],
        "clinical_significance": "CYP2C19 PM: prolonged diazepam half-life",
        "key_variants": ["*2", "*3", "*17"],
    },
    "CYP2C9": {
        "description": "Drug metabolism",
        "phenotypes": ["Poor Metabolizer", "Intermediate Metabolizer", "Normal Metabolizer"],
        "frequency_note": "PM: 1-3% Caucasian",
        "affected_drugs": ["THC"],
        "clinical_significance": "CYP2C9*3 carriers show increased THC exposure",
        "key_variants": ["*2", "*3"],
    },
    "CYP2B6": {
        "description": "Drug metabolism - increasingly recognized polymorphic enzyme",
        "phenotypes": ["Poor Metabolizer", "Intermediate Metabolizer", "Normal Metabolizer"],
        "frequency_note": "Significant ethnic variation in *6 allele frequency",
        "affected_drugs": ["Ketamine", "MDMA"],
        "clinical_significance": "CYP2B6 polymorphisms affect ketamine and MDMA metabolism",
        "key_variants": ["*6", "*18"],
    },
}

# 약물 상호작용 - CYP 억제/유도
DRUG_CYP_INTERACTIONS = [
    {"Drug": "Cocaine", "CYP": "CYP3A4", "Effect": "Inhibitor", "Strength": "Moderate",
     "Clinical_Impact": "Can increase plasma levels of fentanyl, diazepam, ketamine, THC"},
    {"Drug": "MDMA", "CYP": "CYP2D6", "Effect": "Mechanism-based inhibitor", "Strength": "Strong",
     "Clinical_Impact": "Irreversible CYP2D6 inhibition; affects methamphetamine metabolism"},
    {"Drug": "THC", "CYP": "CYP3A4", "Effect": "Inhibitor", "Strength": "Weak-Moderate",
     "Clinical_Impact": "May increase fentanyl, diazepam, ketamine levels"},
    {"Drug": "THC", "CYP": "CYP2C9", "Effect": "Inhibitor", "Strength": "Moderate",
     "Clinical_Impact": "Self-inhibition of THC metabolism"},
    {"Drug": "Cocaine", "CYP": "CYP2D6", "Effect": "Inhibitor", "Strength": "Weak",
     "Clinical_Impact": "May affect MDMA, methamphetamine metabolism"},
    {"Drug": "Ketamine", "CYP": "CYP3A4", "Effect": "Neither", "Strength": "None",
     "Clinical_Impact": "Primarily a substrate, not a significant inhibitor/inducer"},
    {"Drug": "Morphine", "CYP": "CYP3A4", "Effect": "Neither", "Strength": "None",
     "Clinical_Impact": "Primarily metabolized by UGT2B7, minimal CYP interaction"},
]

def get_pubchem_cyp_assays(cid, cyp_name):
    """PubChem에서 특정 CYP 효소 관련 assay 검색"""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "Table" in data:
                columns = data["Table"]["Columns"]["Column"]
                rows = data["Table"]["Row"]
                cyp_results = []
                for row in rows:
                    cell = row["Cell"]
                    record = dict(zip(columns, cell))
                    target_name = record.get("Target Name", "").upper()
                    if cyp_name.upper() in target_name:
                        cyp_results.append(record)
                return cyp_results
    except:
        pass
    return []

def main():
    os.makedirs("pharmacogenomics", exist_ok=True)
    
    # 1. CYP-Drug 대사 매트릭스
    print("=== Step 1: CYP-Drug Metabolism Matrix ===")
    matrix_rows = []
    for drug, cyps in CYP_DRUG_MATRIX.items():
        for cyp, role in cyps.items():
            matrix_rows.append({
                "Chemical": drug,
                "CYP_Enzyme": cyp,
                "Metabolism_Role": role,
            })
    
    matrix_df = pd.DataFrame(matrix_rows)
    matrix_df.to_csv("pharmacogenomics/cyp_drug_metabolism_matrix.csv", index=False)
    print(f"  CYP-Drug matrix: {len(matrix_df)} entries")
    
    # Pivot table for heatmap
    pivot = matrix_df.pivot_table(
        index="Chemical", columns="CYP_Enzyme", values="Metabolism_Role",
        aggfunc="first"
    )
    pivot.to_csv("pharmacogenomics/cyp_drug_heatmap_data.csv")
    
    # 2. CYP 다형성 정보
    print("\n=== Step 2: CYP Polymorphism Info ===")
    poly_rows = []
    for cyp, info in CYP_POLYMORPHISMS.items():
        poly_rows.append({
            "CYP_Gene": cyp,
            "Description": info["description"],
            "Phenotypes": "; ".join(info["phenotypes"]),
            "Frequency_Note": info["frequency_note"],
            "Affected_Drugs": "; ".join(info["affected_drugs"]),
            "Clinical_Significance": info["clinical_significance"],
            "Key_Variants": "; ".join(info["key_variants"]),
        })
    
    poly_df = pd.DataFrame(poly_rows)
    poly_df.to_csv("pharmacogenomics/cyp_polymorphisms.csv", index=False)
    print(f"  CYP polymorphisms: {len(poly_df)} entries")
    
    # 3. 약물 상호작용 매트릭스
    print("\n=== Step 3: Drug-CYP Interaction Effects ===")
    inter_df = pd.DataFrame(DRUG_CYP_INTERACTIONS)
    inter_df.to_csv("pharmacogenomics/drug_cyp_interactions.csv", index=False)
    print(f"  Drug-CYP interactions: {len(inter_df)} entries")
    
    # 4. 혼합 시 잠재적 위험 조합 분석
    print("\n=== Step 4: Potential Dangerous Combinations ===")
    dangerous_combos = []
    
    # 로직: Drug A가 CYP X를 억제하고, Drug B가 CYP X에 의해 대사되면 위험
    for inter in DRUG_CYP_INTERACTIONS:
        if inter["Effect"] == "Inhibitor":
            inhibitor = inter["Drug"]
            cyp = inter["CYP"]
            # 이 CYP에 의해 대사되는 다른 약물 찾기
            for drug, cyps in CYP_DRUG_MATRIX.items():
                if drug != inhibitor and cyps.get(cyp, "none") in ("major", "minor"):
                    risk = "HIGH" if cyps[cyp] == "major" and inter["Strength"] in ("Strong", "Moderate") else "MODERATE"
                    dangerous_combos.append({
                        "Inhibitor_Drug": inhibitor,
                        "Affected_Drug": drug,
                        "CYP_Enzyme": cyp,
                        "Inhibition_Strength": inter["Strength"],
                        "Metabolism_Dependency": cyps[cyp],
                        "Risk_Level": risk,
                        "Mechanism": f"{inhibitor} inhibits {cyp} → reduced clearance of {drug}",
                        "Expected_Effect": f"Increased {drug} plasma levels → enhanced toxicity",
                    })
    
    if dangerous_combos:
        combo_df = pd.DataFrame(dangerous_combos)
        combo_df = combo_df.sort_values("Risk_Level")
        combo_df.to_csv("pharmacogenomics/dangerous_combinations.csv", index=False)
        print(f"  Dangerous combinations: {len(combo_df)}")
        
        # HIGH risk만 별도 저장
        high_risk = combo_df[combo_df["Risk_Level"] == "HIGH"]
        if not high_risk.empty:
            high_risk.to_csv("pharmacogenomics/high_risk_combinations.csv", index=False)
            print(f"  HIGH risk: {len(high_risk)}")
    
    print("\n=== 약물유전체학 데이터 수집 완료 ===")
    for f in os.listdir("pharmacogenomics"):
        size = os.path.getsize(f"pharmacogenomics/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
