#!/usr/bin/env python3
"""
Enhanced Nirvana in Fire Sentence Extractor for Anki
=====================================================
NEW FEATURES:
- DeepL API translation for example sentences
- CC-CEDICT definitions for vocabulary words
- Extended Anki TSV output with translation and definition fields

1. Parses CTA word list, merges duplicates (case-insensitive pinyin)
2. Finds example sentences from subtitle files
3. Looks up definitions in CC-CEDICT
4. Translates sentences via DeepL API
5. Outputs Anki-ready TSV with all fields
"""

import re
import os
import time
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# OpenCC for proper simplified↔traditional conversion
try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False
    print("Warning: opencc not installed. Install with: pip install opencc-python-reimplemented")
    print("Traditional conversion will be disabled.")

# DeepL for translations
try:
    import deepl
    DEEPL_AVAILABLE = True
except ImportError:
    DEEPL_AVAILABLE = False
    print("Warning: deepl not installed. Install with: pip install deepl")
    print("Translation will be disabled.")

# CC-CEDICT for definitions
from cedict_manager import CEDICTParser


@dataclass
class WordEntry:
    """Represents a deduplicated word with all its info."""
    simplified: str
    traditional: str  # Primary traditional form
    traditional_variants: List[str] = field(default_factory=list)
    pinyin: str = ""
    pinyin_variants: List[str] = field(default_factory=list)
    is_name: bool = False  # True if any pinyin variant was capitalized
    example_sentence_simplified: str = ""
    example_sentence_traditional: str = ""
    example_sentence_translation: str = ""  # NEW: DeepL translation
    definition: str = ""  # NEW: CC-CEDICT definition
    episode: str = ""
    line_number: int = 0

# Common traditional forms that should be preferred over rare variants
PREFERRED_TRADITIONAL = {
    '囌': '蘇',  # su - 蘇 is standard
    '叡': '睿',  # rui - both acceptable but 睿 more common
}


def parse_cta_export(filepath: str) -> Dict[str, WordEntry]:
    """
    Parse Chinese Text Analyzer export and merge duplicates.
    
    Format: simplified	simplified[Traditional]	pinyin
    Example: 苏	苏[蘇]	Sū
    """
    words = {}  # Key: simplified form
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) < 3:
                # Handle entries with missing pinyin (like 梅长苏)
                if len(parts) >= 2:
                    simplified = parts[0]
                    bracket_part = parts[1]
                    pinyin = ""
                else:
                    continue
            else:
                simplified = parts[0]
                bracket_part = parts[1]
                pinyin = parts[2]
            
            # Parse the bracket notation: simplified[Traditional]
            match = re.match(r'([^\[]*)\[([^\]]*)\]', bracket_part)
            if match:
                traditional = match.group(2) if match.group(2) else simplified
            else:
                traditional = simplified
            
            # Check if this is a proper noun (capitalized pinyin)
            is_name = bool(pinyin and pinyin[0].isupper())
            
            # Normalize pinyin for comparison (lowercase)
            pinyin_normalized = pinyin.lower().strip()
            
            # Merge with existing entry or create new
            if simplified in words:
                entry = words[simplified]
                # Add traditional variant if different
                if traditional and traditional != entry.traditional:
                    if traditional not in entry.traditional_variants:
                        entry.traditional_variants.append(traditional)
                    # Check if new traditional is preferred over current
                    if entry.traditional in PREFERRED_TRADITIONAL:
                        # Swap: move current to variants, use the common one
                        if PREFERRED_TRADITIONAL[entry.traditional] == traditional:
                            entry.traditional_variants.append(entry.traditional)
                            entry.traditional = traditional
                        elif traditional in PREFERRED_TRADITIONAL.values():
                            entry.traditional_variants.append(entry.traditional)
                            entry.traditional = traditional
                # Add pinyin variant if different
                if pinyin_normalized and pinyin_normalized != entry.pinyin.lower():
                    if pinyin_normalized not in [p.lower() for p in entry.pinyin_variants]:
                        entry.pinyin_variants.append(pinyin)
                # Mark as name if any variant is capitalized
                if is_name:
                    entry.is_name = True
            else:
                # Check if initial traditional should be swapped
                if traditional in PREFERRED_TRADITIONAL:
                    # Use preferred form instead
                    preferred = PREFERRED_TRADITIONAL[traditional]
                    # We'll pick it up when we see it
                    pass
                
                words[simplified] = WordEntry(
                    simplified=simplified,
                    traditional=traditional if traditional else simplified,
                    pinyin=pinyin,
                    is_name=is_name
                )
    
    # Post-process: swap rare traditional forms with common ones
    for simplified, entry in words.items():
        if entry.traditional in PREFERRED_TRADITIONAL:
            preferred = PREFERRED_TRADITIONAL[entry.traditional]
            # Check if preferred is in variants
            if preferred in entry.traditional_variants:
                entry.traditional_variants.remove(preferred)
                entry.traditional_variants.append(entry.traditional)
                entry.traditional = preferred
        
        # Clean up: remove primary from variants list if it's there
        if entry.traditional in entry.traditional_variants:
            entry.traditional_variants.remove(entry.traditional)
        
        # Remove duplicates from variants
        entry.traditional_variants = list(dict.fromkeys(entry.traditional_variants))
    
    return words


