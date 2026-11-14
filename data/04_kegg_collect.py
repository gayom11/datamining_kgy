"""
KEGG 데이터 수집 스크립트
- 약물 대사 관련 pathway (Drug metabolism - cytochrome P450)
- 신경전달물질 관련 pathway
- 물질별 KEGG Drug/Compound 정보
"""
import requests
import pandas as pd
import time
import os
import re

KEGG_API = "https://rest.kegg.jp"

# 타겟 물질의 KEGG compound/drug ID
CHEMICALS_KEGG = {
    "Methamphetamine": {"compound": "C07098", "drug": "D08187"},
    "MDMA": {"compound": "C07577", "drug": None},
    "Cocaine": {"compound": "C01416", "drug": "D00110"},
    "Morphine": {"compound": "C01516", "drug": "D08233"},
    "Fentanyl": {"compound": "C07569", "drug": "D00320"},
    "Diazepam": {"compound": "C06948", "drug": "D00293"},
    "Ketamine": {"compound": "C07525", "drug": "D08098"},
    "THC": {"compound": "C06970", "drug": "D00306"},  # Dronabinol
}

# 신경계 관련 KEGG pathway
NEURO_PATHWAYS = [
    "hsa04080",  # Neuroactive ligand-receptor interaction
    "hsa04726",  # Serotonergic synapse
    "hsa04728",  # Dopaminergic synapse
    "hsa04727",  # GABAergic synapse
    "hsa04725",  # Cholinergic synapse
    "hsa04724",  # Glutamatergic synapse
    "hsa04723",  # Retrograde endocannabinoid signaling
    "hsa04721",  # Synaptic vesicle cycle
    "hsa04720",  # Long-term potentiation
    "hsa00982",  # Drug metabolism - cytochrome P450
    "hsa00983",  # Drug metabolism - other enzymes
    "hsa04014",  # Ras signaling pathway
    "hsa04010",  # MAPK signaling pathway
    "hsa04020",  # Calcium signaling pathway
    "hsa04064",  # NF-kappa B signaling pathway
    "hsa04210",  # Apoptosis
]

def get_pathway_genes(pathway_id):
    """KEGG pathway에 속한 유전자 목록"""
    url = f"{KEGG_API}/link/hsa/{pathway_id}"
    r = requests.get(url)
    genes = []
    if r.status_code == 200 and r.text.strip():
        for line in r.text.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                gene_id = parts[1].replace("hsa:", "")
                genes.append(gene_id)
    return genes

def get_pathway_info(pathway_id):
    """Pathway 기본 정보"""
    url = f"{KEGG_API}/get/{pathway_id}"
    r = requests.get(url)
    if r.status_code == 200:
        name_match = re.search(r"NAME\s+(.+)", r.text)
        name = name_match.group(1).strip() if name_match else ""
        # Remove " - Homo sapiens (human)" suffix
        name = re.sub(r"\s*-\s*Homo sapiens.*$", "", name)
        return name
    return ""

def get_drug_targets(drug_id):
    """KEGG Drug 타겟 정보"""
    url = f"{KEGG_API}/get/{drug_id}"
    r = requests.get(url)
    targets = []
    if r.status_code == 200:
        in_target = False
        for line in r.text.split("\n"):
            if line.startswith("TARGET"):
                in_target = True
                target_text = line.replace("TARGET", "").strip()
                if target_text:
                    targets.append(target_text)
            elif in_target:
                if line.startswith(" ") or line.startswith("\t"):
                    targets.append(line.strip())
                else:
                    in_target = False
    return targets

def get_gene_name(gene_id):
    """KEGG gene ID로 유전자 이름 조회"""
    url = f"{KEGG_API}/get/hsa:{gene_id}"
    r = requests.get(url)
    if r.status_code == 200:
        name_match = re.search(r"NAME\s+(.+)", r.text)
        if name_match:
            return name_match.group(1).strip().split(",")[0]
    return ""

def main():
    os.makedirs("kegg", exist_ok=True)
    
    # 1. 신경계 pathway 유전자 수집
    print("=== Step 1: Neuro Pathway Genes ===")
    all_pathway_genes = []
    pathway_names = {}
    
    for pw_id in NEURO_PATHWAYS:
        pw_name = get_pathway_info(pw_id)
        pathway_names[pw_id] = pw_name
        genes = get_pathway_genes(pw_id)
        for g in genes:
            all_pathway_genes.append({
                "Pathway_ID": pw_id,
                "Pathway_Name": pw_name,
                "Gene_ID": g,
            })
        print(f"  {pw_id} ({pw_name}): {len(genes)} genes")
        time.sleep(0.5)
    
    pg_df = pd.DataFrame(all_pathway_genes)
    pg_df.to_csv("kegg/neuro_pathway_genes.csv", index=False)
    
    # 2. KEGG Drug 타겟 정보
    print("\n=== Step 2: Drug Target Info ===")
    all_drug_targets = []
    for name, ids in CHEMICALS_KEGG.items():
        drug_id = ids.get("drug")
        if drug_id:
            targets = get_drug_targets(drug_id)
            for t in targets:
                all_drug_targets.append({
                    "Chemical": name,
                    "KEGG_Drug": drug_id,
                    "Target": t,
                })
            print(f"  {name} ({drug_id}): {len(targets)} targets")
            time.sleep(0.5)
    
    dt_df = pd.DataFrame(all_drug_targets)
    dt_df.to_csv("kegg/drug_targets.csv", index=False)
    
    # 3. Pathway 요약 저장
    pw_summary = pd.DataFrame([
        {"Pathway_ID": k, "Pathway_Name": v, "Gene_Count": len(pg_df[pg_df["Pathway_ID"] == k])}
        for k, v in pathway_names.items()
    ])
    pw_summary.to_csv("kegg/pathway_summary.csv", index=False)
    
    # 4. CYP 효소 (약물 대사) 관련 유전자 추출
    print("\n=== Step 3: CYP Enzyme Genes ===")
    cyp_pathways = ["hsa00982", "hsa00983"]
    cyp_genes = set()
    for pw_id in cyp_pathways:
        genes = get_pathway_genes(pw_id)
        cyp_genes.update(genes)
    
    cyp_info = []
    for i, gid in enumerate(sorted(cyp_genes)):
        gname = get_gene_name(gid)
        cyp_info.append({"Gene_ID": gid, "Gene_Name": gname})
        if i % 20 == 0:
            print(f"  CYP gene {i+1}/{len(cyp_genes)} 조회 중...")
        time.sleep(0.3)
    
    cyp_df = pd.DataFrame(cyp_info)
    cyp_df.to_csv("kegg/cyp_metabolism_genes.csv", index=False)
    
    print("\n=== KEGG 데이터 수집 완료 ===")
    for f in os.listdir("kegg"):
        size = os.path.getsize(f"kegg/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
