"""
교차 데이터베이스 분석 (Cross-Database Integration)
- 서로 다른 DB에서 수집한 데이터 간 연결
- 약물-유전자-질환-pathway 네트워크 구축
- 공통 유전자/단백질 식별
"""
import pandas as pd
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_data():
    """수집된 모든 데이터 로드"""
    data = {}
    
    # PubChem
    data["pubchem_targets"] = pd.read_csv(os.path.join(DATA_DIR, "pubchem", "bioassay_gene_targets.csv"))
    data["pubchem_assays"] = pd.read_csv(os.path.join(DATA_DIR, "pubchem", "active_assays.csv"))
    data["pubchem_props"] = pd.read_csv(os.path.join(DATA_DIR, "pubchem", "compound_properties.csv"))
    
    # ChEMBL
    data["chembl_activities"] = pd.read_csv(os.path.join(DATA_DIR, "chembl", "bioactivities.csv"))
    data["chembl_targets"] = pd.read_csv(os.path.join(DATA_DIR, "chembl", "targets.csv"))
    data["chembl_summary"] = pd.read_csv(os.path.join(DATA_DIR, "chembl", "chemical_target_summary.csv"))
    
    # KEGG
    data["kegg_pathways"] = pd.read_csv(os.path.join(DATA_DIR, "kegg", "neuro_pathway_genes.csv"))
    data["kegg_drug_targets"] = pd.read_csv(os.path.join(DATA_DIR, "kegg", "drug_targets.csv"))
    data["kegg_cyp"] = pd.read_csv(os.path.join(DATA_DIR, "kegg", "cyp_metabolism_genes.csv"))
    
    # STRING/UniProt
    data["string_ppi"] = pd.read_csv(os.path.join(DATA_DIR, "string", "ppi_network.csv"))
    data["string_enrichment"] = pd.read_csv(os.path.join(DATA_DIR, "string", "functional_enrichment.csv"))
    data["uniprot"] = pd.read_csv(os.path.join(DATA_DIR, "uniprot", "protein_info.csv"))
    
    # Open Targets / NCBI
    data["ot_disease_targets"] = pd.read_csv(os.path.join(DATA_DIR, "opentargets", "disease_target_associations.csv"))
    data["ncbi_chem_genes"] = pd.read_csv(os.path.join(DATA_DIR, "ncbi_gene", "chemical_gene_associations.csv"))
    
    # DisGeNET (NCBI based)
    data["disease_genes"] = pd.read_csv(os.path.join(DATA_DIR, "disgenet", "disease_gene_associations.csv"))
    
    # FDA Adverse Events
    data["adverse_events"] = pd.read_csv(os.path.join(DATA_DIR, "sider_fda", "adverse_events.csv"))
    data["neuro_adverse"] = pd.read_csv(os.path.join(DATA_DIR, "sider_fda", "neuro_adverse_events.csv"))
    
    # Pharmacogenomics
    data["cyp_matrix"] = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "cyp_drug_metabolism_matrix.csv"))
    data["dangerous_combos"] = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "dangerous_combinations.csv"))
    data["high_risk"] = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "high_risk_combinations.csv"))
    
    return data

def analyze_shared_targets(data):
    """약물 간 공유 타겟 유전자 분석"""
    print("\n=== 1. Shared Drug Targets Analysis ===")
    
    # ChEMBL에서 Human 타겟만
    chembl = data["chembl_activities"]
    human_targets = chembl[chembl["Target_Organism"] == "Homo sapiens"].copy()
    
    # 약물별 타겟 세트
    drug_targets = {}
    for drug in human_targets["Chemical"].unique():
        targets = set(human_targets[human_targets["Chemical"] == drug]["Target_Name"].dropna().unique())
        drug_targets[drug] = targets
        print(f"  {drug}: {len(targets)} unique targets")
    
    # 쌍별 공유 타겟
    chemicals = sorted(drug_targets.keys())
    overlap_records = []
    for i, d1 in enumerate(chemicals):
        for d2 in chemicals[i+1:]:
            shared = drug_targets[d1] & drug_targets[d2]
            if shared:
                overlap_records.append({
                    "Drug_1": d1,
                    "Drug_2": d2,
                    "Shared_Target_Count": len(shared),
                    "Shared_Targets": "; ".join(sorted(shared)[:20]),  # top 20
                    "Drug1_Total": len(drug_targets[d1]),
                    "Drug2_Total": len(drug_targets[d2]),
                    "Jaccard_Index": len(shared) / len(drug_targets[d1] | drug_targets[d2]),
                })
    
    overlap_df = pd.DataFrame(overlap_records)
    overlap_df = overlap_df.sort_values("Shared_Target_Count", ascending=False)
    overlap_df.to_csv("shared_drug_targets.csv", index=False)
    print(f"\n  Total drug pairs with shared targets: {len(overlap_df)}")
    print(f"  Top pairs:")
    for _, row in overlap_df.head(5).iterrows():
        print(f"    {row['Drug_1']}-{row['Drug_2']}: {row['Shared_Target_Count']} shared (Jaccard={row['Jaccard_Index']:.3f})")
    
    return overlap_df

