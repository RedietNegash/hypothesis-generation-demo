import pandas as pd
import gzip
import os

file_path = "../susie/gwas/21001_raw.gwas.imputed_v3.both_sexes.tsv.bgz"
with gzip.open(file_path, 'rt') as f:
    gwas_data_df = pd.read_csv(f, sep='\t') 

gwas_data_df = gwas_data_df[gwas_data_df['low_confidence_variant'] == False]
gwas_data_cleaned = gwas_data_df[['variant', 'beta', 'se', 'pval', 'minor_AF']]
gwas_data_cleaned[['chrom', 'pos', 'ref_allele', 'alt_allele']] = gwas_data_cleaned['variant'].str.split(':|:', expand=True)
gwas_data_cleaned['pos'] = gwas_data_cleaned['pos'].astype(int)
gwas_data_cleaned = gwas_data_cleaned[['chrom', 'pos', 'beta', 'se', 'pval']]
gwas_data_cleaned['SNP'] = gwas_data_cleaned['chrom'] + ':' + gwas_data_cleaned['pos'].astype(str)
gwas_data_cleaned = gwas_data_cleaned[['SNP', 'beta', 'se', 'pval']]

print(gwas_data_cleaned.head())

output_dir = "./"
output_file_path = os.path.join(output_dir, "cleaned_gwas_data_for_ldsc.txt")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gwas_data_cleaned.to_csv(output_file_path, sep='\t', index=False)
print(f"Cleaned GWAS data saved to {output_file_path}")
