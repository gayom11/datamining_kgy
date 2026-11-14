"""
Solar Pro4로 보고서 생성하는 스크립트
skill 폴더의 프롬프트와 data/experiment의 데이터를 읽어서
Solar Pro4 API에 전달하고, docx 보고서를 생성

사용법:
  python skill/generate_report.py --api-key YOUR_SOLAR_API_KEY

Solar Pro4 API: https://api.upstage.ai/v1/chat/completions
Model: solar-pro4
"""
import argparse
import requests
import json
import os
import sys
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

SOLAR_API_URL = "https://api.upstage.ai/v1/chat/completions"
MODEL = "solar-pro4"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_skill_files():
    """skill 폴더의 프롬프트 파일들 로드"""
    skill_dir = os.path.join(PROJECT_ROOT, "skill")
    skills = {}
    for fname in os.listdir(skill_dir):
        if fname.endswith(".md"):
            with open(os.path.join(skill_dir, fname), "r", encoding="utf-8") as f:
                skills[fname] = f.read()
    return skills

def load_data_summaries():
    """분석 결과 데이터 요약 로드"""
    summaries = {}
    
    # 교차 분석 결과
    exp_dir = os.path.join(PROJECT_ROOT, "experiment")
    for fname in ["shared_drug_targets.csv", "drug_disease_gene_overlap.csv", 
                   "drug_pathway_hits.csv", "ppi_hub_proteins.csv",
                   "database_summary.csv", "integrated_summary.json"]:
        fpath = os.path.join(exp_dir, fname)
        if os.path.exists(fpath):
            if fname.endswith(".json"):
                with open(fpath) as f:
                    summaries[fname] = json.load(f)
            else:
                df = pd.read_csv(fpath)
                summaries[fname] = df.to_string(index=False, max_rows=30)
    
    # 핵심 데이터 파일들
    data_dir = os.path.join(PROJECT_ROOT, "data")
    key_files = [
        "pubchem/compound_properties.csv",
        "pharmacogenomics/high_risk_combinations.csv",
        "pharmacogenomics/cyp_polymorphisms.csv",
        "pharmacogenomics/drug_cyp_interactions.csv",
        "sider_fda/neuro_adverse_events.csv",
    ]
    for rel_path in key_files:
        fpath = os.path.join(data_dir, rel_path)
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            summaries[rel_path] = df.to_string(index=False, max_rows=30)
    
    return summaries

def call_solar_pro4(api_key, system_prompt, user_prompt, max_tokens=4096):
    """Solar Pro4 API 호출"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,  # 보고서 일관성을 위해 낮은 temperature
    }
    
    r = requests.post(SOLAR_API_URL, headers=headers, json=payload, timeout=120)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        print(f"API Error: {r.status_code} - {r.text}")
        return None

def generate_report_sections(api_key, skills, data_summaries):
    """보고서 섹션별로 Solar Pro4에게 작성 요청"""
    system_prompt = skills.get("report_generation_prompt.md", "")
    style_guide = skills.get("writing_style_guide.md", "")
    data_dict = skills.get("data_dictionary.md", "")
    
    full_system = f"""You are a scientific report writer specializing in toxicology and pharmacogenomics.

{system_prompt}

{style_guide}

{data_dict}
"""

    sections = {}
    
    # 섹션별 생성
    section_prompts = {
        "executive_summary": f"""Write the Executive Summary section (about 250 words).
Key data:
{json.dumps(data_summaries.get('integrated_summary.json', {}), indent=2)}

High-risk combinations:
{data_summaries.get('pharmacogenomics/high_risk_combinations.csv', 'N/A')}
""",
        "introduction": f"""Write the Introduction section (about 500 words).
Include Table 1 (analyzed chemicals) and Table 2 (databases used).
Chemical properties:
{data_summaries.get('pubchem/compound_properties.csv', 'N/A')}

Database summary:
{data_summaries.get('database_summary.csv', 'N/A')}
""",
        "methods": f"""Write the Methods section (about 800 words).