def analyze_neuro_gene_overlap(data):
    """약물 타겟과 신경질환 관련 유전자 교차 분석"""
    print("\n=== 2. Drug Target ∩ Neuro Disease Gene Overlap ===")
    
    # 약물 타겟 유전자 (NCBI Gene 기반 - gene symbol 사용)
    ncbi = data["ncbi_chem_genes"]
    drug_genes = {}
    for drug in ncbi["Chemical"].unique():
        genes = set(ncbi[ncbi["Chemical"] == drug]["Symbol"].dropna().unique())
        drug_genes[drug] = genes
    
    # 질환 관련 유전자
    disease_df = data["disease_genes"]
    disease_genes = {}
    for disease in disease_df["Disease"].unique():
        genes = set(disease_df[disease_df["Disease"] == disease]["Gene_Symbol"].dropna().unique())
        disease_genes[disease] = genes
    
    # 교차 분석
    overlap_records = []
    for drug, d_genes in drug_genes.items():
        for disease, dis_genes in disease_genes.items():
            shared = d_genes & dis_genes
            if shared:
                overlap_records.append({
                    "Chemical": drug,
                    "Disease": disease,
                    "Overlap_Count": len(shared),
                    "Overlap_Genes": "; ".join(sorted(shared)[:15]),
                    "Drug_Gene_Count": len(d_genes),
                    "Disease_Gene_Count": len(dis_genes),
                })
    
    if overlap_records:
        ol_df = pd.DataFrame(overlap_records)
        ol_df = ol_df.sort_values("Overlap_Count", ascending=False)
        ol_df.to_csv("drug_disease_gene_overlap.csv", index=False)
        print(f"  Drug-Disease pairs with gene overlap: {len(ol_df)}")
        for _, row in ol_df.head(10).iterrows():
            print(f"    {row['Chemical']}-{row['Disease']}: {row['Overlap_Count']} genes")
        return ol_df
    
    return pd.DataFrame()

def analyze_pathway_enrichment(data):
    """약물 타겟 유전자의 pathway 분포 분석"""
    print("\n=== 3. Drug Target Pathway Distribution ===")
    
    # KEGG pathway 유전자 목록
    kegg = data["kegg_pathways"]
    
    # NCBI 약물-유전자에서 Gene ID 추출
    ncbi = data["ncbi_chem_genes"]
    
    # Gene ID 기반 매칭
    pathway_hits = []
    for drug in ncbi["Chemical"].unique():
        drug_gene_ids = set(ncbi[ncbi["Chemical"] == drug]["Gene_ID"].astype(str).unique())
        
        for pw_name in kegg["Pathway_Name"].unique():
            pw_genes = set(kegg[kegg["Pathway_Name"] == pw_name]["Gene_ID"].astype(str).unique())
            overlap = drug_gene_ids & pw_genes
            if overlap:
                pathway_hits.append({
                    "Chemical": drug,
                    "Pathway": pw_name,
                    "Pathway_ID": kegg[kegg["Pathway_Name"] == pw_name]["Pathway_ID"].iloc[0],
                    "Hit_Count": len(overlap),
                    "Pathway_Size": len(pw_genes),
                    "Hit_Ratio": len(overlap) / len(pw_genes),
                })
    
    if pathway_hits:
        ph_df = pd.DataFrame(pathway_hits)
        ph_df = ph_df.sort_values(["Chemical", "Hit_Count"], ascending=[True, False])
        ph_df.to_csv("drug_pathway_hits.csv", index=False)
        print(f"  Drug-Pathway connections: {len(ph_df)}")
        return ph_df
    
    return pd.DataFrame()

