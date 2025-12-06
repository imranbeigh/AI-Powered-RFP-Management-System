import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class GroqAIService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
    
    def _call_groq(self, messages: List[Dict[str, str]]) -> str:
        """Make API call to Groq"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API call failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid response format from Groq: {str(e)}")
    
    def parse_natural_language_to_rfp(self, text: str) -> Dict[str, Any]:
        """Convert natural language to structured RFP data"""
        prompt = f"""
Extract the following from this procurement request and return as valid JSON:
- Title (brief summary)
- Items needed (list with quantities and specifications)
- Total budget
- Deadline
- Payment terms
- Warranty requirements
- Any other special conditions

User input: {text}

Return JSON with this exact structure:
{{
    "title": "",
    "items": [
        {{"name": "", "quantity": 0, "specs": ""}}
    ],
    "budget": 0,
    "deadline": "",
    "payment_terms": "",
    "warranty": "",
    "special_conditions": ""
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a procurement expert who extracts structured data from natural language requests. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_groq(messages)
            # Clean up response to extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    
    def parse_vendor_response(self, email_content: str) -> Dict[str, Any]:
        """Parse vendor proposal email and extract structured data"""
        prompt = f"""
Parse this vendor proposal email and extract the following information as valid JSON:
- Items with individual prices
- Total price
- Delivery time
- Warranty offered
- Payment terms
- Any special notes or conditions

Email content: {email_content}

Return JSON with this structure:
{{
    "items": [
        {{"name": "", "quantity": 0, "unit_price": 0, "total_price": 0}}
    ],
    "total_price": 0,
    "delivery_time": "",
    "warranty": "",
    "payment_terms": "",
    "special_notes": ""
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an expert at parsing vendor proposals. Extract all pricing and terms information accurately. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_groq(messages)
            # Clean up response to extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse vendor response as JSON: {str(e)}")
    
    def compare_and_recommend(self, proposals_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare proposals and provide recommendations"""
        proposals_json = json.dumps(proposals_list, indent=2)
        
        prompt = f"""
Compare these vendor proposals and provide a detailed analysis:

Proposals:
{proposals_json}

Analyze each proposal and:
1. Score each vendor (0-100) based on:
   - Price competitiveness (lower is better, but quality matters)
   - Delivery time (faster is better)
   - Warranty quality
   - Completeness of response
   - Terms and conditions favorability

2. Identify the best vendor with detailed reasoning
3. Highlight pros and cons for each vendor
4. Provide overall recommendation

Return JSON with this structure:
{{
    "rankings": [
        {{
            "vendor_id": 0,
            "vendor_name": "",
            "score": 0,
            "pros": [""],
            "cons": [""],
            "detailed_analysis": ""
        }}
    ],
    "recommendation": {{
        "best_vendor_id": 0,
        "best_vendor_name": "",
        "reasoning": "",
        "confidence": 0.0,
        "key_factors": [""]
    }},
    "summary": ""
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a procurement analyst expert at comparing vendor proposals. Provide objective, detailed analysis with clear reasoning. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_groq(messages)
            # Clean up response to extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse comparison response as JSON: {str(e)}")

# Singleton instance
ai_service = GroqAIService()
