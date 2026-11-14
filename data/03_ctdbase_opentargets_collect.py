"""
Open Targets Platform + NCBI Gene 데이터 수집
- Open Targets: 약물-타겟-질환 연관 (CTDbase 대체)
- NCBI Gene: 화학물질-유전자 연관 (GeneRIF)
CTDbase batch query가 현재 HTML만 반환하므로 대체 소스 사용
"""
import requests
import pandas as pd
import time
import os
import json

# Open Targets GraphQL API
OT_API = "https://api.platform.opentargets.org/api/v4/graphql"

# NCBI E-utilities
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

CHEMICALS = [
    "Methamphetamine", "MDMA", "Cocaine", "Morphine",
    "Fentanyl", "Diazepam", "Ketamine", "THC",
]

# 신경/정신계 질환 EFO IDs (Open Targets)
NEURO_DISEASE_EFO = {
    "nervous system disease": "EFO_0000618",
    "mental disorder": "MONDO_0002025",
    "neurodegenerative disease": "EFO_0005772",
    "substance dependence": "EFO_0003894",
    "schizophrenia": "MONDO_0005090",
    "major depressive disorder": "EFO_0003761",
    "seizure": "HP_0001250",
    "anxiety disorder": "EFO_0004209",
    "Parkinson disease": "MONDO_0005180",
    "psychotic disorder": "EFO_0005407",
}