def extract_srt_lines(srt_folder: str) -> List[Tuple[str, str, int, str]]:
    """
    Extract all lines from SRT files with metadata.
    Returns: List of (text, episode_name, line_number, raw_line)
    """
    lines = []
    srt_path = Path(srt_folder)
    
    # Find all subtitle files
    srt_files = sorted(srt_path.glob('*'))
    
    for srt_file in srt_files:
        if not srt_file.is_file():
            continue
            
        episode_name = srt_file.stem
        
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(srt_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            except Exception as e:
                print(f"Could not read {srt_file}: {e}")
                continue
        
        file_lines = content.split('\n')
        line_num = 0
        
        for raw_line in file_lines:
            raw_line = raw_line.strip()
            
            # Skip empty, numbers, timestamps
            if not raw_line:
                continue
            if re.match(r'^\d+$', raw_line):
                continue
            if re.match(r'^\d{2}:\d{2}:\d{2}', raw_line):
                continue
            
            # Clean formatting tags
            clean_line = re.sub(r'<[^>]+>', '', raw_line)
            clean_line = re.sub(r'\{[^}]+\}', '', clean_line)
            clean_line = clean_line.strip()
            
            if clean_line and len(clean_line) >= 2:
                line_num += 1
                lines.append((clean_line, episode_name, line_num, raw_line))
    
    return lines


def simplified_to_traditional(text: str, converter=None) -> str:
    """
    Convert simplified Chinese text to traditional using OpenCC.
    
    Args:
        text: Simplified Chinese text
        converter: OpenCC converter instance (created if None)
    
    Returns:
        Traditional Chinese text
    """
    if not OPENCC_AVAILABLE:
        return text  # Return unchanged if OpenCC not available
    
    if converter is None:
        converter = OpenCC('s2t')  # Simplified to Traditional (standard)
    
    return converter.convert(text)


def lookup_definitions(words: Dict[str, WordEntry], cedict: CEDICTParser):
    """
    Look up definitions for all words in CC-CEDICT.
    
    Args:
        words: Dictionary of word entries
        cedict: Loaded CC-CEDICT parser
    """
    print("\nLooking up definitions in CC-CEDICT...")
    found_count = 0
    
    for simplified, entry in words.items():
        # Look up with pinyin preference to get best match
        definition = cedict.lookup_first(simplified, prefer_pinyin=entry.pinyin)
        
        if definition:
            entry.definition = definition
            found_count += 1
    
    print(f"Found definitions for {found_count}/{len(words)} words")


def translate_sentences_deepl(
    words: Dict[str, WordEntry],
    api_key: str,
    target_lang: str = "EN-US",
    batch_size: int = 50,
    delay: float = 0.5
):
    """
    Translate example sentences using DeepL API.
    
    Args:
        words: Dictionary of word entries
        api_key: DeepL API key
        target_lang: Target language code (EN-US, CS, etc.)
        batch_size: Number of translations per batch
        delay: Delay between batches to respect rate limits
    """
    if not DEEPL_AVAILABLE:
        print("DeepL not available, skipping translations")
        return
    
    print(f"\nTranslating sentences to {target_lang} using DeepL API...")
    
    # Initialize DeepL translator
    translator = deepl.Translator(api_key)
    
    # Collect sentences to translate
    to_translate = []
    entries_with_sentences = []
    
    for entry in words.values():
        if entry.example_sentence_simplified:
            to_translate.append(entry.example_sentence_simplified)
            entries_with_sentences.append(entry)
    
    if not to_translate:
        print("No sentences to translate")
        return
    
    print(f"Translating {len(to_translate)} sentences...")
    
    # Translate in batches
    translated_count = 0
    
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i+batch_size]
        batch_entries = entries_with_sentences[i:i+batch_size]
        
        try:
            # Translate batch
            results = translator.translate_text(
                batch,
                source_lang="ZH",
                target_lang=target_lang
            )
            
            # Handle single result vs list of results
            if not isinstance(results, list):
                results = [results]
            
            # Store translations
            for entry, result in zip(batch_entries, results):
                entry.example_sentence_translation = result.text
                translated_count += 1
            
            print(f"  Translated {min(i+batch_size, len(to_translate))}/{len(to_translate)}")
            
            # Rate limiting delay
            if i + batch_size < len(to_translate):
                time.sleep(delay)
        
        except Exception as e:
            print(f"  Error translating batch {i//batch_size + 1}: {e}")
            # Continue with next batch
            continue
    
    print(f"Successfully translated {translated_count}/{len(to_translate)} sentences")


