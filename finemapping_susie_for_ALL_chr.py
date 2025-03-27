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