import os
import re
import json
import ssl
import string
import nltk
import spacy
import docx
import PyPDF2

from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

# SSL fix for NLTK downloads
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# Load models once at startup
print("Loading NLP models...")
_sent_model = SentenceTransformer('all-MiniLM-L6-v2')
_nlp = spacy.load("en_core_web_lg")
print("Models ready.")

GENERIC_WORDS = {
    'figure', 'table', 'section', 'paper', 'work', 'model', 'method',
    'approach', 'result', 'study', 'system', 'show', 'propose', 'present',
    'use', 'base', 'include', 'provide', 'discuss', 'example', 'type',
    'number', 'level', 'point', 'case', 'term', 'area', 'field', 'word',
    'note', 'task', 'feature', 'process', 'problem', 'also', 'however',
    'thing', 'way', 'part', 'kind', 'form', 'group', 'set', 'step',
    'fact', 'role', 'rate', 'size', 'time', 'place', 'state', 'order',
    'amount', 'degree', 'range', 'sense', 'reason', 'aspect', 'factor',
    'effect', 'impact', 'output', 'input', 'version', 'stage', 'phase',
    'item', 'unit', 'value', 'data', 'info', 'detail', 'content', 'extent',
}

# Determiners / pronouns that should never start a sub-phrase
_BAD_STARTERS = {
    'those', 'these', 'this', 'that', 'other', 'each', 'every', 'any',
    'our', 'their', 'its', 'his', 'her', 'some', 'all', 'both', 'such',
    'certain', 'various', 'several', 'many', 'more', 'most', 'which',
    'what', 'where', 'when', 'how', 'why', 'also', 'therefore', 'thus',
    'different', 'similar', 'same', 'new', 'old', 'high', 'low',
    'good', 'better', 'best', 'large', 'small', 'little', 'big',
    'real', 'important', 'significant', 'key', 'main', 'major',
    'next', 'last', 'first', 'second', 'third',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'remaining', 'unnecessary', 'corresponding', 'expressive',
    'only', 'general', 'specific', 'particular', 'pure', 'whole',
    'given', 'current', 'prior', 'recent', 'previous', 'following',
    'further', 'additional', 'final', 'initial', 'original',
    'detailed', 'efficient', 'effective', 'direct', 'indirect',
    'traditional', 'standard', 'typical', 'common', 'popular',
    'known', 'existing', 'proposed', 'related',
    'abstract', 'concrete', 'possible', 'potential', 'critical',
    'important', 'significant', 'major', 'minor', 'simple',
    'straightforward', 'simplified', 'appropriate', 'not', 'less', 'fewer',
    'overall', 'enough', 'aforementioned', 'above', 'below', 'following',
    'higher', 'lower', 'wider', 'deeper', 'broader', 'stronger', 'clearer',
    'better', 'faster', 'larger', 'smaller', 'greater', 'earlier', 'later',
    # Fragments from "state of the art" stripping
    'art',
    # Other weak standalone openers
    'use', 'due', 'via', 'per', 'non', 'sub', 'pre', 'post',
}

# Head nouns that make a phrase too generic regardless of modifiers
_GENERIC_HEADS = {
    'approach', 'method', 'way', 'type', 'form', 'step', 'aspect', 'level',
    'case', 'point', 'example', 'instance', 'version', 'kind', 'mode',
    'basis', 'means', 'measure', 'factor', 'element', 'component',
    'variety', 'manner', 'work', 'evaluation', 'relevance', 'nature',
    'extent', 'degree', 'scope', 'range', 'scale', 'amount', 'number',
    'value', 'process', 'statement', 'issue', 'challenge', 'task',
}


# ── File extraction ────────────────────────────────────────────────────────────

