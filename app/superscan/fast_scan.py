"""
This module provides the `FastScan` class, which is responsible for generating
an ontology proposal from a document using a large language model (LLM).
"""

from typing import Any, Dict, List
import json

class FastScan:
    """
    A class for generating a fast, sparse ontology proposal using an LLM.

    The `FastScan` class takes text snippets from a document, prepares a prompt
    for an LLM, and then parses the LLM's response to create a structured
    proposal for the knowledge graph's ontology. This proposal includes
    candidate nodes, edges, and their attributes.
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initializes the `FastScan` class with an LLM client.

        Args:
            api_key: The API key for the LLM service (e.g., OpenAI or
                DeepSeek).
            base_url: The base URL for the LLM service. This is optional and
                is used for custom endpoints like DeepSeek.
            model: The name of the model to use. Defaults to 'gpt-3.5-turbo'
                for OpenAI or 'deepseek-chat' for DeepSeek.
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
        """
        Builds a prompt for the LLM to generate an ontology proposal.

        Args:
            snippets: A list of text snippets from the document.
            hints: A dictionary of hints to guide the LLM, such as the
                document's domain.

        Returns:
            A string containing the prompt for the LLM.
        """
        domain = (hints or {}).get("domain", "")
        header = "You are a schema designer. Propose an ontology with NODE and EDGE types."
        hint_line = f"Domain: {domain}" if domain else ""
        joined = "\n\n".join(snippets[:10])  # limit for speed
        return f"""
{header}
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
        """
        Parses the LLM's response into a structured proposal.

        This method first tries to parse the response as a JSON object. If that
        fails, it tries to extract a JSON object from a markdown code block.

        Args:
            text: The LLM's response as a string.

        Returns:
            A dictionary containing the parsed proposal.
        """
        try:
            # Try JSON parsing first
            return json.loads(text)
        except Exception:
            # Fallback: try to extract JSON from markdown code block
            import re
            match = re.search(r'```(?:json)?\s*({{.*?}})\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            # Fallback to an empty proposal if parsing fails
            return {"nodes": [], "edges": [], "summary": "parse_error"}

    def _try_huggingface_fallback(self, snippets: List[str], hints: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Fallback to HuggingFace Inference API when DeepSeek fails.

        Args:
            snippets: A list of text snippets from the document.
            hints: A dictionary of hints to guide the LLM.

        Returns:
            A dictionary containing the ontology proposal from HuggingFace.
        """
        import os
        hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

        if not hf_token:
            print("⚠️ No HuggingFace token found, using default schema")
            return self._get_default_schema()

        try:
            import requests
            print("🔄 Trying HuggingFace Inference API fallback...")

            # Use Mistral-7B-Instruct for schema generation
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {hf_token}"}

            prompt = self.build_prompt(snippets, hints)
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1500,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    proposal = self.parse_response(text)

                    # If parsing succeeded and we got schemas
                    if proposal.get("nodes") or proposal.get("edges"):
                        proposal["summary"] = "Ontology proposal from HuggingFace Mistral-7B"
                        print(f"✅ HuggingFace generated {len(proposal.get('nodes', []))} node schemas")
                        return proposal

            print(f"⚠️ HuggingFace API returned status {response.status_code}")

        except Exception as e:
            print(f"⚠️ HuggingFace fallback failed: {e}")

        # If HuggingFace also fails, return default schema
        return self._get_default_schema()

    def _get_default_schema(self) -> Dict[str, Any]:
        """
        Returns a default schema proposal when all LLM attempts fail.

        Returns:
            A dictionary containing a basic default schema.
        """
        print("📋 Using default schema (Person, Organization, Location)")
        return {
            "nodes": [
                {
                    "schema_name": "Person",
                    "entity_type": "NODE",
                    "structured_attributes": [
                        {"name": "name", "data_type": "string", "required": True},
                        {"name": "title", "data_type": "string", "required": False},
                        {"name": "email", "data_type": "string", "required": False},
                    ],
                    "notes": "Default Person schema",
                },
                {
                    "schema_name": "Organization",
                    "entity_type": "NODE",
                    "structured_attributes": [
                        {"name": "name", "data_type": "string", "required": True},
                        {"name": "industry", "data_type": "string", "required": False},
                    ],
                    "notes": "Default Organization schema",
                },
                {
                    "schema_name": "Location",
                    "entity_type": "NODE",
                    "structured_attributes": [
                        {"name": "name", "data_type": "string", "required": True},
                        {"name": "country", "data_type": "string", "required": False},
                    ],
                    "notes": "Default Location schema",
                }
            ],
            "edges": [
                {
                    "schema_name": "WORKS_AT",
                    "entity_type": "EDGE",
                    "structured_attributes": [
                        {"name": "start_date", "data_type": "string", "required": False},
                        {"name": "position", "data_type": "string", "required": False},
                    ],
                    "notes": "Person works at Organization",
                }
            ],
            "summary": "Default schema proposal (LLM unavailable)",
        }

    def generate_proposal(self, snippets: List[str], hints: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Generates an ontology proposal from text snippets using an LLM.

        Tries DeepSeek first, falls back to HuggingFace if DeepSeek fails,
        and uses a default schema if both fail.

        Args:
            snippets: A list of text snippets from the document.
            hints: A dictionary of hints to guide the LLM.

        Returns:
            A dictionary containing the ontology proposal, with keys for
            'nodes', 'edges', and 'summary'.
        """
        if not self.client:
            print("⚠️ No DeepSeek client configured, trying HuggingFace...")
            return self._try_huggingface_fallback(snippets, hints)

        # Try DeepSeek first
        try:
            print(f"🤖 Trying DeepSeek API ({self.model})...")
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

            # Check if DeepSeek returned valid schemas
            if proposal.get("nodes") or proposal.get("edges"):
                proposal.setdefault("summary", f"Ontology proposal from {self.model}")
                print(f"✅ DeepSeek generated {len(proposal.get('nodes', []))} node schemas")
                return proposal
            else:
                print("⚠️ DeepSeek returned empty proposal, trying HuggingFace...")
                return self._try_huggingface_fallback(snippets, hints)

        except Exception as e:
            print(f"⚠️ DeepSeek API failed: {e}")
            print("🔄 Falling back to HuggingFace...")
            return self._try_huggingface_fallback(snippets, hints)