def analyze_ppi_drug_network(data):
    """단백질 상호작용 네트워크 내 약물 타겟 분석"""
    print("\n=== 4. PPI Network Drug Target Analysis ===")
    
    ppi = data["string_ppi"]
    
    # 약물별 타겟 유전자 (PubChem assay 기반)
    # ChEMBL에서 human target name 추출
    chembl = data["chembl_activities"]
    human = chembl[chembl["Target_Organism"] == "Homo sapiens"]
    
    drug_target_names = {}
    for drug in human["Chemical"].unique():
        targets = set(human[human["Chemical"] == drug]["Target_Name"].dropna().unique())
        drug_target_names[drug] = targets
    
    # PPI 네트워크에서 약물 타겟 간 연결 분석
    ppi_proteins = set(ppi["Protein_A"].unique()) | set(ppi["Protein_B"].unique())
    print(f"  PPI network proteins: {len(ppi_proteins)}")
    
    # 네트워크 허브 분석
    from collections import Counter
    degree = Counter()
    for _, row in ppi.iterrows():
        degree[row["Protein_A"]] += 1
        degree[row["Protein_B"]] += 1
    
    hub_df = pd.DataFrame([
        {"Protein": k, "Degree": v} for k, v in degree.most_common(30)
    ])
    hub_df.to_csv("ppi_hub_proteins.csv", index=False)
    print(f"  Top hub proteins:")
    for _, row in hub_df.head(10).iterrows():
        print(f"    {row['Protein']}: degree={row['Degree']}")
    
    return hub_df

def build_integrated_summary(data):
    """통합 요약 보고서 데이터 생성"""
    print("\n=== 5. Integrated Summary ===")
    
    summary = {
        "databases_used": [
            {"name": "PubChem", "type": "Chemical/Bioassay", "records": len(data["pubchem_assays"])},
            {"name": "ChEMBL", "type": "Bioactivity", "records": len(data["chembl_activities"])},
            {"name": "KEGG", "type": "Pathway", "records": len(data["kegg_pathways"])},
            {"name": "STRING", "type": "PPI Network", "records": len(data["string_ppi"])},
            {"name": "UniProt", "type": "Protein Info", "records": len(data["uniprot"])},
            {"name": "Open Targets", "type": "Disease-Target", "records": len(data["ot_disease_targets"])},
            {"name": "NCBI Gene", "type": "Chemical-Gene", "records": len(data["ncbi_chem_genes"])},
            {"name": "OpenFDA", "type": "Adverse Events", "records": len(data["adverse_events"])},
            {"name": "Pharmacogenomics", "type": "Drug Metabolism", "records": len(data["cyp_matrix"])},
        ],
        "chemicals_analyzed": 8,
        "high_risk_combinations": len(data["high_risk"]),
        "total_ppi_interactions": len(data["string_ppi"]),
    }
    
    with open("integrated_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Summary table
    db_summary = pd.DataFrame(summary["databases_used"])
    db_summary.to_csv("database_summary.csv", index=False)
    
    print(f"  Databases used: {len(summary['databases_used'])}")
    print(f"  Total records across databases: {sum(d['records'] for d in summary['databases_used'])}")
    
    return summary

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Loading data...")
    data = load_data()
    print("Data loaded successfully.\n")
    
    # 분석 실행
    shared_targets = analyze_shared_targets(data)
    neuro_overlap = analyze_neuro_gene_overlap(data)
    pathway_hits = analyze_pathway_enrichment(data)
    hub_proteins = analyze_ppi_drug_network(data)
    summary = build_integrated_summary(data)
    
    print("\n=== 교차 분석 완료 ===")
    for f in os.listdir("."):
        if f.endswith((".csv", ".json")) and not f.endswith(".py"):
            size = os.path.getsize(f)
            print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
