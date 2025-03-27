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