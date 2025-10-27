"""
Vocalization Detection and Classification

Detects and classifies non-verbal vocalizations (grunts, yells, screams, etc.)
using pattern-based regex matching with confidence scoring.

Example:
    from classify_vocalizations import classify_text, VocalizationType
    
    result = classify_text("Gllgghh!")
    if result:
        print(f"Type: {result['type']}, Confidence: {result['confidence']}")
"""

import re
from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass


class VocalizationType(Enum):
    """Types of vocalizations that can be detected."""
    GRUNT = "grunt"           # Grunts, groans, ugh sounds
    SCREAM = "scream"         # Screams, shrieks, piercing cries
    MOAN = "moan"             # Moans, whimpers, pained sounds
    YELL = "yell"             # Yells, shouts, battle cries
    GASP = "gasp"             # Gasps, sudden intakes of breath
    LAUGH = "laugh"           # Laughter, chuckles, giggles
    CRY = "cry"               # Crying, sobbing, weeping
    COUGH = "cough"           # Coughing, clearing throat
    SIGH = "sigh"             # Sighs, exhales
    GENERIC = "generic"       # Generic non-verbal sound


@dataclass
class VocalizationPattern:
    """Pattern definition for vocalization matching."""
    type: VocalizationType
    pattern: str              # Regex pattern
    confidence: float         # Base confidence score (0.0-1.0)
    description: str          # Human-readable description


# Vocalization patterns ordered by specificity (most specific first)
VOCALIZATION_PATTERNS: List[VocalizationPattern] = [
    # Action descriptions (explicit markers)
    VocalizationPattern(
        type=VocalizationType.COUGH,
        pattern=r'\*\s*cough\s*\*',
        confidence=1.0,
        description="Explicit cough marker"
    ),
    VocalizationPattern(
        type=VocalizationType.CRY,
        pattern=r'\*\s*sob\s*\*',
        confidence=1.0,
        description="Explicit sob marker"
    ),
    VocalizationPattern(
        type=VocalizationType.GASP,
        pattern=r'\*\s*gasp\s*\*',
        confidence=1.0,
        description="Explicit gasp marker"
    ),
    VocalizationPattern(
        type=VocalizationType.SIGH,
        pattern=r'\*\s*sigh\s*\*',
        confidence=1.0,
        description="Explicit sigh marker"
    ),
    VocalizationPattern(
        type=VocalizationType.LAUGH,
        pattern=r'\*\s*(laugh|chuckle|giggle|snicker|heh)\s*\*',
        confidence=1.0,
        description="Explicit laugh marker"
    ),
    
    # High-confidence phonetic patterns
    VocalizationPattern(
        type=VocalizationType.SCREAM,
        pattern=r'^[aei]{3,}[aeiou]*[gh]*!+$',
        confidence=0.95,
        description="Scream pattern (aaah!, eeeek!)"
    ),
    VocalizationPattern(
        type=VocalizationType.GRUNT,
        pattern=r'^[ug]+[rl]*[gh]+[!\.]*$',
        confidence=0.9,
        description="Grunt pattern (ugh, grrr, urgh)"
    ),
    VocalizationPattern(
        type=VocalizationType.GRUNT,
        pattern=r'^g+l+[gh]+[!\.]*$',
        confidence=0.9,
        description="Grunt pattern (gllgghh)"
    ),
    VocalizationPattern(
        type=VocalizationType.YELL,
        pattern=r'^[rae]+[gh]*!+$',
        confidence=0.85,
        description="Yell pattern (raaagh!, yaah!)"
    ),
    VocalizationPattern(
        type=VocalizationType.MOAN,
        pattern=r'^[uo]+[wh]*[!\.]*$',
        confidence=0.85,
        description="Moan pattern (ooh, uhhh, oww)"
    ),
    VocalizationPattern(
        type=VocalizationType.GASP,
        pattern=r'^[ha]+[sp]*h*[!\.]*$',
        confidence=0.8,
        description="Gasp pattern (hasp, hah)"
    ),
    VocalizationPattern(
        type=VocalizationType.LAUGH,
        pattern=r'^he+[h]*[!\.]*$',
        confidence=0.8,
        description="Laugh pattern (heh, hehe)"
    ),
    VocalizationPattern(
        type=VocalizationType.SIGH,
        pattern=r'^[ha]+[ah]*\.+$',
        confidence=0.75,
        description="Sigh pattern (haa..., ahh...)"
    ),
    
    # Medium-confidence patterns
    VocalizationPattern(
        type=VocalizationType.YELL,
        pattern=r'^no+!+$',
        confidence=0.7,
        description="Emphatic no"
    ),
    VocalizationPattern(
        type=VocalizationType.CRY,
        pattern=r'^[nw]+o+[!\.]+$',
        confidence=0.7,
        description="Cry pattern (nooo, woo)"
    ),
    
    # Generic low-confidence patterns (catch-all)
    VocalizationPattern(
        type=VocalizationType.GENERIC,
        pattern=r'^[aeiou]{2,}[bcdfghjklmnpqrstvwxyz]*[!\.]+$',
        confidence=0.5,
        description="Generic vocalization"
    ),
    VocalizationPattern(
        type=VocalizationType.GENERIC,
        pattern=r'^[bcdfghjklmnpqrstvwxyz]{3,}[!\.]*$',
        confidence=0.4,
        description="Consonant-heavy non-word"
    ),
]


