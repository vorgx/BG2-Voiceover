# Emotion-Aware Synthesis System

## Overview

Automatic emotion detection and application for Index-TTS synthesis to match dialogue tone.

## How It Works

### 1. Text Analysis
The `bg2vo.emotions.detect_emotion()` function analyzes dialogue text for:
- **Keywords**: Character names (Khalid = sad), action words (rip/kill = angry)
- **Punctuation**: Multiple `!` = angry, `...` = hesitant/sad, `?` = questioning
- **Context**: Combined signals (e.g., "Khalid... No!" = mourning + anger)

### 2. Emotion Categories

| Emotion | Triggers | Example Lines |
|---------|----------|---------------|
| **angry** | rip, kill, enough!, curse | "You will watch your tongue lest I rip it from you!" |
| **sad** | khalid, mourn, death, lost | "Kha... Khalid?" "I will mourn according to what I believe." |
| **happy** | wonderful, excellent, pleased | (Less common in Chapter 1 dungeon context) |
| **fear** | afraid, danger, trap, help! | (Combat/surprise situations) |
| **urgent** | hurry, quick, must, now! | "We... we must hurry before we are noticed." |
| **neutral** | Default fallback | Regular conversational dialogue |

### 3. Emotional Reference Clips

Located in `refs/emotions/<character>/`:
- `angry.wav` - Forceful, stern delivery
- `sad.wav` - Mourning, grief-stricken
- `happy.wav` - Pleased, content
- `fear.wav` - Worried, concerned
- `urgent.wav` - Tense, hurried

**For Jaheira:**
- angry: JAHEIR17.WAV (3.86 sec)
- sad: JAHEIR01.WAV (6.53 sec - Khalid mourning)
- happy: JAHEIR15.WAV (5.07 sec)
- fear: JAHEIR19.WAV (4.50 sec)
- urgent: JAHEIR07.WAV (4.04 sec)

### 4. Index-TTS Parameters

When emotion detected, adds to voice config:
```json
{
  "voice": "refs/jaheira_ref.wav",
  "emo_audio_prompt": "refs/emotions/jaheira/sad.wav",
  "emo_alpha": 0.7
}
```

**emo_alpha values:**
- 0.8 = Strong emotion (angry)
- 0.7 = Clear emotion (sad, fear)
- 0.6 = Moderate emotion (happy)
- 0.5 = Subtle emotion (urgent)
- 0.0 = No emotion (neutral)

## Integration with synth.py

The `synth_one()` function now:
1. Detects emotion from dialogue text
2. Gets emotion config (reference clip + alpha)
3. Merges with character voice config
4. Uses Index-TTS Python API for emotion parameters
5. Prints detected emotion: `🎭 Detected emotion: sad`

## Testing

### Verify Emotion Detection

```python
from bg2vo.emotions import detect_emotion

test_lines = [
    "Kha... Khalid?",                                    # Should detect: sad
    "You will watch your tongue lest I rip it from you!", # Should detect: angry
    "We must hurry before we are noticed.",              # Should detect: urgent
]

for line in test_lines:
    emotion = detect_emotion(line)
    print(f"{emotion:<10} | {line}")
```

### Test Synthesis

```powershell
# Regenerate with emotion detection
python scripts/core/synth.py --input data/test_jaheira.csv
```

Look for emotion indicators in output:
```
Generating: 1035 -> build/OGG/1035.wav
  🎭 Detected emotion: sad
Generating (API): 1035 -> build/OGG/1035.wav
```

## Manual Override

You can still manually specify emotion per character in `data/voices.json`:

```json
"Jaheira": {
  "voice": "C:\\Users\\tenod\\source\\repos\\BG2 Voiceover\\refs\\jaheira_ref.wav",
  "emo_audio_prompt": "refs/emotions/jaheira/sad.wav",
  "emo_alpha": 0.8,
  "notes": "Force sad/mourning tone for all lines"
}
```

Manual settings override automatic detection.

## Creating Emotion Refs for Other Characters

1. Listen to original BG2 audio files
2. Identify clips showing clear emotion
3. Copy to `refs/emotions/<character>/<emotion>.wav`
4. Test synthesis with character lines

Example for Minsc:
```python
# refs/emotions/minsc/angry.wav - Battle cry
# refs/emotions/minsc/happy.wav - Victory quote
# refs/emotions/minsc/sad.wav - Concerned about Boo
```

## Limitations

- Emotion detection is keyword-based (not AI/ML)
- May misdetect complex sarcasm or subtext
- Requires manual emotion reference clips per character
- Best results with clear emotional language

## Future Improvements

- [ ] LLM-based emotion detection (GPT/Claude API)
- [ ] Per-line emotion overrides in CSV (new column: `Emotion`)
- [ ] Multiple emotion refs per type (random selection)
- [ ] Emotion intensity scaling (mild vs intense anger)
- [ ] Context-aware detection (previous line influences current)

## Files Modified

- `src/bg2vo/emotions.py` - NEW emotion detection module
- `scripts/core/synth.py` - Integrated emotion detection in synth_one()
- `refs/emotions/jaheira/*.wav` - NEW emotional reference clips
