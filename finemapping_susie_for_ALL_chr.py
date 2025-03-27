import gwaslab as gl
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import gzip
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import rpy2.robjects.numpy2ri as numpy2ri
import rpy2.robjects.pandas2ri as pandas2ri


# Activate R-Python converters
numpy2ri.activate()
pandas2ri.activate()

def load_gwas_data(file_path):
    """Load GWAS data from a compressed TSV file."""
    with gzip.open(file_path, 'rt') as f:
        gwas_data_df = pd.read_csv(f, sep='\t')
    return gwas_data_df

def preprocess_gwas_data(gwas_data_df):
    """Preprocess GWAS data by splitting variant info and renaming columns."""
    # Split variant information
    gwas_data_df['CHR'] = gwas_data_df['variant'].str.split(':').str[0]
    gwas_data_df['POS'] = gwas_data_df['variant'].str.split(':').str[1]
    gwas_data_df['A2'] = gwas_data_df['variant'].str.split(':').str[2]
    gwas_data_df['A1'] = gwas_data_df['variant'].str.split(':').str[3]
    
    # Rename columns
    gwas_data_df = gwas_data_df.rename(columns={'variant': 'SNPID', 'pval': 'P'})
    
    return gwas_data_df


def filter_significant_snps(gwas_data_df, maf_threshold=0.05, p_threshold=5e-8):
    """Filter significant SNPs based on MAF and p-value thresholds."""
    # Apply filters
    minor_af_filtered_df = gwas_data_df[gwas_data_df['minor_AF'] > maf_threshold]
    significant_snp_df = minor_af_filtered_df[minor_af_filtered_df['P'] <= p_threshold]
    significant_snp_df = significant_snp_df[~significant_snp_df['SNPID'].str.startswith('X:')]
    
    return significant_snp_df


def prepare_cojo_file(significant_snp_df, output_path):
    """Prepare data for COJO analysis and save to file."""
    formatted_cojo_df = significant_snp_df.rename(columns={
        'SNPID': 'SNP',
        'A1': 'A1',
        'A2': 'A2',
        'minor_AF': 'freq',
        'beta': 'b',
        'se': 'se',
        'P': 'p',
        'n_complete_samples': 'N'
    })
    
    cojo_ready_df = formatted_cojo_df[['SNP', 'A1', 'A2', 'freq', 'b', 'se', 'p', 'N']]
    cojo_ready_df.to_csv(output_path, sep=" ", index=False)
    return cojo_ready_df


def extract_region_snps(significant_snp_df, variant_position, window_size=500000):
    """Extract SNPs within a window around a variant position."""
    start_pos = variant_position - window_size
    end_pos = variant_position + window_size
    region_snp_df = significant_snp_df[
        (significant_snp_df['POS'] >= start_pos) & 
        (significant_snp_df['POS'] <= end_pos)
    ]
    region_snp_df["log_pvalue"] = -np.log10(region_snp_df["P"])
    return region_snp_df

def run_susie_analysis(snp_df, ld_matrix, n=503, L=10):
    """Run SuSiE analysis on SNP data with LD matrix."""
    susieR = importr('susieR')
    ro.r('set.seed(123)')
    
    fit = susieR.susie_rss(
        bhat=snp_df["beta"].values.reshape(len(snp_df), 1),
        shat=snp_df["se"].values.reshape(len(snp_df), 1),
        R=ld_matrix,
        L=L,
        n=n
    )
    
    return fit
