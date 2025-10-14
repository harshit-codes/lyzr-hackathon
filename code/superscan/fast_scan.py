from typing import Any, Dict, List
import json

class FastScan:
    """
    Sparse, fast ontology proposal using a low-reasoning LLM (OpenAI).

    This class prepares a prompt from lightweight file metadata and sparse text
    snippets, calls the LLM, and parses a structured proposal
    with candidate nodes, edges, and attributes.
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize FastScan with LLM client.
        
        Args:
            api_key: OpenAI or DeepSeek API key
            base_url: Optional base URL (e.g., 'https://api.deepseek.com' for DeepSeek)
            model: Model name (default: 'gpt-3.5-turbo' for OpenAI, 'deepseek-chat' for DeepSeek)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model or ("deepseek-chat" if base_url and "deepseek" in base_url else "gpt-3.5-turbo")
        
        try:
            import openai
            if api_key:
                if base_url:
                    # DeepSeek or custom endpoint
                    self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
                else:
                    # Standard OpenAI
                    self.client = openai.OpenAI(api_key=api_key)
            else:
                self.client = None
        except ImportError:
            self.client = None

    def build_prompt(self, snippets: List[str], hints: Dict[str, Any] | None = None) -> str:
        domain = (hints or {}).get("domain", "")
        header = "You are a schema designer. Propose an ontology with NODE and EDGE types."
        hint_line = f"Domain: {domain}" if domain else ""
        joined = "\n\n".join(snippets[:10])  # limit for speed
        return f"""{header}
{hint_line}

Text Samples:
{joined}

Instructions:
- Identify entity types (NODEs) and relationship types (EDGEs)
- For each NODE, provide: schema_name, structured_attributes[] (name, data_type, required)
- For each EDGE, provide: schema_name, structured_attributes[] (name, data_type, required)
- Output valid JSON with keys: nodes[], edges[]
"""

    def parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response into structured proposal."""
        try:
            # Try JSON parsing first
            return json.loads(text)
        except Exception:
            # Fallback: try to extract JSON from markdown code block
            import re
            match = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            # Fallback to an empty proposal if parsing fails
            return {"nodes": [], "edges": [], "summary": "parse_error"}

    def generate_proposal(self, snippets: List[str], hints: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Generate ontology proposal from text snippets using LLM.
        
        Returns:
            Dict with keys: nodes[], edges[], summary
        """
        if not self.client:
            # Mock response if no OpenAI client
            return {
                "nodes": [
                    {
                        "schema_name": "Document",
                        "entity_type": "NODE",
                        "structured_attributes": [
                            {"name": "title", "data_type": "string", "required": True},
                            {"name": "author", "data_type": "string", "required": False},
                        ],
                        "notes": "Mock proposal (no OpenAI key)",
                    }
                ],
                "edges": [],
                "summary": "Mock proposal generated without OpenAI",
            }
        
        try:
            prompt = self.build_prompt(snippets, hints)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful ontology designer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=1500,
            )
            text = response.choices[0].message.content
            proposal = self.parse_response(text)
            proposal.setdefault("summary", f"Ontology proposal from {self.model}")
            return proposal
        except Exception as e:
            # Return error proposal
            return {
                "nodes": [],
                "edges": [],
                "summary": f"LLM error: {str(e)}",
            }
