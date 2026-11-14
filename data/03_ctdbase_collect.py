"""
CTDbase (Comparative Toxicogenomics Database) 데이터 수집
- 화학물질-유전자 상호작용
- 화학물질-질환 연관
- 유전자-질환 연관 (신경계 질환)
CTDbase API: http://ctdbase.org/tools/batchQuery.go
"""
import requests
import pandas as pd
import time
import os
import csv
import io

BASE_URL = "http://ctdbase.org/tools/batchQuery.go"

# CTDbase에서 사용하는 화학물질 MeSH ID
CHEMICALS = {
    "Methamphetamine": "D008694",
    "MDMA": "D018817",  # N-Methyl-3,4-methylenedioxyamphetamine  
    "Cocaine": "D003042",
    "Morphine": "D009020",
    "Fentanyl": "D005283",
    "Diazepam": "D003975",
    "Ketamine": "D007649",
    "THC": "D013759",  # Tetrahydrocannabinol (Dronabinol)
}

# 신경/정신계 질환 MeSH terms
NEURO_DISEASES = {
    "Neurotoxicity Syndromes": "D020258",
    "Nervous System Diseases": "D009422",
    "Mental Disorders": "D001523",
    "Neurodegenerative Diseases": "D019636",
    "Substance-Related Disorders": "D019966",
    "Serotonin Syndrome": "D020230",
    "Seizures": "D012640",
    "Psychotic Disorders": "D011618",
    "Depressive Disorder": "D003866",
    "Schizophrenia": "D012559",
}

def query_ctd_chem_gene(mesh_id, chemical_name):
    """화학물질-유전자 상호작용 조회"""
    url = f"http://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms={mesh_id}&report=genes_curated&format=csv"
    r = requests.get(url, timeout=60)
    if r.status_code == 200:
        # CTD CSV parsing
        lines = r.text.strip().split("\n")
        # Skip comment lines starting with #
        data_lines = [l for l in lines if not l.startswith("#")]
        if data_lines:
            reader = csv.reader(io.StringIO("\n".join(data_lines)))
            records = list(reader)
            if len(records) > 1:
                header = records[0]
                rows = records[1:]
                df = pd.DataFrame(rows, columns=header)
                df["Query_Chemical"] = chemical_name
                return df
    return pd.DataFrame()

def query_ctd_chem_disease(mesh_id, chemical_name):
    """화학물질-질환 연관 조회"""
    url = f"http://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms={mesh_id}&report=diseases_curated&format=csv"
    r = requests.get(url, timeout=60)
    if r.status_code == 200:
        lines = r.text.strip().split("\n")
        data_lines = [l for l in lines if not l.startswith("#")]
        if data_lines:
            reader = csv.reader(io.StringIO("\n".join(data_lines)))
            records = list(reader)
            if len(records) > 1:
                header = records[0]
                rows = records[1:]
                df = pd.DataFrame(rows, columns=header)
                df["Query_Chemical"] = chemical_name
                return df
    return pd.DataFrame()

def query_ctd_chem_pathway(mesh_id, chemical_name):
    """화학물질-pathway 연관 조회"""
    url = f"http://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms={mesh_id}&report=pathways_enriched&format=csv"
    r = requests.get(url, timeout=60)
    if r.status_code == 200:
        lines = r.text.strip().split("\n")
        data_lines = [l for l in lines if not l.startswith("#")]
        if data_lines:
            reader = csv.reader(io.StringIO("\n".join(data_lines)))
            records = list(reader)
            if len(records) > 1:
                header = records[0]
                rows = records[1:]
                df = pd.DataFrame(rows, columns=header)
                df["Query_Chemical"] = chemical_name
                return df
    return pd.DataFrame()

def main():
    os.makedirs("ctdbase", exist_ok=True)
    
    # 1. 화학물질-유전자 상호작용
    print("=== Step 1: Chemical-Gene Interactions ===")
    all_chem_gene = []
    for name, mesh_id in CHEMICALS.items():
        print(f"  {name} ({mesh_id}) 처리 중...")
        df = query_ctd_chem_gene(mesh_id, name)
        if not df.empty:
            all_chem_gene.append(df)
            print(f"    Gene interactions: {len(df)}")
        else:
            print(f"    No data found")
        time.sleep(2)  # CTDbase rate limit 준수
    
    if all_chem_gene:
        cg_df = pd.concat(all_chem_gene, ignore_index=True)
        cg_df.to_csv("ctdbase/chemical_gene_interactions.csv", index=False)
        print(f"  총 {len(cg_df)} gene interactions 저장")
    
    # 2. 화학물질-질환 연관
    print("\n=== Step 2: Chemical-Disease Associations ===")
    all_chem_disease = []
    for name, mesh_id in CHEMICALS.items():
        print(f"  {name} 처리 중...")
        df = query_ctd_chem_disease(mesh_id, name)
        if not df.empty:
            all_chem_disease.append(df)
            print(f"    Disease associations: {len(df)}")
        else:
            print(f"    No data found")
        time.sleep(2)
    
    if all_chem_disease:
        cd_df = pd.concat(all_chem_disease, ignore_index=True)
        cd_df.to_csv("ctdbase/chemical_disease_associations.csv", index=False)
        print(f"  총 {len(cd_df)} disease associations 저장")
    
    # 3. 화학물질-Pathway 연관
    print("\n=== Step 3: Chemical-Pathway Associations ===")
    all_chem_pathway = []
    for name, mesh_id in CHEMICALS.items():
        print(f"  {name} 처리 중...")
        df = query_ctd_chem_pathway(mesh_id, name)
        if not df.empty:
            all_chem_pathway.append(df)
            print(f"    Pathway associations: {len(df)}")
        else:
            print(f"    No data found")
        time.sleep(2)
    
    if all_chem_pathway:
        cp_df = pd.concat(all_chem_pathway, ignore_index=True)
        cp_df.to_csv("ctdbase/chemical_pathway_associations.csv", index=False)
        print(f"  총 {len(cp_df)} pathway associations 저장")
    
    print("\n=== CTDbase 데이터 수집 완료 ===")
    for f in os.listdir("ctdbase"):
        size = os.path.getsize(f"ctdbase/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
