"""
전체 데이터 수집 마스터 스크립트
각 수집 스크립트를 순차 실행
"""
import subprocess
import sys
import os

SCRIPTS = [
    "01_pubchem_collect.py",
    "02_chembl_collect.py",
    "03_ctdbase_collect.py",
    "04_kegg_collect.py",
    "05_string_uniprot_collect.py",
    "06_disgenet_sider_collect.py",
    "07_pharmgkb_collect.py",
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    for script in SCRIPTS:
        print(f"\n{'='*60}")
        print(f"실행: {script}")
        print(f"{'='*60}")
        
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False,
            text=True,
        )
        
        if result.returncode != 0:
            print(f"  ⚠ {script} 실행 중 오류 (코드: {result.returncode})")
        else:
            print(f"  ✓ {script} 완료")
    
    print(f"\n{'='*60}")
    print("전체 데이터 수집 완료!")
    print(f"{'='*60}")
    
    # 수집된 파일 목록
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.endswith(".csv"):
                path = os.path.join(root, f)
                size = os.path.getsize(path)
                print(f"  {path}: {size:,} bytes")

if __name__ == "__main__":
    main()
