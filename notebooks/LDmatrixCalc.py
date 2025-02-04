import os
import subprocess
import pandas as pd

# Configuration
CHROMOSOME = "16"
POPULATION = "EUR"
VCF_URL = f"ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr{CHROMOSOME}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
SAMPLE_PANEL_URL = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"
OUTPUT_DIR = "chr16_eur_dataset"
SNP_LIST_FILE = "filtered_snplist.txt" 


def run_command(cmd):
    """Execute shell command with error checking"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(result.stderr)
        exit(1)
    return result

def prepare_ld_matrix():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists("integrated_call_samples_v3.20130502.ALL.panel"):
        run_command(f"wget {SAMPLE_PANEL_URL}")

    panel = pd.read_csv("integrated_call_samples_v3.20130502.ALL.panel", sep="\t")
    eur_samples = panel[panel["super_pop"] == POPULATION]["sample"].tolist()

    with open(f"{OUTPUT_DIR}/eur_samples.txt", "w") as f:
     f.write("\n".join([f"{s}\t{s}" for s in eur_samples]))

    vcf_file = f"{OUTPUT_DIR}/ALL.chr{CHROMOSOME}.vcf.gz"
    if not os.path.exists(vcf_file):
        run_command(f"wget {VCF_URL} -O {vcf_file}")
    
    plink_prefix = f"{OUTPUT_DIR}/chr{CHROMOSOME}_eur"
    if not os.path.exists(f"{plink_prefix}.bed"):
      
        run_command(
            f"plink --vcf {vcf_file} "
            f"--keep {OUTPUT_DIR}/eur_samples.txt "
            f"--make-bed --out {plink_prefix} "
            f"--set-missing-var-ids @:#:\$1:\$2"
        )


    print(f"\nLD matrix saved to: {OUTPUT_DIR}/chr{CHROMOSOME}_ld_matrix.ld")
if __name__ == "__main__":
     prepare_ld_matrix()


    

