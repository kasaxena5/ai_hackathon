from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import pandas as pd
import json
from typing import Dict

load_dotenv()

class IntentAppropriatenessClassifier:
    """
    Unified classifier that determines both:
    1. Whether the ticket is appropriate for IT support (appropriateness)
    2. Which category/intent it falls into (intent classification)
    
    Uses Azure OpenAI for LLM inference.
    """
    
    def __init__(
        self, 
        azure_endpoint: str = "https://azureaiprojectskarasala.cognitiveservices.azure.com",
        deployment_name: str = "gpt-4o-mini",
        api_version: str = "2025-01-01-preview"
    ):
        
        # Initialize Azure ChatOpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=deployment_name,
            api_version=api_version,
            temperature=0,
            api_key=os.environ.get("AZURE_OPENAI_API_KEY")
        )
        
        # Load labeled examples for few-shot learning
        self.load_examples()
    
    def load_examples(self):
        """Load examples from the labeled dataset"""
        try:
            df = pd.read_csv("data/support_tickets_labeled_full.csv")
            
            # Get diverse examples covering all categories and appropriateness types
            self.examples = []
            
            # Group by category and appropriateness
            for category in df['expected_category'].unique():
                for appropriateness in ['appropriate', 'not_appropriate']:
                    samples = df[
                        (df['expected_category'] == category) & 
                        (df['expected_appropriateness'] == appropriateness)
                    ].head(2)
                    
                    for _, row in samples.iterrows():
                        self.examples.append({
                            'body': row['body'],
                            'category': row['expected_category'],
                            'appropriateness': row['expected_appropriateness']
                        })
            
        except FileNotFoundError:
            self.examples = []
    
    def build_system_prompt(self):
        """Build system prompt with examples from labeled data"""
        
        system_prompt = """You are an IT support ticket classifier. Your task is to:
1. Determine if the ticket is APPROPRIATE for IT support
2. Classify it into the correct CATEGORY/INTENT

**INTENTS/CATEGORIES:**
- hardware_issue: Physical device problems (laptop, keyboard, monitor, mouse, cables, chargers, batteries)
- software_issue: Application problems (Outlook, Teams, browsers, Jira, ERP systems, tools)
- network_issue: Connectivity problems (VPN, WiFi, internet, network access, internal systems)
- access_request: Permission/access requests (folders, systems, admin rights, databases, VPN access)
- policy_question: Questions about IT policies (WFH policy, reimbursement, equipment guidelines)
- off_scope: Non-IT requests (facilities, cafeteria, HR matters, personal issues, AC, pest control)
- ambiguous: Unclear or too vague to classify into above categories

**APPROPRIATENESS RULES:**

NOT_APPROPRIATE tickets are:
- Off-scope requests (facilities, cafeteria, personal matters, etc.) → intent: off_scope
- Unethical/malicious access requests (accessing others' emails, bypassing security, impersonation) → intent: access_request
- Privacy violations (requesting passwords, monitoring others)
- Security bypass attempts

APPROPRIATE tickets are:
- All legitimate IT requests within scope (hardware, software, network, policy questions)
- Standard access requests for work purposes (even if user lacks authorization)
- Requests that follow normal business processes

**IMPORTANT**: Appropriateness checks ETHICS and SCOPE, not authorization level.
Example: "I need admin rights" is APPROPRIATE (legitimate request) but may be denied due to lack of authorization.

---
**EXAMPLES:**
"""
        
        # Add examples
        for ex in self.examples[:20]:  # Limit to keep prompt size reasonable
            system_prompt += f"\nRequest: \"{ex['body']}\"\n"
            system_prompt += f"INTENT: {ex['category']}\n"
            system_prompt += f"APPROPRIATENESS: {ex['appropriateness']}\n"
        
        system_prompt += """
---
**OUTPUT FORMAT:**
Respond in JSON format with ONLY these two fields:
{{
  "intent": "one of: hardware_issue, software_issue, network_issue, access_request, policy_question, off_scope, ambiguous",
  "appropriateness": "appropriate or not_appropriate"
}}
"""
        
        return system_prompt
    
    def classify_intent_and_appropriateness(self, ticket_text: str) -> Dict[str, any]:
        """
        Main method to classify ticket intent and appropriateness.
        Called by orchestrator.
        
        Args:
            ticket_text: The support ticket text to analyze
            
        Returns:
            dict with keys:
                - intent: str (hardware_issue, software_issue, etc.)
                - is_appropriate: bool
        """
        
        system_prompt = self.build_system_prompt()
        
        classification_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Classify this ticket:\n\n{ticket_text}")
        ])
        
        chain = classification_prompt | self.llm | StrOutputParser()
        result = chain.invoke({"ticket_text": ticket_text})
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
            else:
                json_str = result.strip()
            
            parsed = json.loads(json_str)
            
            intent = parsed.get("intent", "ambiguous")
            appropriateness = parsed.get("appropriateness", "appropriate")
            
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            # Fallback parsing
            intent = "ambiguous"
            appropriateness = "appropriate"
            
            # Try basic text parsing
            result_lower = result.lower()
            if "off_scope" in result_lower:
                intent = "off_scope"
            elif "hardware" in result_lower:
                intent = "hardware_issue"
            elif "software" in result_lower:
                intent = "software_issue"
            elif "network" in result_lower:
                intent = "network_issue"
            elif "access" in result_lower:
                intent = "access_request"
            elif "policy" in result_lower:
                intent = "policy_question"
            
            if "not_appropriate" in result_lower or "not appropriate" in result_lower:
                appropriateness = "not_appropriate"
        
        is_appropriate = appropriateness == "appropriate"
        
        return {
            "intent": intent,
            "is_appropriate": is_appropriate
        }