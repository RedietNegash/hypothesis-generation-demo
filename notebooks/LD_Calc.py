import os
import subprocess
import pandas as pd
from cyvcf2 import VCF, Writer

CHROMOSOME = "16"
POPULATION = "EUR"
VCF_URL = f"ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr{CHROMOSOME}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
SAMPLE_PANEL_URL = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"
OUTPUT_DIR = "../data/plot_chr16_eur"
SNP_LIST_FILE = "../data/snplist/sig_locus.snplist.txt"

def run_command(cmd):
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
    
    vcf = VCF(vcf_file)
    output_vcf_file = f"{OUTPUT_DIR}/ALL.chr{CHROMOSOME}.updated.vcf.gz"
    writer = Writer(output_vcf_file, vcf)

    for variant in vcf:
        chrom = variant.CHROM
        pos = variant.POS
        ref=variant.REF
        alt=variant.ALT[0]
        variant.ID =  f"{chrom}:{pos}:{ref}:{alt}"
        writer.write_record(variant)

    writer.close()

    output_vcf_file='../data/plot_chr16_eur/ALL.chr16.updated.vcf.gz'
    
    plink_prefix = f"{OUTPUT_DIR}/chr{CHROMOSOME}_eur"
    if not os.path.exists(f"{plink_prefix}.bed"):
        run_command(
            f"plink --vcf {output_vcf_file} "
            f"--keep {OUTPUT_DIR}/eur_samples.txt "
            f"--make-bed --out {plink_prefix} "
            # f"--set-missing-var-ids @:#:\$1:\$2"
        )
       
    # filtered_prefix = f"{OUTPUT_DIR}/chr{CHROMOSOME}_eur_filtered"
    # run_command(
    #     f"plink --bfile {plink_prefix} "
    #     f"--extract {SNP_LIST_FILE} "
    #     f"--make-bed --out {filtered_prefix}"
    # )
    # run_command(
    # f"plink --bfile {plink_prefix} "
    # f"--keep-allele-order "
    # f"--r square "
    # f"--extract {SNP_LIST_FILE} "
    # f"--out ../data/ld/sig_locus_mt"
    # )

    # run_command(
    # f"plink --bfile {plink_prefix} "
    # f"--keep-allele-order "
    # f"--r2 square "
    # f"--extract {SNP_LIST_FILE} "
    # f"--out ../data/ld/sig_locus_mt_r2"
    # )

    #Load LD data
  
    # run_command(
    #     !plink \
    #     --bfile "../data/chr16_eur" \
    #     --keep-allele-order \
    #     --r square \
    #     --extract ../data/sig_locus.snplist \
    #     --out ../data/sig_locus_mt

    #     !plink \
    #     --bfile "../data/chr16_eur" \
    #     --keep-allele-order \
    #     --r2 square \
    #     --extract ../data/sig_locus.snplist \
    #     --out ../data/sig_locus_mt_r2
    # )
    
    
    # run_command(
    #     f"plink --bfile {filtered_prefix} "
    #     "--r2 square "
    #     f"--out {OUTPUT_DIR}/chr{CHROMOSOME}_ld_matrix"
    # )

    # print(f"\nLD matrix saved to: {OUTPUT_DIR}/chr{CHROMOSOME}_ld_matrix.ld")

if __name__ == "__main__":
    prepare_ld_matrix()