def find_example_sentences(
    words: Dict[str, WordEntry], 
    srt_lines: List[Tuple[str, str, int, str]],
    min_length: int = 4,
    combine_short: bool = True
) -> Dict[str, WordEntry]:
    """
    Find first occurrence of each word in a suitable sentence.
    
    Args:
        words: Dictionary of word entries
        srt_lines: List of (text, episode, line_num, raw) tuples
        min_length: Minimum sentence length to consider
        combine_short: If True, combine consecutive short lines
    """
    # Pre-process: combine short consecutive lines
    processed_lines = []
    
    if combine_short:
        i = 0
        while i < len(srt_lines):
            text, episode, line_num, raw = srt_lines[i]
            
            # If line is short, try to combine with next
            combined = text
            combined_count = 1
            
            while len(combined) < min_length * 2 and i + combined_count < len(srt_lines):
                next_text, next_ep, _, _ = srt_lines[i + combined_count]
                # Only combine if same episode
                if next_ep == episode:
                    combined = combined + next_text
                    combined_count += 1
                else:
                    break
            
            if combined_count > 1 and len(combined) > len(text):
                processed_lines.append((combined, episode, line_num, f"[combined {combined_count} lines]"))
            
            processed_lines.append((text, episode, line_num, raw))
            i += 1
    else:
        processed_lines = srt_lines
    
    # Create OpenCC converter once for efficiency
    converter = None
    if OPENCC_AVAILABLE:
        converter = OpenCC('s2t')
    
    # Find sentences for each word
    found_count = 0
    
    for simplified, entry in words.items():
        if entry.example_sentence_simplified:
            continue  # Already found
        
        for text, episode, line_num, _ in processed_lines:
            if simplified in text and len(text) >= min_length:
                entry.example_sentence_simplified = text
                entry.example_sentence_traditional = simplified_to_traditional(text, converter)
                entry.episode = episode
                entry.line_number = line_num
                found_count += 1
                break
    
    print(f"Found example sentences for {found_count}/{len(words)} words")
    return words


def create_cloze(sentence: str, word: str) -> str:
    """Create Anki cloze deletion format."""
    return sentence.replace(word, f"{{{{c1::{word}}}}}", 1)