Describe data collection from each database and cross-database integration methodology.
Reference the data dictionary for specific data types collected.
Database summary:
{data_summaries.get('database_summary.csv', 'N/A')}
""",
        "results": f"""Write the Results section (about 1500 words).
Reference Figures 1-10 and include key numerical findings.

Shared drug targets:
{data_summaries.get('shared_drug_targets.csv', 'N/A')}

Drug-disease gene overlap (top entries):
{data_summaries.get('drug_disease_gene_overlap.csv', 'N/A')}

PPI hub proteins:
{data_summaries.get('ppi_hub_proteins.csv', 'N/A')}

Neurological adverse events:
{data_summaries.get('sider_fda/neuro_adverse_events.csv', 'N/A')}

CYP interactions:
{data_summaries.get('pharmacogenomics/drug_cyp_interactions.csv', 'N/A')}

High risk combinations:
{data_summaries.get('pharmacogenomics/high_risk_combinations.csv', 'N/A')}
""",
        "discussion": f"""Write the Discussion section (about 1000 words).
Focus on:
1. MDMA-Methamphetamine CYP2D6 interaction
2. Cocaine-Opioid (Fentanyl) CYP3A4 interaction
3. Pharmacogenomic variability (CYP2D6 PM, CYP2C19 PM)
4. Network analysis insights (hub proteins)
5. Limitations

CYP polymorphisms:
{data_summaries.get('pharmacogenomics/cyp_polymorphisms.csv', 'N/A')}
""",
        "conclusion": f"""Write the Conclusion section (about 200 words).
