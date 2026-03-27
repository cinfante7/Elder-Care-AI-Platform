import json
import os
from typing import Tuple, Dict

FAQ_PATH = os.path.join("data", "faq.sample.json")

def load_knowledge_base() -> dict:
    """
    Load the FAQ or knowledge base from the JSON file.
    Returns the dictionary of FAQs.
    """
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_knowledge_base():
    return load_knowledge_base()

def tokenize(text: str) -> set:
    # Simple tokenizer splitting on whitespace and removing punctuation
    import string
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.translate(translator)
    return set(clean_text.lower().split())

def search_knowledge_base(query: str, context: Dict) -> Tuple[str, Dict]:
    """
    Perform a context-aware query search.
    """
    knowledge_base = get_knowledge_base()

    query_tokens = tokenize(query)
    last_intent = context.get("last_intent", None)

    # Simple context-aware clarification example
    if last_intent == "awaiting_clarification":
        if "medication" in query.lower():
            response = knowledge_base.get("check medication list", "Here is your medication schedule.")
            updated_context = {"last_intent": "medication_inquiry"}
        elif "calendar" in query.lower():
            response = knowledge_base.get("daily tasks", "Here are your upcoming calendar events.")
            updated_context = {"last_intent": "calendar_inquiry"}
        else:
            response = "Sorry, I didn't understand. Do you want medication or calendar info?"
            updated_context = {"last_intent": "awaiting_clarification"}
        return response, updated_context

    # Match FAQ keys based on word overlap
    best_match = None
    max_overlap = 0
    min_threshold = 1  # Allow single-word matches
    
    for key, answer in knowledge_base.items():
        key_tokens = tokenize(key)
        overlap = len(query_tokens.intersection(key_tokens))
        
        # For single-word queries, be more flexible
        if len(query_tokens) == 1 and overlap >= 1:
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = (answer, key)
        # For multi-word queries, require at least 2 word overlap
        elif len(query_tokens) > 1 and overlap >= 2:
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = (answer, key)

    if best_match:
        response, matched_key = best_match
        updated_context = {"last_intent": matched_key}
        return response, updated_context

    # Fallback generic response
    return "I'm here to help you with that.", {"last_intent": "general_query"}
