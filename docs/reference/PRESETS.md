# Voice Preset Guidelines

This file captures the evolving mapping between character traits and Index‑TTS settings. Use it as the canonical reference when expanding `config/voices.sample.json` or `data/voices.json`.

## Trait Grid

| Archetype | Energy | Timbre | Suggested Voice | Speed Δ | Pitch Δ | Notes |
|-----------|--------|--------|-----------------|---------|---------|-------|
| Cheery Young Female | High | Bright | `female_lighthearted` | +0.04 | +0.12 | Ideal for Imoen-style characters. Keep micro-pauses short. |
| Stoic Ranger/Druid | Medium-Low | Neutral | `female_determined` | -0.03 | -0.05 | Works for Jaheira-like lines; emphasize consonants. |
| Heroic Berserker | High | Warm | `male_big_hearted` | +0.05 | +0.08 | Use for Minsc and similar high-octane deliveries. |
| Smooth Rogue | Medium | Soft | `male_rogue` | -0.01 | +0.02 | Controlled, sly tone. Keep laugh lines subtle. |
| Deadpan Narrator | Low | Neutral | `narrator` | 0.0 | 0.0 | Default fallback. |

## Adding a New Preset

1. Identify dominant traits from `data/character_cards.json` (once the draft script is fleshed out).
2. Choose the closest archetype above or create a new row.
3. Record the chosen `voice`, `speed`, and `pitch` adjustments.
4. Optionally, note `ref` files for pseudo-reference conditioning.
5. Update both `config/voices.sample.json` (for experimentation) and `data/voices.json` (for production) accordingly.

## Reference Audio Strategy

- Place seed prompts under `data/style_seeds/<Speaker>.txt` (one line per prompt).
- Render them with `scripts/gen_pseudorefs.py` to create `refs/<Speaker>.wav`.
- Add the `"ref": "refs/<Speaker>.wav"` property to the speaker’s voice config.

## Change Management

- Log preset changes in `VOICE_IMPROVEMENT_LOG.md` with date, StrRefs affected, and reasoning.
- When a preset is considered final, mark the speaker as `Status=Locked` in `data/characters.csv` (once the roster file is introduced).