def _clean_text(text):
    """Normalize extracted text: fix hyphenated line-breaks, collapse whitespace."""
    # Truncate at References / Bibliography section (handles various formats)
    ref_pattern = re.compile(
        r'(?:^|\s{2,}|\n)(REFERENCES|References|BIBLIOGRAPHY|Bibliography|Works Cited|WORKS CITED)\s',
        re.MULTILINE
    )
    m = ref_pattern.search(text)
    if m:
        text = text[:m.start()]

    # Rejoin words split across lines with a hyphen (e.g. "compu-\ntation" -> "computation")
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    # Fix soft-hyphens inside words: "compu- tation" -> "computation"
    # This happens in word-processor docs where words are broken for layout
    # Pattern: word-char, hyphen, 1-3 spaces, then a LOWERCASE letter (continuation)
    # (uppercase after hyphen = intentional compound like "high-Energy")
    text = re.sub(r'(\w)-\s{1,3}([a-z])', r'\1\2', text)
    # Replace remaining newlines/tabs inside a paragraph with spaces
    text = re.sub(r'[ \t]*\n[ \t]*', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    # Remove URLs / DOIs / file paths
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    # Remove bracketed citations like [2], [1,2], [1-3]
    text = re.sub(r'\[\d[\d,\-]*\]', '', text)
    # Remove reference-style author fragments: "A.Buluc and J.R.Gilbert, ..."
    text = re.sub(r'[A-Z]\.[A-Za-z]+\s+and\s+[A-Z]\.[A-Za-z]+[^.]*', '', text)
    # Remove reference-style lines: "Author et al. VENUE year" fragments
    text = re.sub(r'\b(et al\.?)\b', '', text)
    return text.strip()


def extract(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.docx':
        doc = docx.Document(filepath)
        raw = '\n'.join(p.text for p in doc.paragraphs)
    elif ext == '.pdf':
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            raw = ''.join(page.extract_text() or '' for page in reader.pages)
    elif ext == '.txt':
        with open(filepath, 'r') as f:
            raw = f.read()
    else:
        return ''
    return _clean_text(raw)


# ── Helpers ────────────────────────────────────────────────────────────────────

def common_prefix_len(a, b):
    n = 0
    for x, y in zip(a.lower(), b.lower()):
        if x == y:
            n += 1
        else:
            break
    return n


def is_variant_of(word, reference_words, sem_threshold=0.72, prefix_threshold=7):
    """True if word is a morphological or semantic variant of any reference word."""
    if not reference_words:
        return False
    ref_list = list(reference_words)
    word_emb = _sent_model.encode([word], show_progress_bar=False)
    ref_embs = _sent_model.encode(ref_list, show_progress_bar=False)
    for i, ref in enumerate(ref_list):
        if util.cos_sim(word_emb, ref_embs[i]).item() > sem_threshold:
            return True
        if common_prefix_len(word, ref) >= prefix_threshold:
            return True
    return False


def semantic_deduplicate(items, threshold=0.75):
    """Remove items too semantically similar to an earlier item."""
    if len(items) <= 1:
        return items
    embs = _sent_model.encode(items, show_progress_bar=False)
    keep = []
    for i in range(len(items)):
        if all(util.cos_sim(embs[i], embs[j]).item() < threshold for j in keep):
            keep.append(i)
    return [items[i] for i in keep]


# ── Stage 1 — Keyword extraction ──────────────────────────────────────────────

def extract_keywords(text, title, n=5):
    sample = text[:12000]
    doc = _nlp(sample)

    # Exclude named entity tokens (people, orgs, places, works of art)
    excluded = set()
    for ent in doc.ents:
        if ent.label_ in ('PERSON', 'ORG', 'GPE', 'LOC', 'NORP', 'FAC', 'WORK_OF_ART'):
            for tok in ent:
                excluded.add(tok.i)

    counts = Counter()
    stop_words = _nlp.Defaults.stop_words
    for token in doc:
        if token.i in excluded:
            continue
        # Skip tokens that are purely numeric or contain digits
        if re.search(r'\d', token.text):
            continue
        lemma = token.lemma_.lower()
        if (token.pos_ in ('NOUN', 'PROPN')
                and len(lemma) >= 4
                and lemma not in stop_words
                and lemma not in GENERIC_WORDS
                and lemma not in string.punctuation):
            counts[lemma] += 1

    candidates = [w for w, _ in counts.most_common(40)]

    # Strip title words and their morphological/semantic variants
    title_words = {w.lower().strip(string.punctuation) for w in title.split()
                   if len(w.strip(string.punctuation)) >= 3}
    # Also include lemmas of title words
    for tw in list(title_words):
        tw_doc = _nlp(tw)
        for t in tw_doc:
            title_words.add(t.lemma_.lower())

    candidates = [
        c for c in candidates
        if not is_variant_of(c, title_words, sem_threshold=0.70, prefix_threshold=6)
    ]

    # Semantic dedup among candidates (removes mitochondria/mitochondrion type pairs)
    candidates = semantic_deduplicate(candidates, threshold=0.72)

    # Final filter: must be at least somewhat specific (not a pure stop-concept)
    candidates = [c for c in candidates if c not in GENERIC_WORDS]

    return candidates[:n]


# ── Stage 2 — Top-K sentence selection per keyword ───────────────────────────

def top_sentences_for_keyword(sentences, keyword, k=20):
    """Return the k sentences most semantically similar to keyword."""
    if not sentences:
        return []
    sent_embs = _sent_model.encode(sentences, show_progress_bar=False)
    kw_emb = _sent_model.encode([keyword], show_progress_bar=False)
    sims = util.cos_sim(kw_emb, sent_embs)[0]
    top_k = min(k, len(sentences))
    indices = sims.argsort(descending=True)[:top_k]
    # Only keep sentences with at least a weak relevance signal
    return [sentences[int(i)] for i in indices if sims[int(i)].item() > 0.1]


# ── Stage 3 — Sub-phrase extraction ───────────────────────────────────────────

def _share_head_noun(a, b):
    """True if two phrases share the same final (head) noun."""
    a_words = [w.strip(string.punctuation) for w in a.split()]
    b_words = [w.strip(string.punctuation) for w in b.split()]
    # Compare last meaningful word
    if a_words and b_words:
        a_last = _nlp(a_words[-1])[0].lemma_.lower()
        b_last = _nlp(b_words[-1])[0].lemma_.lower()
        if a_last == b_last and len(a_last) > 3:
            return True
    return False


def deduplicate_phrases(phrases, threshold=0.72):
    """Remove substring-dominated, same-head-noun, and semantically similar phrases."""
    if len(phrases) <= 1:
        return phrases
    phrase_set = set(phrases)
    # Remove a phrase if it is a strict substring of another phrase
    filtered = [p for p in phrases
                if not any(p != other and p in other for other in phrase_set)]
    if len(filtered) <= 1:
        return filtered
    # Remove phrases that share the same head noun (keep the first/highest-scored one)
    deheaded = []
    head_nouns_seen = set()
    for p in filtered:
        words = [w.strip(string.punctuation) for w in p.split()]
        if words:
            head = _nlp(words[-1])[0].lemma_.lower() if words else ''
            if head and len(head) > 3 and head in head_nouns_seen:
                continue
            if head and len(head) > 3:
                head_nouns_seen.add(head)
        deheaded.append(p)
    if len(deheaded) <= 1:
        return deheaded
    return semantic_deduplicate(deheaded, threshold=threshold)


def _strip_leading_determiners(text):
    """
    Repeatedly strip leading articles and weak determiners from a phrase.
    e.g. "the other words" -> "words"  (strips 'the', then 'other')
    """
    leading = (
        'the ', 'a ', 'an ',
        'those ', 'these ', 'this ', 'that ',
        'other ', 'each ', 'every ', 'any ',
        'our ', 'their ', 'its ', 'his ', 'her ',
        'some ', 'all ', 'both ', 'such ',
        'certain ', 'various ', 'several ',
        'many ', 'more ', 'most ',
        'also ', 'therefore ', 'thus ',
    )
    changed = True
    while changed:
        changed = False
        t = text.lower().strip()
        for prefix in leading:
            if t.startswith(prefix):
                text = t[len(prefix):].strip()
                changed = True
                break
    return text.strip()


def _normalize_apostrophe(s):
    """Replace Unicode smart quotes / apostrophes with ASCII equivalents."""
    return s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')


def _word_tokens(w):
    """Return all surface + lemma forms of a word for skip-token matching.

    Hyphenated tokens (e.g. 'high-energy') are treated as a single unit —
    we do NOT split on the hyphen so that compound adjectives like
    'high-energy' are not rejected just because 'energy' is a skip token.
    """
    w = _normalize_apostrophe(w)
    w_clean = re.sub(r"'s$|s'$", '', w.strip(string.punctuation)).lower()
    forms = {w_clean}
    # Only tokenize if the word is not a hyphenated compound
    if '-' not in w_clean:
        for t in _nlp(w_clean):
            forms.add(t.lemma_.lower())
    return forms


def _is_bad_phrase(phrase, skip_tokens):
    """Return True if the phrase should be rejected."""
    # Normalize smart apostrophes/quotes first
    phrase = _normalize_apostrophe(phrase)
    words = phrase.split()
    if len(words) < 2 or len(words) > 5:
        return True
    # Must contain at least one alphabetic character
    if not any(c.isalpha() for c in phrase):
        return True
    # Reject if phrase contains digits (likely a citation, version number, etc.)
    if re.search(r'\d', phrase):
        return True
    # Reject if phrase contains underscores (code identifiers like row_ptr)
    if '_' in phrase:
        return True
    # Reject if first word is too short (likely a fragment like "art", "use", etc.)
    first_alpha = re.sub(r'[^a-zA-Z]', '', words[0])
    if len(first_alpha) <= 2 and '-' not in words[0]:
        return True
    # Reject if first word is a bad starter
    if words[0].lower() in _BAD_STARTERS:
        return True
    # Reject if any skip token appears in the phrase (including possessives + lemmas)
    for w in words:
        if _word_tokens(w) & skip_tokens:
            return True
    # Reject if any single-character token (after stripping punctuation + possessives)
    for w in words:
        w_bare = re.sub(r"'s$|s'$", '', w.strip(string.punctuation))
        if len(w_bare) <= 1:
            return True
    # Reject if head noun (last word) is too generic — check both surface and lemma
    last_word = re.sub(r'[^a-zA-Z]', '', words[-1]).lower()
    last_lemma = _nlp(last_word)[0].lemma_.lower() if last_word else ''
    if last_word in _GENERIC_HEADS or last_lemma in _GENERIC_HEADS:
        return True
    # Reject phrases starting with negation (e.g. "not-so-appropriate ...")
    if words[0].lower().startswith('not'):
        return True
    # Reject pure punctuation / symbol phrases
    alphanum = re.sub(r'[^a-zA-Z0-9 ]', '', phrase)
    if len(alphanum.strip()) < 4:
        return True
    # Reject if phrase starts with a quote character
    if phrase.startswith(('"', "'", '\u201c', '\u201d')):
        return True
    # Reject if phrase contains a comma or conjunction (likely two phrases merged)
    if ',' in phrase:
        return True
    if re.search(r'\b(or|and|nor|but)\b', phrase):
        return True
    # Reject if any word is an all-caps abbreviation of 4+ chars (likely an acronym/identifier)
    for w in words:
        w_alpha = re.sub(r'[^a-zA-Z]', '', w)
        if len(w_alpha) >= 4 and w_alpha.isupper():
            return True
    # Short jargon words blocklist (single-letter, abbreviations, code names)
    _JARGON = {
        'buf', 'grp', 'ptr', 'idx', 'pos', 'tmp', 'cnt', 'num', 'var',
        'cfg', 'init', 'iter', 'prev', 'curr', 'mkl', 'isa', 'nza',
        'csr', 'csc', 'bsr', 'bsc', 'nnz',
    }
    for w in words:
        w_alpha = re.sub(r'[^a-zA-Z]', '', w)
        if '-' not in w and len(w_alpha) < 2:
            return True
        # Reject very short purely-lowercase acronyms (3 chars, all consonants)
        if len(w_alpha) <= 3 and w_alpha.lower() in _JARGON:
            return True
        # Reject if any word is in the jargon blocklist
        if w.lower().strip(string.punctuation) in _JARGON:
            return True
    # Reject phrases where the ratio of alpha chars to total chars is very low
    alpha_chars = sum(c.isalpha() for c in phrase)
    if alpha_chars / max(len(phrase), 1) < 0.5:
        return True
    return False


def extract_subphrases(sentences, keyword, title, n=5, all_keywords=None):
    """
    Extract clean noun phrases from the keyword's most relevant sentences.
    Uses spaCy noun chunks scored by semantic similarity to the keyword.
    """
    text = ' '.join(sentences)
    if not text.strip():
        return []

    doc = _nlp(text)

    # Build prefixes from title words for adjectival variant detection
    # e.g. "mitochondria" -> prefix "mitochon" catches "mitochondrial"
    title_prefixes = []
    for w in title.lower().split():
        w_clean = w.strip(string.punctuation)
        if len(w_clean) >= 7:
            title_prefixes.append(w_clean[:7])

    # Words to exclude from sub-phrases:
    #   - the CURRENT keyword's tokens + their lemmas
    #   - title words + their lemmas
    # (We do NOT ban other branch keywords here — that would over-filter)
    skip_tokens = set()

    # Current keyword
    for w in keyword.split():
        w_clean = w.strip(string.punctuation).lower()
        skip_tokens.add(w_clean)
        if '-' not in w_clean:
            tok_doc = _nlp(w_clean)
            for t in tok_doc:
                skip_tokens.add(t.lemma_.lower())

    # Title words and their lemmas
    for w in title.lower().split():
        w_clean = w.strip(string.punctuation)
        if len(w_clean) >= 3:
            skip_tokens.add(w_clean)
            if '-' not in w_clean:
                tok_doc = _nlp(w_clean)
                for t in tok_doc:
                    skip_tokens.add(t.lemma_.lower())

    # Build a secondary (relaxed) skip set: only keyword + title, no cross-keyword filtering
    skip_tokens_strict = set(skip_tokens)  # full set for primary pass
    skip_tokens_relaxed = set()
    for w in keyword.split():
        w_clean = w.strip(string.punctuation).lower()
        skip_tokens_relaxed.add(w_clean)
        if '-' not in w_clean:
            for t in _nlp(w_clean):
                skip_tokens_relaxed.add(t.lemma_.lower())
    for w in title.lower().split():
        w_clean = w.strip(string.punctuation)
        if len(w_clean) >= 3:
            skip_tokens_relaxed.add(w_clean)
            if '-' not in w_clean:
                for t in _nlp(w_clean):
                    skip_tokens_relaxed.add(t.lemma_.lower())

    chunks = Counter()
    chunks_relaxed = Counter()
    for chunk in doc.noun_chunks:
        # Strip leading determiners/articles iteratively
        cleaned = _strip_leading_determiners(chunk.text)
        # Normalize smart quotes/apostrophes
        text_lower = _normalize_apostrophe(cleaned).lower().strip()

        if not _is_bad_phrase(text_lower, skip_tokens_strict):
            chunks[text_lower] += 1
        elif not _is_bad_phrase(text_lower, skip_tokens_relaxed):
            chunks_relaxed[text_lower] += 1

    if not chunks and not chunks_relaxed:
        return []

    # Primary candidates from strict filter; supplement with relaxed if too few
    candidates = [c for c, _ in chunks.most_common(50)]
    if len(candidates) < n * 2:
        relaxed_extras = [c for c, _ in chunks_relaxed.most_common(50)
                          if c not in set(candidates)]
        candidates = candidates + relaxed_extras

    # Score candidates by semantic similarity to the keyword
    kw_emb = _sent_model.encode([keyword], show_progress_bar=False)
    cand_embs = _sent_model.encode(candidates, show_progress_bar=False)
    scored = []
    for i, cand in enumerate(candidates):
        sim = util.cos_sim(cand_embs[i], kw_emb).item()
        # Keep phrases with at least a weak relevance signal
        if 0.15 < sim < 0.92:
            scored.append((cand, sim))

    # Exclude phrases identical to any keyword
    keyword_set = {k.lower() for k in (all_keywords or [])}
    scored = [(p, s) for p, s in scored if p not in keyword_set]

    # Exclude phrases that are morphological variants of the keyword (long common prefix)
    kw_lower = keyword.lower()
    scored = [
        (p, s) for p, s in scored
        if not (common_prefix_len(p, kw_lower) >= min(5, len(kw_lower) - 1))
    ]

    # Exclude phrases that contain a title-derived word (adjectival variants via prefix)
    def _contains_title_variant(phrase):
        for pw in phrase.split():
            pw_clean = pw.strip(string.punctuation).lower()
            if '-' in pw_clean:
                continue  # skip hyphenated compounds
            for pfx in title_prefixes:
                if pw_clean.startswith(pfx) and len(pw_clean) > len(pfx):
                    return True
        return False

    scored = [(p, s) for p, s in scored if not _contains_title_variant(p)]

    # Exclude 2-word phrases that are just [adjective + keyword] or [keyword + noun]
    # where the keyword IS the current branch keyword (already excluded by skip_tokens)
    # or where BOTH words are keywords (useless combo)
    def _all_keywords(phrase):
        pw = [w.strip(string.punctuation).lower() for w in phrase.split()]
        if len(pw) != 2:
            return False
        kw_words = set()
        for k in (all_keywords or []):
            kw_words.update(k.lower().split())
        # Filter only if ALL words are keywords (not just one)
        return all(w in kw_words for w in pw if '-' not in w)

    scored = [(p, s) for p, s in scored if not _all_keywords(p)]

    scored.sort(key=lambda x: x[1], reverse=True)
    phrases = [p for p, _ in scored[:n * 4]]
    return deduplicate_phrases(phrases)[:n]


# ── Main pipeline ──────────────────────────────────────────────────────────────

def build_mind_map(text, title):
    sentences = [s.strip() for s in sent_tokenize(text) if len(s.split()) >= 5]
    keywords = extract_keywords(text, title)
    if not keywords:
        return {}

    result = {}
    for kw in keywords:
        top_sents = top_sentences_for_keyword(sentences, kw, k=30)
        result[kw] = extract_subphrases(top_sents, kw, title, n=5, all_keywords=keywords)

    # Count total phrases to determine if document is too small for aggressive dedup
    total_phrases = sum(len(v) for v in result.values())
    target_n = 5  # target sub-phrases per branch
    # min_phrases_to_spare: only dedup if branch has more than this many phrases
    min_spare = max(2, target_n // 2)

    kw_embs = {kw: _sent_model.encode([kw], show_progress_bar=False) for kw in keywords}

    # Cross-branch dedup pass 1: exact match
    # Keep phrase only in the branch where it has the highest similarity
    phrase_to_branches = {}
    for kw, phrases in result.items():
        for p in phrases:
            phrase_to_branches.setdefault(p, []).append(kw)

    for phrase, branches in phrase_to_branches.items():
        if len(branches) <= 1:
            continue
        p_emb = _sent_model.encode([phrase], show_progress_bar=False)
        best = max(branches, key=lambda kw: util.cos_sim(p_emb, kw_embs[kw]).item())
        for kw in branches:
            # Remove from non-best branch only if that branch has enough phrases (> 1)
            if kw != best and len(result[kw]) > 1:
                result[kw] = [p for p in result[kw] if p != phrase]

    # Cross-branch dedup pass 2: semantic near-duplicates across branches
    # (e.g. "visual representation" vs "visual representations")
    # Only when document has enough variety (not a tiny focused doc)
    if total_phrases > len(keywords) * 3:
        all_phrases_flat = [(kw, p) for kw, phrases in result.items() for p in phrases]
        if len(all_phrases_flat) > 1:
            all_p = [p for _, p in all_phrases_flat]
            all_embs = _sent_model.encode(all_p, show_progress_bar=False)
            to_remove = set()
            for i in range(len(all_p)):
                if i in to_remove:
                    continue
                for j in range(i + 1, len(all_p)):
                    if j in to_remove:
                        continue
                    kw_i, kw_j = all_phrases_flat[i][0], all_phrases_flat[j][0]
                    if kw_i == kw_j:
                        continue  # same branch — handled by within-branch dedup
                    sim = util.cos_sim(all_embs[i], all_embs[j]).item()
                    if sim > 0.88:  # very similar across branches
                        sim_i = util.cos_sim(all_embs[i], kw_embs[kw_i]).item()
                        sim_j = util.cos_sim(all_embs[j], kw_embs[kw_j]).item()
                        if sim_i >= sim_j and len(result[kw_j]) > min_spare:
                            to_remove.add(j)
                        elif sim_j > sim_i and len(result[kw_i]) > min_spare:
                            to_remove.add(i)

            for idx in to_remove:
                kw, phrase = all_phrases_flat[idx]
                result[kw] = [p for p in result[kw] if p != phrase]

    return result


def nodes(title, d):
    node_list = {"1": {"id": 1, "label": title}}
    node_id = 2
    for key in d:
        curr = node_id
        node_list[str(curr)] = {"id": curr, "label": key, "parent": 1}
        node_id += 1
        for phrase in d[key]:
            label = phrase if len(phrase) <= 50 else phrase[:47] + '...'
            node_list[str(node_id)] = {"id": node_id, "label": label, "parent": curr}
            node_id += 1
    return node_list


# ── Flask app ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/saveDoc', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.docx', '.pdf', '.txt'):
        return jsonify({"error": "Unsupported file type"}), 400

    tmp_path = f"/tmp/upload{ext}"
    file.save(tmp_path)

    raw = extract(tmp_path)
    if not raw.strip():
        return jsonify({"error": "Could not extract text from file"}), 400

    title = next((l.strip() for l in raw.split('\n') if l.strip()), "Document")[:80]
    data = nodes(title, build_mind_map(raw, title))
    print(data)

    with open("../src/Data/data.json", "w") as f:
        json.dump(data, f)

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=False, port=5002)
