import openai
import json
from typing import Dict, List, Optional

class TissueMappingAgent:
    def __init__(self, api_key: str):
        """Initialize the OpenAI client for tissue mapping."""
        self.client = openai.OpenAI(api_key=api_key)
        
    def get_cellxgene_equivalent(self, tissue_data: Dict) -> Dict:
        """
        Use OpenAI to analyze tissue context and suggest CellxGene equivalents.
        
        Args:
            tissue_data: Dictionary containing GTEx tissue information
            
        Returns:
            Dictionary with suggested CellxGene mappings
        """
        
        gtex_name = tissue_data.get("gtex_tissue_name", "")
        uberon_id = tissue_data.get("gtex_uberon_id", "")
        ontology_name = tissue_data.get("gtex_ontology_name", "")
        match_type = tissue_data.get("match_type", "")
        notes = tissue_data.get("notes", "")
        

        prompt = f"""
You are an expert in biological tissue ontology and single-cell genomics databases. 

I need to find equivalent tissue names in the CellxGene Census database for the following GTEx tissue:

GTEx Tissue Information:
- Name: {gtex_name}
- UBERON ID: {uberon_id}
- Ontology Name: {ontology_name}
- Current Match Status: {match_type}
- Notes: {notes}

Please analyze this tissue information and suggest:

1. **Direct CellxGene Equivalent**: The most specific matching tissue name in CellxGene Census
2. **Broader Categories**: More general tissue categories that might contain this specific tissue
3. **Alternative Names**: Other common names or synonyms for this tissue type
4. **Anatomical Context**: Brief explanation of the anatomical location and function
5. **Mapping Confidence**: Your confidence level (High/Medium/Low) in the suggested mapping

For the specific example of "Brain_Spinal_cord_cervical_c-1" (C1 segment of cervical spinal cord), consider:
- CellxGene may use broader categories like "spinal cord" instead of specific segments
- Look for related terms like "central nervous system", "neural tissue", etc.
- Consider developmental or functional groupings

Please provide your response in JSON format with the following structure:
{{
    "suggested_cellxgene_name": "most likely equivalent name",
    "broader_categories": ["category1", "category2"],
    "alternative_names": ["alt1", "alt2"],
    "anatomical_context": "brief explanation",
    "mapping_confidence": "High/Medium/Low",
    "reasoning": "explanation of your mapping logic"
}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert biologist specializing in tissue ontology and genomics databases. Provide accurate, well-reasoned mappings between different tissue classification systems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1, 
                max_tokens=1000
            )
        
            response_text = response.choices[0].message.content
            
        
            try:
                mapping_result = json.loads(response_text)
            except json.JSONDecodeError:
                mapping_result = {
                    "suggested_cellxgene_name": "parsing_error",
                    "broader_categories": [],
                    "alternative_names": [],
                    "anatomical_context": response_text,
                    "mapping_confidence": "Low",
                    "reasoning": "Failed to parse JSON response"
                }
            
            return mapping_result
            
        except Exception as e:
            return {
                "error": str(e),
                "suggested_cellxgene_name": "error",
                "mapping_confidence": "Low"
            }
    
    def process_tissue_batch(self, tissue_dict: Dict) -> Dict:
        results = {}
        
        for tissue_key, tissue_info in tissue_dict.items():
            print(f"Processing: {tissue_key}")
            mapping = self.get_cellxgene_equivalent(tissue_info)
            
            results[tissue_key] = {
                **tissue_info, 
                "openai_suggestions": mapping
            }
            
        return results

def main():
    API_KEY = "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"
    mapper = TissueMappingAgent(API_KEY)
    
    sample_tissue = {
        "Brain_Spinal_cord_cervical_c-1": {
            "gtex_tissue_name": "Brain_Spinal_cord_cervical_c-1",
            "gtex_uberon_id": "UBERON:0006469",
            "gtex_ontology_name": "C1 segment of cervical spinal cord",
            "cellxgene_parent_uberon_id": None,
            "cellxgene_parent_ontology_name": None,
            "cellxgene_descendant_uberon_id": None,
            "cellxgene_descendant_ontology_name": None,
            "match_type": "no_cellxgene_match",
            "notes": "No suitable CellxGene Census tissue (direct or broader) found for GTEx UBERON ID 'UBERON:0006469'."
        }
    }
    results = mapper.process_tissue_batch(sample_tissue)
    print(json.dumps(results, indent=2))
    
    for tissue_key, tissue_data in results.items():
        suggestions = tissue_data.get("openai_suggestions", {})
        print(f"\n{tissue_key}:")
        print(f"  Suggested CellxGene name: {suggestions.get('suggested_cellxgene_name', 'N/A')}")
        print(f"  Confidence: {suggestions.get('mapping_confidence', 'N/A')}")
        print(f"  Broader categories: {suggestions.get('broader_categories', [])}")

if __name__ == "__main__":
    main()


def extract_suggested_names(results_dict: Dict) -> Dict[str, str]:
    """Extract just the suggested CellxGene names from the full results."""
    name_mapping = {}
    
    for tissue_key, tissue_data in results_dict.items():
        suggestions = tissue_data.get("openai_suggestions", {})
        suggested_name = suggestions.get("suggested_cellxgene_name", "no_suggestion")
        name_mapping[tissue_key] = suggested_name
    
    return name_mapping

def filter_by_confidence(results_dict: Dict, min_confidence: str = "Medium") -> Dict:
    """Filter results by confidence level."""
    confidence_order = {"Low": 0, "Medium": 1, "High": 2}
    min_level = confidence_order.get(min_confidence, 1)
    
    filtered = {}
    for tissue_key, tissue_data in results_dict.items():
        suggestions = tissue_data.get("openai_suggestions", {})
        confidence = suggestions.get("mapping_confidence", "Low")
        
        if confidence_order.get(confidence, 0) >= min_level:
            filtered[tissue_key] = tissue_data
    
    return filtered