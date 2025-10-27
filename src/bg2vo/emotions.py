"""Emotion detection for dialogue lines to guide TTS synthesis."""
from __future__ import annotations

import re
from typing import Literal

EmotionType = Literal["angry", "sad", "happy", "fear", "neutral", "urgent", "hesitant", "borrowed_voice"]


def detect_emotion(text: str) -> EmotionType:
    """
    Detect emotion from dialogue text using keyword analysis and punctuation.
    
    Returns emotion label for use with Index-TTS emo_audio_prompt parameter.
    """
    text_lower = text.lower()
    
    # ANGRY/AGGRESSIVE patterns
    angry_keywords = [
        'rip', 'tear', 'kill', 'die', 'death', 'blood', 'fool', 'idiot',
        'damn', 'curse', 'enough!', 'silence!', 'attack', 'fight', 'battle',
        'rage', 'fury', 'hate', 'destroy', 'crush'
    ]
    
    # SAD/MOURNING patterns
    sad_keywords = [
        'khalid', 'dead', 'lost', 'gone', 'mourn', 'grief', 'sorrow',
        'miss', 'alone', 'tears', 'cry', 'weep', 'pain', 'suffer',
        'goodbye', 'farewell', 'never again'
    ]
    
    # HAPPY/PLEASED patterns
    happy_keywords = [
        'wonderful', 'excellent', 'perfect', 'good', 'great', 'joy',
        'delight', 'pleased', 'glad', 'happy', 'smile', 'laugh',
        'celebrate', 'success', 'victory', 'triumph'
    ]
    
    # FEAR/WORRY patterns
    fear_keywords = [
        'afraid', 'fear', 'scared', 'worry', 'danger', 'trap', 'help!',
        'run!', 'flee', 'escape', 'hide', 'careful', 'watch out',
        'beware', 'threat', 'peril'
    ]
    
    # URGENT/TENSE patterns
    urgent_keywords = [
        'hurry', 'quick', 'fast', 'now!', 'must', 'immediately', 'urgent',
        'rush', 'time', 'before', 'after', 'soon', 'wait'
    ]
    
    # Punctuation-based detection
    exclamation_count = text.count('!')
    question_count = text.count('?')
    ellipsis_count = text.count('...')
    
    # Multiple exclamations = anger or urgency
    if exclamation_count >= 2:
        return "angry"
    
    # Ellipsis = hesitation, sadness, or trailing off
    if ellipsis_count >= 2:
        return "sad"
    
    # Keyword-based detection (prioritized)
    if any(keyword in text_lower for keyword in angry_keywords):
        return "angry"
    
    if any(keyword in text_lower for keyword in sad_keywords):
        return "sad"
    
    if any(keyword in text_lower for keyword in fear_keywords):
        return "fear"
    
    if any(keyword in text_lower for keyword in happy_keywords):
        return "happy"
    
    if any(keyword in text_lower for keyword in urgent_keywords):
        return "urgent"
    
    # Question with urgency = fear or concern
    if question_count > 0 and any(word in text_lower for word in ['what', 'where', 'who', 'how', 'why']):
        if any(word in text_lower for word in ['happen', 'wrong', 'matter', 'is it']):
            return "fear"
    
    # All caps words = shouting/anger
    if re.search(r'\b[A-Z]{3,}\b', text):
        return "angry"
    
    # Default neutral
    return "neutral"


def get_emotion_config(emotion: EmotionType, character: str) -> dict:
    """
    Get Index-TTS emotion configuration for a character and emotion.
    
    Uses emotion vectors (Index-TTS v2.0+ feature) instead of audio references.
    Emotion vectors are 8D: [Happy, Angry, Sad, Afraid, Disgusted, Melancholic, Surprised, Calm]
    
    Returns dict with emo_vector (list of 8 floats, 0.0-1.0 each).
    
    Special emotion 'borrowed_voice' is used when a character borrows another
    companion's voice. This doesn't add emotion params but serves as a marker.
    """
    # Emotion vectors: [Happy, Angry, Sad, Afraid, Disgusted, Melancholic, Surprised, Calm]
    # All emotions capped at 30% (0.3) max for subtlety
    emotion_vectors = {
        "angry": {
            "vector": [0.0, 0.3, 0.0, 0.0, 0.15, 0.0, 0.0, 0.0],  # Moderate angry, some disgust
        },
        "sad": {
            "vector": [0.0, 0.0, 0.3, 0.0, 0.0, 0.2, 0.0, 0.0],  # Sad + melancholic
        },
        "happy": {
            "vector": [0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15, 0.0],  # Happy + some surprise
        },
        "fear": {
            "vector": [0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.15, 0.0],  # Afraid + surprise
        },
        "urgent": {
            "vector": [0.0, 0.25, 0.0, 0.15, 0.0, 0.0, 0.0, 0.0],  # Moderate angry + some fear
        },
        "hesitant": {
            "vector": [0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0],  # Fear + some sadness
        },
        "borrowed_voice": {
            "vector": None,  # Marker only - uses speed/pitch_shift instead
        },
        "neutral": {
            "vector": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3],  # Calm/neutral
        },
    }
    
    config = emotion_vectors.get(emotion, emotion_vectors["neutral"])
    
    result = {}
    if config["vector"]:
        result["emo_vector"] = config["vector"]
    
    return result


def analyze_dialogue_emotions(csv_path: str) -> dict[str, int]:
    """
    Analyze a CSV file and count emotion distribution.
    
    Returns dict mapping emotion type to count.
    """
    import csv
    from pathlib import Path
    
    emotion_counts: dict[str, int] = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            emotion = detect_emotion(row['Text'])
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    return emotion_counts
