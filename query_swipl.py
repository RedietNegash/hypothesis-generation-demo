<<<<<<< HEAD
import json
import pickle
from pengines.Builder import PengineBuilder
from pengines.Pengine import Pengine
from loguru import logger

class PrologQuery:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        logger.info(f"Connecting to Prolog server at {host}:{port}")
        self.pengine_builder = PengineBuilder(urlserver=f"http://{self.host}:{self.port}")
        # self.pengine = Pengine(builder=pengine_builder)
        # self.pengine.create()

    def get_candidate_genes(self, variant_id):
        """
        Given a SNP, get candidate genes that are proximal to it.
        """
        logger.info(f"Getting candidate genes for variant {variant_id}")
        query = f"candidate_genes(snp({variant_id}), Genes)"
        pengine = Pengine(builder=self.pengine_builder)
        pengine.doAsk(pengine.ask(query))
        result = pengine.currentQuery.availProofs[0]
        genes = [g.upper() for g in result["Genes"]]
        return genes
    
    def get_relevant_gene_proof(self, variant_id, gene):
        gene_id = self.get_gene_ids([gene])[0]
        query = f"json_proof_tree(relevant_gene(gene({gene_id}), snp({variant_id})), Graph)"
        print(f"Gene Proof Query: {query}")
        pengine = Pengine(builder=self.pengine_builder)
        pengine.doAsk(pengine.ask(query))
        if pengine.currentQuery is None:
            pengine = Pengine(builder=self.pengine_builder)
            pengine.doAsk(pengine.ask("meta_interpreter:rule_body(relevant_gene(G, S), R)")) #Get the body of the failed rule
            rule = pengine.currentQuery.availProofs[0]["R"]
            print(f"q rule: {rule}")
            return None, rule
        graph = pengine.currentQuery.availProofs[0]["Graph"]
        # pengine.doStop()
        return json.loads(graph), True
    
    def get_gene_ids(self, genes):
        genes = [g.lower() for g in genes]
        query = f"maplist(gene_id, {genes}, GeneIds)"
        pengine = Pengine(builder=self.pengine_builder)
        pengine.doAsk(pengine.ask(query))
        gene_ids = pengine.currentQuery.availProofs[0]["GeneIds"]
        # self.pengine.doStop()
        return gene_ids

    def execute_query(self, query):
        pengine = Pengine(builder=self.pengine_builder)
        pengine.doAsk(pengine.ask(query))
        return pengine.currentQuery.availProofs[0]["X"]

if __name__ == "__main__":
    prolog_query = PrologQuery(host="100.67.47.42", port=4242)
    result = prolog_query.execute_query("maplist(variant_id, [snp(rs1421085)], X)")
#     # result = prolog_query.get_candidate_genes("rs1421085")
    print(result)
=======
from swiplserver import PrologMQI, PrologThread
import json
import pickle

class PrologQuery:

    def __init__(self, mqi_port, mqi_pass):
        self.mqi_port = mqi_port
        self.mqi_pass = mqi_pass

    def get_relevant_gene(self, variant_id):
        """
        Given a SNP get the genes which are relevant to it either via eqtl association or proximity.
        """

        with PrologMQI(launch_mqi=False, port=self.mqi_port, password=self.mqi_pass) as mqi:
            with mqi.create_thread() as prolog_thread:
                # result = prolog_thread.query("json_proof(natnum(s(s(0))), PT).")
                var = "G"
                result = prolog_thread.query(f"relevant_gene({var}, sequence_variant({variant_id})).")
                if result:
                    genes = []
                    for r in result:
                        gene = r[var]["args"][0]
                        genes.append(gene)

                    genes = [g.upper() for g in genes]
                    return genes

    def get_go_proof(self, go_term, variant_id, sig_genes, pval):

        """
        Given a GO term, SNP and genes that are significantly enriched in the GO term
         get the proof tree explaining the causal association between the go_term and the variant.
        """
        sig_genes = [g.lower() for g in sig_genes]
        go_term = f"go_{go_term.split(':')[-1]}"
        with PrologMQI(launch_mqi=False, port=self.mqi_port, password=self.mqi_pass) as mqi:
            with mqi.create_thread() as prolog_thread:
                result = prolog_thread.query(f"json_proof(relevant_go({go_term}, {variant_id}, {sig_genes}, {pval}), PT)")
                return json.loads(result[0]["PT"])


if __name__ == "__main__":
    prolog_query = PrologQuery(4242, "pass123")
    result = prolog_query.get_go_proof("GO:0045598", "rs1421085",
                                       ["ensg00000172216", "ensg00000170323"], 0.001)
    print(result)
            
>>>>>>> f3dea18 (Initial implementation of hypothesis genearation backend)