def query_opentargets_disease_targets(disease_efo_id, size=200):
    """Open Targets에서 질환-타겟 연관 조회"""
    query = """
    query diseaseTargets($efoId: String!, $size: Int!) {
      disease(efoId: $efoId) {
        id
        name
        associatedTargets(page: {index: 0, size: $size}) {
          count
          rows {
            target {
              id
              approvedSymbol
              approvedName
            }
            score
            datatypeScores {
              id
              score
            }
          }
        }
      }
    }
    """
    r = requests.post(OT_API, json={
        "query": query,
        "variables": {"efoId": disease_efo_id, "size": size}
    }, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get("data", {}).get("disease", {})
    return {}

def query_opentargets_drug_targets(drug_name, size=50):
    """Open Targets에서 약물의 타겟 검색"""
    query = """
    query drugSearch($name: String!, $size: Int!) {
      search(queryString: $name, entityNames: ["drug"], page: {index: 0, size: $size}) {
        hits {
          id
          name
          entity
          object {
            ... on Drug {
              id
              name
              mechanismsOfAction {
                rows {
                  mechanismOfAction
                  targets {
                    id
                    approvedSymbol
                    approvedName
                  }
                  actionType
                }
              }
              linkedTargets {
                count
                rows {
                  id
                  approvedSymbol
                  approvedName
                }
              }
            }
          }
        }
      }
    }
    """
    r = requests.post(OT_API, json={
        "query": query,
        "variables": {"name": drug_name, "size": size}
    }, timeout=30)
    if r.status_code == 200:
        return r.json().get("data", {}).get("search", {}).get("hits", [])
    return []

def ncbi_gene_search(query_term, retmax=100):
    """NCBI Gene에서 검색"""
    url = f"{NCBI_BASE}/esearch.fcgi"
    params = {
        "db": "gene",
        "term": f'{query_term} AND "Homo sapiens"[Organism] AND alive[prop]',
        "retmax": retmax,
        "retmode": "json",
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 200:
        return r.json().get("esearchresult", {}).get("idlist", [])
    return []

def ncbi_gene_summary(gene_ids):
    """NCBI Gene 요약 정보"""
    if not gene_ids:
        return []
    url = f"{NCBI_BASE}/esummary.fcgi"
    params = {
        "db": "gene",
        "id": ",".join(gene_ids[:100]),
        "retmode": "json",
    }
    r = requests.get(url, params=params, timeout=30)
    records = []
    if r.status_code == 200:
        result = r.json().get("result", {})
        for gid in gene_ids[:100]:
            if gid in result and isinstance(result[gid], dict):
                info = result[gid]
                records.append({
                    "Gene_ID": gid,
                    "Symbol": info.get("name", ""),
                    "Description": info.get("description", ""),
                    "Chromosome": info.get("chromosome", ""),
                })
    return records

def ncbi_chemical_gene_links(chemical_name):
    """NCBI에서 화학물질과 연관된 유전자 검색"""
    # PubChem compound -> Gene links via E-utilities
    # First find substance in PubChem
    gene_ids = ncbi_gene_search(f'"{chemical_name}" AND (receptor OR transporter OR enzyme OR target)')
    if gene_ids:
        return ncbi_gene_summary(gene_ids)
    return []

def main():
    os.makedirs("opentargets", exist_ok=True)
    os.makedirs("ncbi_gene", exist_ok=True)
    
    # 1. Open Targets: 신경/정신질환 관련 타겟 유전자
    print("=== Step 1: Open Targets Disease-Target Associations ===")
    all_disease_targets = []
    
    for disease_name, efo_id in NEURO_DISEASE_EFO.items():
        print(f"  {disease_name} ({efo_id}) 조회 중...")
        result = query_opentargets_disease_targets(efo_id)
        if result and "associatedTargets" in result:
            targets = result["associatedTargets"].get("rows", [])
            for t in targets:
                target = t.get("target", {})
                all_disease_targets.append({
                    "Disease": disease_name,
                    "Disease_EFO": efo_id,
                    "Gene_Ensembl": target.get("id", ""),
                    "Gene_Symbol": target.get("approvedSymbol", ""),
                    "Gene_Name": target.get("approvedName", ""),
                    "Association_Score": t.get("score", 0),
                })
            print(f"    타겟: {len(targets)}")
        else:
            print(f"    결과 없음")
        time.sleep(0.5)
    
    if all_disease_targets:
        dt_df = pd.DataFrame(all_disease_targets)
        dt_df.to_csv("opentargets/disease_target_associations.csv", index=False)
        print(f"  총 {len(dt_df)} disease-target associations")
    
    # 2. Open Targets: 약물별 작용 메커니즘/타겟
    print("\n=== Step 2: Open Targets Drug Targets ===")
    all_drug_targets = []
    all_drug_mechanisms = []
    
    for chem in CHEMICALS:
        print(f"  {chem} 검색 중...")
        hits = query_opentargets_drug_targets(chem)
        for hit in hits:
            obj = hit.get("object")
            if not obj:
                continue
            
            # Mechanisms of action
            moa = obj.get("mechanismsOfAction", {})
            if moa:
                for row in moa.get("rows", []):
                    for tgt in row.get("targets", []):
                        all_drug_mechanisms.append({
                            "Chemical": chem,
                            "Drug_ID": obj.get("id", ""),
                            "Drug_Name": obj.get("name", ""),
                            "Mechanism": row.get("mechanismOfAction", ""),
                            "Action_Type": row.get("actionType", ""),
                            "Target_Symbol": tgt.get("approvedSymbol", ""),
                            "Target_Name": tgt.get("approvedName", ""),
                            "Target_Ensembl": tgt.get("id", ""),
                        })
            
            # Linked targets
            linked = obj.get("linkedTargets", {})
            if linked:
                for tgt in linked.get("rows", []):
                    all_drug_targets.append({
                        "Chemical": chem,
                        "Drug_ID": obj.get("id", ""),
                        "Drug_Name": obj.get("name", ""),
                        "Target_Symbol": tgt.get("approvedSymbol", ""),
                        "Target_Name": tgt.get("approvedName", ""),
                        "Target_Ensembl": tgt.get("id", ""),
                    })
        
        print(f"    Hits: {len(hits)}")
        time.sleep(0.5)
    
    if all_drug_targets:
        pd.DataFrame(all_drug_targets).to_csv("opentargets/drug_targets.csv", index=False)
    if all_drug_mechanisms:
        pd.DataFrame(all_drug_mechanisms).to_csv("opentargets/drug_mechanisms.csv", index=False)
    
    print(f"  Drug targets: {len(all_drug_targets)}, Mechanisms: {len(all_drug_mechanisms)}")
    
    # 3. NCBI Gene: 화학물질-유전자 연관
    print("\n=== Step 3: NCBI Gene Chemical-Gene Links ===")
    all_chem_genes = []
    
    for chem in CHEMICALS:
        print(f"  {chem} 유전자 검색 중...")
        genes = ncbi_chemical_gene_links(chem)
        for g in genes:
            g["Chemical"] = chem
            all_chem_genes.append(g)
        print(f"    관련 유전자: {len(genes)}")
        time.sleep(0.5)
    
    if all_chem_genes:
        cg_df = pd.DataFrame(all_chem_genes)
        cg_df.to_csv("ncbi_gene/chemical_gene_associations.csv", index=False)
        print(f"  총 {len(cg_df)} chemical-gene associations")
    
    # 4. 교차 분석: 약물 타겟 + 질환 타겟 겹치는 유전자
    print("\n=== Step 4: Overlap Analysis ===")
    if all_drug_targets and all_disease_targets:
        drug_genes = set(r["Target_Symbol"] for r in all_drug_targets)
        disease_genes = set(r["Gene_Symbol"] for r in all_disease_targets)
        overlap = drug_genes & disease_genes
        
        overlap_records = []
        for gene in overlap:
            # 어떤 약물이 타겟하는지
            drugs = list(set(r["Chemical"] for r in all_drug_targets if r["Target_Symbol"] == gene))
            # 어떤 질환과 연관되는지
            diseases = list(set(r["Disease"] for r in all_disease_targets if r["Gene_Symbol"] == gene))
            overlap_records.append({
                "Gene_Symbol": gene,
                "Targeted_By_Drugs": "; ".join(drugs),
                "Associated_Diseases": "; ".join(diseases),
                "N_Drugs": len(drugs),
                "N_Diseases": len(diseases),
            })
        
        overlap_df = pd.DataFrame(overlap_records)
        overlap_df = overlap_df.sort_values("N_Drugs", ascending=False)
        overlap_df.to_csv("opentargets/drug_disease_gene_overlap.csv", index=False)
        print(f"  약물-질환 공통 유전자: {len(overlap)}")
    
    print("\n=== Open Targets / NCBI Gene 수집 완료 ===")
    for folder in ["opentargets", "ncbi_gene"]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                size = os.path.getsize(f"{folder}/{f}")
                print(f"  {folder}/{f}: {size:,} bytes")

if __name__ == "__main__":
    main()
