# Prompt for Next Chat Session

Copy and paste this prompt when starting your new chat:

---

I'm working on a BG2 voiceover mod using Index-TTS v2.0 for voice synthesis. I've just completed setting up all voice references for Chapter 1 (8 speakers, 905 lines).

**Current Status:**
- 7 speakers approved and locked (Jaheira, Minsc, Imoen, Yoshimo, Valygar, Rielev, Dryad)
- 1 speaker ready for final approval (Ilyich - custom ElevenLabs voice with emotion detection + post-processing)
- Ilyich's 4 test lines just finished generating with these settings:
  - ElevenLabs v3 reference (30.9s)
  - Auto-detected emotion: "angry" (30% intensity, 15% disgusted)
  - Post-processing: pitch -2 semitones, speed 0.95x, pauses 0.45s
  - CUDA GPU enabled

**What I Need:**
Please check if Ilyich's generation completed successfully. The 4 test files should be in `build/OGG/` with StrRefs: 18384, 18447, 18449, 18450.

Once I approve his voice, I'm ready to start the full Chapter 1 synthesis (905 lines, ~1-2 hours with GPU).

**Reference Documentation:**
- Main handover guide: `docs/HANDOVER_CHAPTER1_SYNTHESIS.md`
- Emotion system: `docs/technical/EMOTION_SYSTEM.md`
- Post-processing: `docs/technical/POST_PROCESSING.md`
- ElevenLabs workflow: `docs/workflows/ELEVENLABS_INTEGRATION.md`

**System Setup:**
- Python 3.13.9 (main environment at `C:\Users\tenod\AppData\Local\Programs\Python\Python313`)
- Python 3.10.19 (Index-TTS .venv at `C:\Users\tenod\source\repos\TTS\index-tts\.venv`)
- Repository: `C:\Users\tenod\source\repos\BG2 Voiceover`
- All voice references in `refs/` directory
- Configuration in `data/voices.json`
- Chapter 1 data: `data/chapter1_split.csv` (905 lines ready)

Let's start by verifying Ilyich's generation, then proceed with approval and full synthesis.

---

**Alternative Shorter Version** (if token budget is tight):

I'm working on BG2 voiceover synthesis. Just completed voice setup for Chapter 1 (8 speakers, 905 lines). 7 speakers locked, 1 (Ilyich) awaiting approval after test generation. Repository: `C:\Users\tenod\source\repos\BG2 Voiceover`. Check `docs/HANDOVER_CHAPTER1_SYNTHESIS.md` for complete context. Need to verify Ilyich test files (18384, 18447, 18449, 18450.wav in `build/OGG/`) then start full synthesis.