def classify_word(word: str) -> Optional[Dict]:
    """
    Classify a single word as a vocalization.
    
    Args:
        word: Single word to classify
        
    Returns:
        Dictionary with 'type' (VocalizationType), 'confidence' (float), 
        'pattern' (str), or None if not a vocalization
    """
    # Normalize: lowercase, strip extra whitespace
    normalized = word.strip().lower()
    
    # Skip empty or very short words
    if len(normalized) < 2:
        return None
    
    # Skip words that are clearly regular speech
    if normalized in ['i', 'a', 'the', 'is', 'it', 'to', 'in', 'of', 'and', 'or']:
        return None
    
    # Try each pattern in order (most specific first)
    for voc_pattern in VOCALIZATION_PATTERNS:
        if re.match(voc_pattern.pattern, normalized, re.IGNORECASE):
            return {
                'type': voc_pattern.type,
                'confidence': voc_pattern.confidence,
                'pattern': voc_pattern.description,
                'original': word
            }
    
    return None


def classify_text(text: str, min_confidence: float = 0.5) -> Optional[Dict]:
    """
    Classify text as containing vocalizations.
    
    If the text contains multiple words, classifies each separately and
    returns the highest-confidence match. If the entire text is a single
    vocalization, returns that classification.
    
    Args:
        text: Text to classify (can be single or multiple words)
        min_confidence: Minimum confidence threshold (0.0-1.0)
        
    Returns:
        Dictionary with:
            - 'type': VocalizationType
            - 'confidence': float (0.0-1.0)
            - 'pattern': str (description of matched pattern)
            - 'original': str (original text)
            - 'is_pure': bool (True if entire text is vocalization)
        Returns None if no vocalization detected above threshold
    """
    if not text or not text.strip():
        return None
    
    # Check if entire text is a single vocalization (no spaces except in markers)
    # Remove common markers first
    clean_text = re.sub(r'\*[^*]+\*', '', text)
    clean_text = clean_text.strip()
    
    # If single word after removing markers
    words = clean_text.split()
    if len(words) == 1:
        result = classify_word(text)  # Use original with markers
        if result and result['confidence'] >= min_confidence:
            result['is_pure'] = True
            return result
    
    # Multi-word text: find all vocalizations and return highest confidence
    vocalizations = []
    
    # Check for action markers
    for voc_pattern in VOCALIZATION_PATTERNS:
        if '*' in voc_pattern.pattern:  # Action marker patterns
            matches = re.finditer(voc_pattern.pattern, text, re.IGNORECASE)
            for match in matches:
                if voc_pattern.confidence >= min_confidence:
                    vocalizations.append({
                        'type': voc_pattern.type,
                        'confidence': voc_pattern.confidence,
                        'pattern': voc_pattern.description,
                        'original': match.group(0),
                        'is_pure': False
                    })
    
    # Check individual words
    for word in words:
        result = classify_word(word)
        if result and result['confidence'] >= min_confidence:
            result['is_pure'] = False
            vocalizations.append(result)
    
    # Return highest confidence vocalization
    if vocalizations:
        return max(vocalizations, key=lambda x: x['confidence'])
    
    return None


def is_vocalization(text: str, min_confidence: float = 0.5) -> bool:
    """
    Check if text contains a vocalization.
    
    Args:
        text: Text to check
        min_confidence: Minimum confidence threshold
        
    Returns:
        True if vocalization detected above threshold
    """
    return classify_text(text, min_confidence) is not None


def get_vocalization_type(text: str, min_confidence: float = 0.5) -> Optional[VocalizationType]:
    """
    Get the vocalization type of text.
    
    Args:
        text: Text to classify
        min_confidence: Minimum confidence threshold
        
    Returns:
        VocalizationType if detected, None otherwise
    """
    result = classify_text(text, min_confidence)
    return result['type'] if result else None


# Test/demo code
if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Gllgghh!",           # Jaheira's grunt
        "No!",                # Emphatic yell
        "Heh...",             # Laugh
        "*cough*",            # Action marker
        "I... *cough* *cough*... I am not here",  # Mixed text
        "Aaaaaah!",           # Scream
        "Ugh.",               # Grunt
        "Raaagh!",            # Battle yell
        "This is normal speech",  # Should not match
    ]
    
    print("Vocalization Classification Test\n")
    print("=" * 60)
    
    for text in test_cases:
        result = classify_text(text)
        if result:
            print(f"\nText: '{text}'")
            print(f"  Type: {result['type'].value}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Pattern: {result['pattern']}")
            print(f"  Pure Vocalization: {result['is_pure']}")
        else:
            print(f"\nText: '{text}'")
            print(f"  No vocalization detected")