Summarize the 4 HIGH risk combinations and emphasize pharmacogenomic variability.
High risk combinations:
{data_summaries.get('pharmacogenomics/high_risk_combinations.csv', 'N/A')}
""",
    }
    
    for section_name, prompt in section_prompts.items():
        print(f"  Generating: {section_name}...")
        text = call_solar_pro4(api_key, full_system, prompt)
        if text:
            sections[section_name] = text
            print(f"    Done ({len(text)} chars)")
        else:
            sections[section_name] = f"[Section generation failed: {section_name}]"
            print(f"    FAILED")
    
    return sections

def build_docx(sections, output_path):
    """DOCX 보고서 파일 생성"""
    doc = Document()
    
    # 스타일 설정
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    
    # 제목
    title = doc.add_heading(level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Synergistic Neurotoxicity Analysis of\nPsychoactive Substances and Narcotics:\nA Multi-Database Integrative Approach")
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0, 0, 0)
    
    doc.add_paragraph("")  # spacing
    
    # 섹션 순서
    section_order = [
        ("1. Executive Summary", "executive_summary"),
        ("2. Introduction", "introduction"),
        ("3. Methods", "methods"),
        ("4. Results", "results"),
        ("5. Discussion", "discussion"),
        ("6. Conclusion", "conclusion"),
    ]
    
    for heading_text, key in section_order:
        doc.add_heading(heading_text, level=1)
        
        text = sections.get(key, "[Not generated]")
        # 간단한 markdown -> docx 변환
        for para_text in text.split("\n\n"):
            para_text = para_text.strip()
            if not para_text:
                continue
            
            if para_text.startswith("### "):
                doc.add_heading(para_text[4:], level=3)
            elif para_text.startswith("## "):
                doc.add_heading(para_text[3:], level=2)
            elif para_text.startswith("# "):
                doc.add_heading(para_text[2:], level=1)
            else:
                p = doc.add_paragraph(para_text)
                p.paragraph_format.space_after = Pt(6)
    
    # Figure placeholders
    doc.add_heading("Figures", level=1)
    fig_dir = os.path.join(PROJECT_ROOT, "experiment", "figures")
    figure_captions = {
        "fig1_cyp_heatmap.png": "Figure 1. CYP Enzyme-Drug Metabolism Heatmap.",
        "fig2_shared_targets_heatmap.png": "Figure 2. Shared Protein Targets Between Drug Pairs.",
        "fig3_neuro_adverse_events.png": "Figure 3. Top Neurological Adverse Events per Drug.",
        "fig4_drug_disease_gene_overlap.png": "Figure 4. Drug Target ∩ Neurological Disease Gene Overlap.",
        "fig5_dangerous_combinations.png": "Figure 5. Predicted Dangerous Drug Combinations via CYP Inhibition.",
        "fig6_ppi_hub_proteins.png": "Figure 6. Top 20 Hub Proteins in PPI Network.",
        "fig7_pathway_enrichment.png": "Figure 7. Functional Enrichment of Drug Target Network.",
        "fig8_integration_diagram.png": "Figure 8. Multi-Database Integration Framework.",
        "fig9_adverse_event_summary.png": "Figure 9. FDA Adverse Event Analysis: Neurological Side Effects.",
        "fig10_high_risk_summary.png": "Figure 10. HIGH RISK Drug Combinations Summary.",
    }
    
    for fig_file, caption in figure_captions.items():
        fig_path = os.path.join(fig_dir, fig_file)
        if os.path.exists(fig_path):
            doc.add_picture(fig_path, width=Inches(5.5))
            last_paragraph = doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            cap_para = doc.add_paragraph(caption)
            cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_para.runs[0].font.size = Pt(9)
            cap_para.runs[0].font.italic = True
            doc.add_paragraph("")  # spacing
    
    # References
    doc.add_heading("7. References", level=1)
    refs = [
        "Kim S, et al. PubChem 2023 update. Nucleic Acids Research. 2023;51(D1):D1373-D1380.",
        "Zdrazil B, et al. The ChEMBL Database in 2023. Nucleic Acids Research. 2024;52(D1):D1180-D1192.",
        "Kanehisa M, et al. KEGG for taxonomy-based analysis of pathways and genomes. Nucleic Acids Research. 2023;51(D1):D587-D592.",
        "Szklarczyk D, et al. The STRING database in 2023. Nucleic Acids Research. 2023;51(D1):D483-D489.",
        "The UniProt Consortium. UniProt: the Universal Protein Knowledgebase in 2023. Nucleic Acids Research. 2023;51(D1):D523-D531.",
        "Ochoa D, et al. The next-generation Open Targets Platform. Nucleic Acids Research. 2023;51(D1):D1353-D1359.",
        "U.S. Food and Drug Administration. openFDA API. https://open.fda.gov/. Accessed November 2024.",
        "Flockhart DA. Drug Interactions: Cytochrome P450 Drug Interaction Table. Indiana University School of Medicine. https://drug-interactions.medicine.iu.edu/.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref, style='List Number')
        p.runs[0].font.size = Pt(9)
    
    doc.save(output_path)
    print(f"\nReport saved: {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")

def main():
    parser = argparse.ArgumentParser(description="Generate report using Solar Pro4")
    parser.add_argument("--api-key", required=True, help="Solar Pro4 API key")
    parser.add_argument("--output", default=None, help="Output docx path")
    args = parser.parse_args()
    
    if args.output is None:
        args.output = os.path.join(PROJECT_ROOT, "report", "neurotoxicity_report.docx")
    
    print("=== Report Generation with Solar Pro4 ===")
    
    # 1. Load skills
    print("\n[1/4] Loading skill files...")
    skills = load_skill_files()
    print(f"  Loaded {len(skills)} skill files")
    
    # 2. Load data
    print("\n[2/4] Loading data summaries...")
    data_summaries = load_data_summaries()
    print(f"  Loaded {len(data_summaries)} data files")
    
    # 3. Generate sections via Solar Pro4
    print("\n[3/4] Generating report sections via Solar Pro4...")
    sections = generate_report_sections(args.api_key, skills, data_summaries)
    
    # Save raw sections
    raw_path = os.path.join(PROJECT_ROOT, "report", "sections_raw.json")
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    
    # 4. Build DOCX
    print("\n[4/4] Building DOCX report...")
    build_docx(sections, args.output)
    
    print("\n=== Report generation complete ===")

if __name__ == "__main__":
    main()
