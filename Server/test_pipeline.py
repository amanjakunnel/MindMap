#!/usr/bin/env python3
"""
Test script for the mind map pipeline.
Imports build_mind_map directly from server.py (no Flask server needed).
"""
import sys
import json
sys.path.insert(0, '/Users/amanjakunnel/Desktop/MindMap/Server')

# Suppress Flask/model loading noise
import io, os

# Patch so Flask app doesn't start
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

from server import extract, build_mind_map

SAMPLE_DIR = '/Users/amanjakunnel/Desktop/MindMap/Server/Sample Text'
DOCS = [
    ('mitochondria.docx', 'Mitochondria'),
    ('smash.docx', 'Super Smash Bros'),
    ('Image_Synthesis_from_themes_generated_in_Poems_using_latent_diffusion_models.pdf',
     'Image Synthesis from Poem Themes'),
]

def assess(result, title):
    """Print structured assessment of the mind map output."""
    print(f"\n{'='*60}")
    print(f"DOCUMENT: {title}")
    print(f"{'='*60}")
    if not result:
        print("  [ERROR] Empty result!")
        return

    all_phrases = []
    print(f"Keywords ({len(result)}): {list(result.keys())}\n")
    for kw, phrases in result.items():
        print(f"  [{kw}]  ({len(phrases)} sub-phrases)")
        for p in phrases:
            print(f"    - {p}")
            all_phrases.append(p)
        if not phrases:
            print("    [WARNING] No sub-phrases!")

    # Check for cross-branch duplicates
    from collections import Counter
    freq = Counter(all_phrases)
    dupes = [p for p, c in freq.items() if c > 1]
    if dupes:
        print(f"\n  [PROBLEM] Cross-branch duplicates: {dupes}")
    else:
        print("\n  [OK] No cross-branch duplicates")

    # Check for leading articles
    bad_art = [p for p in all_phrases if p.lower().startswith(('the ', 'a ', 'an '))]
    if bad_art:
        print(f"  [PROBLEM] Leading articles: {bad_art}")
    else:
        print("  [OK] No leading articles")

    # Check if any phrase contains the title words
    title_words = {w.lower() for w in title.split() if len(w) > 3}
    phrase_has_title = [p for p in all_phrases
                        if any(tw in p.lower() for tw in title_words)]
    if phrase_has_title:
        print(f"  [WARNING] Phrases containing title words: {phrase_has_title}")


for fname, title in DOCS:
    fpath = os.path.join(SAMPLE_DIR, fname)
    if not os.path.exists(fpath):
        print(f"[SKIP] {fname} not found")
        continue
    print(f"\nProcessing {fname}...")
    text = extract(fpath)
    result = build_mind_map(text, title)
    assess(result, title)

print("\n\nDone.")
