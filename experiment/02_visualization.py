"""
시각화 스크립트
- 보고서에 포함될 모든 그래프/차트 생성
- matplotlib 사용 (배점 기준)
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# 스타일 설정
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
})

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIG_DIR = "figures"

def setup():
    os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# Figure 1: CYP-Drug Metabolism Heatmap
# ============================================================
def fig1_cyp_heatmap():
    """약물-CYP 효소 대사 관계 히트맵"""
    df = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "cyp_drug_metabolism_matrix.csv"))
    
    # 숫자 매핑
    role_map = {"major": 3, "minor": 1, "none": 0}
    df["Score"] = df["Metabolism_Role"].map(role_map)
    
    pivot = df.pivot_table(index="Chemical", columns="CYP_Enzyme", values="Score", aggfunc="first")
    pivot = pivot.fillna(0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Custom colormap
    from matplotlib.colors import ListedColormap
    colors = ['#f0f0f0', '#fdd49e', '#d7301f']  # none, minor, major
    cmap = ListedColormap(colors)
    
    im = ax.imshow(pivot.values, cmap=cmap, aspect='auto', vmin=0, vmax=3)
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    
    # 텍스트 레이블 추가
    role_labels = {0: "—", 1: "Minor", 3: "Major"}
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = int(pivot.values[i, j])
            text_color = 'white' if val == 3 else 'black'
            ax.text(j, i, role_labels.get(val, ""), ha='center', va='center', 
                   fontsize=9, color=text_color, fontweight='bold' if val == 3 else 'normal')
    
    ax.set_title("Drug-CYP Enzyme Metabolism Relationships", fontsize=13, fontweight='bold')
    ax.set_xlabel("CYP Enzyme")
    ax.set_ylabel("Drug/Substance")
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#f0f0f0', edgecolor='gray', label='None'),
        Patch(facecolor='#fdd49e', edgecolor='gray', label='Minor substrate'),
        Patch(facecolor='#d7301f', edgecolor='gray', label='Major substrate'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.35, 1))
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig1_cyp_heatmap.png", bbox_inches='tight')
    plt.close()
    print("  Fig 1: CYP-Drug Heatmap saved")

# ============================================================
# Figure 2: Shared Drug Targets Heatmap
# ============================================================
def fig2_shared_targets():
    """약물 쌍별 공유 타겟 히트맵"""
    df = pd.read_csv("shared_drug_targets.csv")
    
    chemicals = sorted(set(df["Drug_1"].unique()) | set(df["Drug_2"].unique()))
    n = len(chemicals)
    matrix = np.zeros((n, n))
    
    chem_idx = {c: i for i, c in enumerate(chemicals)}
    for _, row in df.iterrows():
        i = chem_idx[row["Drug_1"]]
        j = chem_idx[row["Drug_2"]]
        matrix[i][j] = row["Shared_Target_Count"]
        matrix[j][i] = row["Shared_Target_Count"]
    
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(n))
    ax.set_xticklabels(chemicals, rotation=45, ha='right')
    ax.set_yticks(range(n))
    ax.set_yticklabels(chemicals)
    
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                ax.text(j, i, f"{int(matrix[i][j])}", ha='center', va='center', fontsize=9)
    
    plt.colorbar(im, label="Number of Shared Targets")
    ax.set_title("Shared Protein Targets Between Drug Pairs\n(ChEMBL Bioactivity Data)", 
                fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig2_shared_targets_heatmap.png", bbox_inches='tight')
    plt.close()
    print("  Fig 2: Shared Targets Heatmap saved")

# ============================================================
# Figure 3: Neurological Adverse Events Comparison
# ============================================================
def fig3_neuro_adverse():
    """약물별 신경계 부작용 비교"""
    df = pd.read_csv(os.path.join(DATA_DIR, "sider_fda", "neuro_adverse_events.csv"))
    
    # 약물별 상위 부작용
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    chemicals = df["Chemical"].unique()
    
    for idx, chem in enumerate(chemicals):
        ax = axes[idx // 4][idx % 4]
        chem_data = df[df["Chemical"] == chem].nlargest(8, "Count")
        
        if not chem_data.empty:
            bars = ax.barh(range(len(chem_data)), chem_data["Count"].values, color='#e74c3c', alpha=0.8)
            ax.set_yticks(range(len(chem_data)))
            ax.set_yticklabels([ae[:25] for ae in chem_data["Adverse_Event"].values], fontsize=7)
            ax.invert_yaxis()
        
        ax.set_title(chem, fontsize=10, fontweight='bold')
        ax.set_xlabel("FDA Reports", fontsize=8)
    
    plt.suptitle("Top Neurological Adverse Events per Drug (FDA FAERS Data)", 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig3_neuro_adverse_events.png", bbox_inches='tight')
    plt.close()
    print("  Fig 3: Neurological Adverse Events saved")

# ============================================================
# Figure 4: Drug-Disease Gene Overlap
# ============================================================
def fig4_drug_disease_overlap():
    """약물 타겟과 신경질환 유전자 교차"""
    if not os.path.exists("drug_disease_gene_overlap.csv"):
        print("  Fig 4: Skipped (no overlap data)")
        return
    
    df = pd.read_csv("drug_disease_gene_overlap.csv")
    
    # Pivot for heatmap
    pivot = df.pivot_table(
        index="Chemical", columns="Disease", values="Overlap_Count",
        aggfunc="sum"
    ).fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    im = ax.imshow(pivot.values, cmap='Blues', aspect='auto')
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=60, ha='right', fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = int(pivot.values[i, j])
            if val > 0:
                ax.text(j, i, str(val), ha='center', va='center', fontsize=7)
    
    plt.colorbar(im, label="Overlapping Genes")
    ax.set_title("Drug Target ∩ Neurological Disease Gene Overlap", fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig4_drug_disease_gene_overlap.png", bbox_inches='tight')
    plt.close()
    print("  Fig 4: Drug-Disease Gene Overlap saved")

# ============================================================
# Figure 5: Dangerous Drug Combinations
# ============================================================
def fig5_dangerous_combos():
    """위험한 약물 조합 시각화"""
    df = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "dangerous_combinations.csv"))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Risk level color
    colors = {"HIGH": "#d7301f", "MODERATE": "#fc8d59"}
    bar_colors = [colors.get(r, "#fee090") for r in df["Risk_Level"]]
    
    labels = [f"{row['Inhibitor_Drug']} → {row['Affected_Drug']}\n(via {row['CYP_Enzyme']})" 
              for _, row in df.iterrows()]
    
    # Sort by risk
    df_sorted = df.copy()
    df_sorted["risk_num"] = df_sorted["Risk_Level"].map({"HIGH": 2, "MODERATE": 1})
    df_sorted = df_sorted.sort_values("risk_num", ascending=False)
    
    y_pos = range(len(df_sorted))
    colors_sorted = [colors.get(r, "#fee090") for r in df_sorted["Risk_Level"]]
    labels_sorted = [f"{row['Inhibitor_Drug']} → {row['Affected_Drug']} (via {row['CYP_Enzyme']})" 
                    for _, row in df_sorted.iterrows()]
    
    ax.barh(y_pos, df_sorted["risk_num"].values, color=colors_sorted, edgecolor='gray', alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels_sorted, fontsize=8)
    ax.set_xlabel("Risk Level")
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["MODERATE", "HIGH"])
    ax.invert_yaxis()
    
    ax.set_title("Predicted Dangerous Drug Combinations via CYP Inhibition", 
                fontsize=13, fontweight='bold')
    
    # Annotation for HIGH risk
    high_risk = df_sorted[df_sorted["Risk_Level"] == "HIGH"]
    for i, (_, row) in enumerate(high_risk.iterrows()):
        ax.annotate("⚠ HIGH RISK", xy=(2, i), fontsize=8, color='darkred', fontweight='bold',
                    xytext=(2.1, i), va='center')
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig5_dangerous_combinations.png", bbox_inches='tight')
    plt.close()
    print("  Fig 5: Dangerous Combinations saved")

# ============================================================
# Figure 6: PPI Network Hub Analysis
# ============================================================
def fig6_ppi_hubs():
    """PPI 네트워크 허브 단백질"""
    df = pd.read_csv("ppi_hub_proteins.csv")
    
    top20 = df.head(20)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(range(len(top20)), top20["Degree"].values, 
                   color='#3498db', alpha=0.85, edgecolor='gray')
    ax.set_yticks(range(len(top20)))
    ax.set_yticklabels(top20["Protein"].values, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Interaction Degree (Number of PPI Partners)")
    ax.set_title("Top 20 Hub Proteins in Neurotransmitter/Drug Target PPI Network\n(STRING Database, score > 400)",
                fontsize=12, fontweight='bold')
    
    # 값 표시
    for i, v in enumerate(top20["Degree"].values):
        ax.text(v + 0.5, i, str(int(v)), va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig6_ppi_hub_proteins.png", bbox_inches='tight')
    plt.close()
    print("  Fig 6: PPI Hub Proteins saved")

# ============================================================
# Figure 7: Pathway Enrichment
# ============================================================
def fig7_pathway_enrichment():
    """약물 타겟 pathway 분포"""
    df = pd.read_csv(os.path.join(DATA_DIR, "string", "functional_enrichment.csv"))
    
    # KEGG pathways only, top 20 by FDR
    kegg = df[df["Category"] == "KEGG"].copy()
    if kegg.empty:
        # Try Process (GO Biological Process)
        kegg = df[df["Category"].str.contains("Process", na=False)].copy()
    
    if kegg.empty:
        kegg = df.head(20).copy()
    
    kegg = kegg.nsmallest(20, "FDR")
    kegg["-log10(FDR)"] = -np.log10(kegg["FDR"].clip(lower=1e-300))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    scatter = ax.scatter(
        kegg["Count"], kegg["-log10(FDR)"],
        s=kegg["Count"] * 20,
        c=kegg["Strength"],
        cmap="RdYlBu_r",
        alpha=0.7,
        edgecolors='gray',
    )
    
    # 레이블
    for _, row in kegg.iterrows():
        desc = row["Description"][:40]
        ax.annotate(desc, (row["Count"], row["-log10(FDR)"]),
                   fontsize=6, alpha=0.8,
                   xytext=(5, 5), textcoords='offset points')
    
    plt.colorbar(scatter, label="Enrichment Strength")
    ax.set_xlabel("Number of Genes")
    ax.set_ylabel("-log10(FDR)")
    ax.set_title("Functional Enrichment of Drug Target Network\n(STRING Enrichment Analysis)",
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig7_pathway_enrichment.png", bbox_inches='tight')
    plt.close()
    print("  Fig 7: Pathway Enrichment saved")

# ============================================================
# Figure 8: Database Integration Network Diagram
# ============================================================
def fig8_integration_diagram():
    """데이터베이스 간 연결 관계 다이어그램"""
    import networkx as nx
    
    G = nx.Graph()
    
    # 노드: 데이터베이스
    dbs = {
        "PubChem": {"type": "db", "color": "#3498db"},
        "ChEMBL": {"type": "db", "color": "#2ecc71"},
        "KEGG": {"type": "db", "color": "#e74c3c"},
        "STRING": {"type": "db", "color": "#9b59b6"},
        "UniProt": {"type": "db", "color": "#f39c12"},
        "OpenTargets": {"type": "db", "color": "#1abc9c"},
        "NCBI Gene": {"type": "db", "color": "#e67e22"},
        "OpenFDA": {"type": "db", "color": "#95a5a6"},
        "CYP-Drug\nMatrix": {"type": "db", "color": "#d35400"},
    }
    
    # 중간 엔티티
    entities = {
        "Chemicals": "#2c3e50",
        "Gene/Protein\nTargets": "#2c3e50",
        "Pathways": "#2c3e50",
        "Diseases": "#2c3e50",
        "Adverse\nEvents": "#2c3e50",
        "Drug\nMetabolism": "#2c3e50",
    }
    
    for db in dbs:
        G.add_node(db, node_type="db")
    for ent in entities:
        G.add_node(ent, node_type="entity")
    
    # 엣지
    edges = [
        ("PubChem", "Chemicals"), ("PubChem", "Gene/Protein\nTargets"),
        ("ChEMBL", "Chemicals"), ("ChEMBL", "Gene/Protein\nTargets"),
        ("KEGG", "Pathways"), ("KEGG", "Gene/Protein\nTargets"), ("KEGG", "Drug\nMetabolism"),
        ("STRING", "Gene/Protein\nTargets"),
        ("UniProt", "Gene/Protein\nTargets"),
        ("OpenTargets", "Gene/Protein\nTargets"), ("OpenTargets", "Diseases"),
        ("NCBI Gene", "Gene/Protein\nTargets"), ("NCBI Gene", "Diseases"),
        ("OpenFDA", "Adverse\nEvents"), ("OpenFDA", "Chemicals"),
        ("CYP-Drug\nMatrix", "Drug\nMetabolism"), ("CYP-Drug\nMatrix", "Chemicals"),
    ]
    G.add_edges_from(edges)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    pos = nx.spring_layout(G, seed=42, k=2.5)
    
    # Draw databases
    db_nodes = [n for n in G.nodes if n in dbs]
    entity_nodes = [n for n in G.nodes if n in entities]
    
    nx.draw_networkx_nodes(G, pos, nodelist=db_nodes,
                          node_color=[dbs[n]["color"] for n in db_nodes],
                          node_size=2000, alpha=0.9, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=entity_nodes,
                          node_color='#ecf0f1', node_size=1500, 
                          edgecolors='#2c3e50', linewidths=2, alpha=0.9, ax=ax)
    
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=1.5, 
                          edge_color='#7f8c8d', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
    
    ax.set_title("Multi-Database Integration Framework\nfor Neurotoxicity Analysis",
                fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#3498db', label='Database Source'),
        Patch(facecolor='#ecf0f1', edgecolor='#2c3e50', label='Data Entity'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig8_integration_diagram.png", bbox_inches='tight')
    plt.close()
    print("  Fig 8: Integration Diagram saved")

# ============================================================
# Figure 9: Adverse Event Count Comparison (bar chart)
# ============================================================
def fig9_adverse_summary():
    """약물별 전체 vs 신경계 부작용 비교"""
    all_ae = pd.read_csv(os.path.join(DATA_DIR, "sider_fda", "adverse_events.csv"))
    neuro_ae = pd.read_csv(os.path.join(DATA_DIR, "sider_fda", "neuro_adverse_events.csv"))
    
    # 약물별 합산
    all_sum = all_ae.groupby("Chemical")["Count"].sum().reset_index()
    all_sum.columns = ["Chemical", "Total_AE_Reports"]
    
    neuro_sum = neuro_ae.groupby("Chemical")["Count"].sum().reset_index()
    neuro_sum.columns = ["Chemical", "Neuro_AE_Reports"]
    
    merged = all_sum.merge(neuro_sum, on="Chemical", how="left").fillna(0)
    merged["Neuro_Ratio"] = merged["Neuro_AE_Reports"] / merged["Total_AE_Reports"]
    merged = merged.sort_values("Neuro_Ratio", ascending=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Total vs Neuro counts
    x = range(len(merged))
    w = 0.35
    ax1.barh([i - w/2 for i in x], merged["Total_AE_Reports"], w, label="Total AE Reports", color="#3498db", alpha=0.8)
    ax1.barh([i + w/2 for i in x], merged["Neuro_AE_Reports"], w, label="Neurological AE Reports", color="#e74c3c", alpha=0.8)
    ax1.set_yticks(x)
    ax1.set_yticklabels(merged["Chemical"])
    ax1.set_xlabel("FDA FAERS Report Count")
    ax1.set_title("Total vs Neurological\nAdverse Event Reports", fontweight='bold')
    ax1.legend(fontsize=8)
    
    # Right: Neuro ratio
    ax2.barh(x, merged["Neuro_Ratio"] * 100, color="#e74c3c", alpha=0.8)
    ax2.set_yticks(x)
    ax2.set_yticklabels(merged["Chemical"])
    ax2.set_xlabel("Neurological AE Ratio (%)")
    ax2.set_title("Proportion of Neurological\nAdverse Events", fontweight='bold')
    
    for i, v in enumerate(merged["Neuro_Ratio"] * 100):
        ax2.text(v + 0.3, i, f"{v:.1f}%", va='center', fontsize=8)
    
    plt.suptitle("FDA Adverse Event Analysis: Neurological Side Effects", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig9_adverse_event_summary.png", bbox_inches='tight')
    plt.close()
    print("  Fig 9: Adverse Event Summary saved")

# ============================================================
# Figure 10: Synergistic Toxicity Risk Summary
# ============================================================
def fig10_risk_summary():
    """최종 위험도 요약 다이어그램"""
    high_risk = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "high_risk_combinations.csv"))
    all_combos = pd.read_csv(os.path.join(DATA_DIR, "pharmacogenomics", "dangerous_combinations.csv"))
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # HIGH risk 조합 강조 테이블 형태
    table_data = []
    for _, row in high_risk.iterrows():
        table_data.append([
            row["Inhibitor_Drug"],
            row["Affected_Drug"],
            row["CYP_Enzyme"],
            row["Inhibition_Strength"],
            "Increased plasma level\n→ Enhanced toxicity"
        ])
    
    col_labels = ["Perpetrator\n(CYP Inhibitor)", "Victim\n(Substrate)", "CYP Enzyme",
                 "Inhibition\nStrength", "Expected\nOutcome"]
    
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Header styling
    for j in range(len(col_labels)):
        table[0, j].set_facecolor('#d7301f')
        table[0, j].set_text_props(color='white', fontweight='bold')
    
    # Row coloring
    for i in range(len(table_data)):
        for j in range(len(col_labels)):
            table[i+1, j].set_facecolor('#fee0d2')
    
    ax.axis('off')
    ax.set_title("HIGH RISK Drug Combinations: CYP-Mediated Pharmacokinetic Interactions\n"
                "Potential for Synergistic Neurotoxicity",
                fontsize=13, fontweight='bold', color='darkred')
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig10_high_risk_summary.png", bbox_inches='tight')
    plt.close()
    print("  Fig 10: Risk Summary saved")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setup()
    
    print("=== 시각화 생성 시작 ===\n")
    
    fig1_cyp_heatmap()
    fig2_shared_targets()
    fig3_neuro_adverse()
    fig4_drug_disease_overlap()
    fig5_dangerous_combos()
    fig6_ppi_hubs()
    fig7_pathway_enrichment()
    fig8_integration_diagram()
    fig9_adverse_summary()
    fig10_risk_summary()
    
    print(f"\n=== 시각화 완료: {FIG_DIR}/ ===")
    for f in sorted(os.listdir(FIG_DIR)):
        size = os.path.getsize(f"{FIG_DIR}/{f}")
        print(f"  {f}: {size:,} bytes")

if __name__ == "__main__":
    main()