def export_for_anki(
    words: Dict[str, WordEntry], 
    output_file: str,
    include_no_sentence: bool = False
):
    """
    Export to TSV format for Anki import.
    
    Fields:
    1. Cloze (Simplified)
    2. Cloze (Traditional)
    3. Target Word (Simplified)
    4. Target Word (Traditional)
    5. Pinyin
    6. Pinyin Variants (if multiple readings)
    7. Is Name (yes/no)
    8. Full Sentence (Simplified)
    9. Full Sentence (Traditional)
    10. Translation (NEW)
    11. Definition (NEW)
    12. Episode
    """
    # Create converter for traditional cloze words
    converter = None
    if OPENCC_AVAILABLE:
        converter = OpenCC('s2t')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("cloze_simplified\tcloze_traditional\tword_simplified\tword_traditional\t")
        f.write("pinyin\tpinyin_variants\tis_name\t")
        f.write("sentence_simplified\tsentence_traditional\ttranslation\tdefinition\tepisode\n")
        
        exported = 0
        skipped = 0
        
        for simplified, entry in words.items():
            if not entry.example_sentence_simplified:
                if include_no_sentence:
                    # Still export but with empty sentence
                    pass
                else:
                    skipped += 1
                    continue
            
            # Convert word to traditional using OpenCC (same as sentence conversion)
            word_trad_for_cloze = simplified_to_traditional(simplified, converter)
            
            # Create cloze versions
            cloze_simp = create_cloze(entry.example_sentence_simplified, simplified)
            cloze_trad = create_cloze(
                entry.example_sentence_traditional, 
                word_trad_for_cloze  # Use OpenCC-converted word, not word list
            )
            
            # Combine pinyin variants
            all_pinyin = [entry.pinyin] + entry.pinyin_variants
            pinyin_main = entry.pinyin
            pinyin_vars = "; ".join(entry.pinyin_variants) if entry.pinyin_variants else ""
            
            # Format traditional: use OpenCC conversion, show word list variants if different
            trad_display = word_trad_for_cloze
            all_variants = []
            # Add word list traditional if different from OpenCC
            if entry.traditional and entry.traditional != word_trad_for_cloze:
                all_variants.append(entry.traditional)
            # Add other variants from word list
            for var in entry.traditional_variants:
                if var != word_trad_for_cloze and var not in all_variants:
                    all_variants.append(var)
            if all_variants:
                trad_display += f" ({'/'.join(all_variants)})"
            
            # is_name: empty string if not a name (so Anki {{#is_name}} works correctly)
            row = [
                cloze_simp,
                cloze_trad,
                simplified,
                trad_display,
                pinyin_main,
                pinyin_vars,
                "yes" if entry.is_name else "",  # Empty = Anki treats as false
                entry.example_sentence_simplified,
                entry.example_sentence_traditional,
                entry.example_sentence_translation,  # NEW
                entry.definition,  # NEW
                entry.episode
            ]
            
            f.write('\t'.join(row) + '\n')
            exported += 1
        
        print(f"Exported {exported} words to {output_file}")
        if skipped:
            print(f"Skipped {skipped} words without example sentences")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract sentences for Anki flashcards with DeepL translation and CC-CEDICT definitions'
    )
    parser.add_argument('wordlist', help='CTA export file (TSV)')
    parser.add_argument('subtitles', help='Folder containing subtitle files')
    parser.add_argument('-o', '--output', default='anki_export.tsv', help='Output TSV file')
    parser.add_argument('--min-length', type=int, default=4, help='Minimum sentence length')
    parser.add_argument('--include-empty', action='store_true', help='Include words without sentences')
    
    # NEW: DeepL options
    parser.add_argument('--deepl-key', help='DeepL API key (or set DEEPL_API_KEY env var)')
    parser.add_argument('--target-lang', default='EN-US', help='DeepL target language (default: EN-US)')
    parser.add_argument('--no-translate', action='store_true', help='Skip DeepL translation')
    
    # NEW: CC-CEDICT options
    parser.add_argument('--cedict-path', default='cedict_ts.u8', help='Path to CC-CEDICT file')
    parser.add_argument('--no-definitions', action='store_true', help='Skip CC-CEDICT definitions')
    
    args = parser.parse_args()
    
    print(f"Loading word list from {args.wordlist}...")
    words = parse_cta_export(args.wordlist)
    print(f"Loaded {len(words)} unique words (after merging duplicates)")
    
    # Show some stats
    names = sum(1 for w in words.values() if w.is_name)
    multi_reading = sum(1 for w in words.values() if w.pinyin_variants)
    print(f"  - {names} proper nouns/names")
    print(f"  - {multi_reading} words with multiple readings")
    
    print(f"\nLoading subtitles from {args.subtitles}...")
    srt_lines = extract_srt_lines(args.subtitles)
    print(f"Loaded {len(srt_lines)} subtitle lines")
    
    print(f"\nFinding example sentences (min length: {args.min_length})...")
    words = find_example_sentences(words, srt_lines, min_length=args.min_length)
    
    # NEW: Look up definitions in CC-CEDICT
    if not args.no_definitions:
        try:
            cedict = CEDICTParser(args.cedict_path)
            cedict.load()
            lookup_definitions(words, cedict)
        except Exception as e:
            print(f"Error loading CC-CEDICT: {e}")
            print("Continuing without definitions...")
    
    # NEW: Translate sentences with DeepL
    if not args.no_translate:
        api_key = args.deepl_key or os.environ.get('DEEPL_API_KEY')
        
        if api_key:
            try:
                translate_sentences_deepl(words, api_key, target_lang=args.target_lang)
            except Exception as e:
                print(f"Error during translation: {e}")
                print("Continuing without translations...")
        else:
            print("\nSkipping translation: No DeepL API key provided")
            print("Set --deepl-key or DEEPL_API_KEY environment variable")
    
    print(f"\nExporting to {args.output}...")
    export_for_anki(words, args.output, include_no_sentence=args.include_empty)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
