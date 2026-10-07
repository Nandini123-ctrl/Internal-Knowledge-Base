import re

# Mock database of 50 known AI startups / canonical entities
CANONICAL_STARTUPS = [
    "openai", "anthropic", "cohere", "mistral ai", "stability ai", 
    "hugging face", "perplexity ai", "runway", "elevenlabs", "adept"
]

def canonicalize_entity(raw_name):
    """Normalizes messy startup strings to match canonical forms"""
    if not raw_name:
        return "Unknown"
    
    # Clean the string: lowercase, strip punctuation/legal suffixes
    cleaned = raw_name.lower().strip()
    cleaned = re.sub(r'\b(inc|llc|corp|co|limited|ltd)\b', '', cleaned)
    cleaned = re.sub(r'[,.\-_]', ' ', cleaned)
    cleaned = " ".join(cleaned.split()) # normalize spacing
    
    # Check against seed list
    for canonical in CANONICAL_STARTUPS:
        if canonical in cleaned or cleaned in canonical:
            # Return title case version of the canonical name
            return canonical.title()
            
    # Default fallback: return clean title case if no exact seed match
    return raw_name.strip()

if __name__ == "__main__":
    # Test cases showing resolution of messy variations
    test_cases = ["OpenAI, Inc.", "  open ai ", "Anthropic LLC", "Cohere Corp"]
    print("Entity Resolution Test:")
    for test in test_cases:
        print(f"Raw: '{test}' --> Canonical: '{canonicalize_entity(test)}'")
