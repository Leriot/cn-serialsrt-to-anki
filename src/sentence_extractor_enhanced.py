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


class WordManager:
    """Manages word entries, deduplication, and processing."""
    
    def __init__(self):
        self.words: Dict[str, WordEntry] = {}
        self.converter = OpenCC('s2t') if OPENCC_AVAILABLE else None

    def add_word(self, simplified: str, traditional: str, pinyin: str):
        """Add or update a word entry."""
        # Sanitize inputs
        simplified = simplified.strip()
        traditional = traditional.strip()
        pinyin = pinyin.strip()
        
        # Check if this is a proper noun (capitalized pinyin)
        is_name = bool(pinyin and pinyin[0].isupper())
        
        # Normalize pinyin for comparison (lowercase)
        pinyin_normalized = pinyin.lower()
        
        if simplified in self.words:
            entry = self.words[simplified]
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
            
            self.words[simplified] = WordEntry(
                simplified=simplified,
                traditional=traditional if traditional else simplified,
                pinyin=pinyin,
                is_name=is_name
            )

    def post_process(self):
        """Clean up variants and preferred forms."""
        for simplified, entry in self.words.items():
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

    def load_cta_export(self, filepath: str):
        """Parse Chinese Text Analyzer export."""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 3:
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
                
                self.add_word(simplified, traditional, pinyin)
        
        self.post_process()

    def find_sentences(self, srt_lines: List[Tuple[str, str, int, str]], min_length: int = 4):
        """Find example sentences."""
        found_count = 0
        for simplified, entry in self.words.items():
            if entry.example_sentence_simplified:
                continue
            
            for text, episode, line_num, _ in srt_lines:
                if simplified in text and len(text) >= min_length:
                    entry.example_sentence_simplified = text
                    entry.example_sentence_traditional = simplified_to_traditional(text, self.converter)
                    entry.episode = episode
                    entry.line_number = line_num
                    found_count += 1
                    break
        print(f"Found example sentences for {found_count}/{len(self.words)} words")

    def lookup_definitions(self, cedict: CEDICTParser):
        """Look up definitions."""
        print("\nLooking up definitions in CC-CEDICT...")
        found_count = 0
        for simplified, entry in self.words.items():
            # Lookup all matching entries
            results = cedict.lookup(simplified, prefer_pinyin=entry.pinyin)
            
            if results:
                # Filter results to match the word's pinyin if possible
                # This avoids showing definitions for different pronunciations
                matching_results = []
                target_pinyin = entry.pinyin.lower().replace(" ", "")
                
                for r in results:
                    r_pinyin = r['pinyin'].lower().replace(" ", "")
                    # Allow partial match or if target is empty
                    if not target_pinyin or target_pinyin in r_pinyin or r_pinyin in target_pinyin:
                        matching_results.append(r)
                
                # If no pinyin match found, fall back to all results
                if not matching_results:
                    matching_results = results
                
                # Extract just the definitions (no pinyin)
                definitions = []
                for r in matching_results:
                    definitions.append(r['definition'])
                
                # Join with <br> for Anki
                entry.definition = "<br>".join(definitions)
                found_count += 1
                
        print(f"Found definitions for {found_count}/{len(self.words)} words")

    def translate_sentences(self, api_key: str, target_lang: str = "EN-US", batch_size: int = 50):
        """Translate sentences using DeepL."""
        if not DEEPL_AVAILABLE:
            print("DeepL not available.")
            return

        print(f"\nTranslating sentences to {target_lang}...")
        translator = deepl.Translator(api_key)
        
        to_translate = []
        entries_with_sentences = []
        
        for entry in self.words.values():
            if entry.example_sentence_simplified:
                to_translate.append(entry.example_sentence_simplified)
                entries_with_sentences.append(entry)
        
        if not to_translate:
            return

        print(f"Translating {len(to_translate)} sentences...")
        translated_count = 0
        
        for i in range(0, len(to_translate), batch_size):
            batch = to_translate[i:i+batch_size]
            batch_entries = entries_with_sentences[i:i+batch_size]
            
            try:
                results = translator.translate_text(batch, source_lang="ZH", target_lang=target_lang)
                if not isinstance(results, list):
                    results = [results]
                
                for entry, result in zip(batch_entries, results):
                    entry.example_sentence_translation = result.text
                    translated_count += 1
                
                print(f"  Translated {min(i+batch_size, len(to_translate))}/{len(to_translate)}")
                if i + batch_size < len(to_translate):
                    time.sleep(0.5)
            except Exception as e:
                print(f"  Error translating batch: {e}")
        
        print(f"Successfully translated {translated_count}/{len(to_translate)} sentences")

    def export_anki(self, output_file: str, include_no_sentence: bool = False):
        """Export to TSV with sanitization."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            headers = [
                "cloze_simplified", "cloze_traditional", "word_simplified", "word_traditional",
                "pinyin", "pinyin_variants", "is_name", "translation", "definition", "episode"
            ]
            f.write('\t'.join(headers) + '\n')
            
            exported = 0
            skipped = 0
            
            for simplified, entry in self.words.items():
                if not entry.example_sentence_simplified and not include_no_sentence:
                    skipped += 1
                    continue
                
                # Prepare fields
                word_trad_for_cloze = simplified_to_traditional(simplified, self.converter)
                cloze_simp = create_cloze(entry.example_sentence_simplified, simplified)
                cloze_trad = create_cloze(entry.example_sentence_traditional, word_trad_for_cloze)
                
                trad_display = word_trad_for_cloze
                all_variants = []
                if entry.traditional and entry.traditional != word_trad_for_cloze:
                    all_variants.append(entry.traditional)
                for var in entry.traditional_variants:
                    if var != word_trad_for_cloze and var not in all_variants:
                        all_variants.append(var)
                if all_variants:
                    trad_display += f" ({'/'.join(all_variants)})"
                
                pinyin_vars = "; ".join(entry.pinyin_variants) if entry.pinyin_variants else ""
                
                # Sanitize fields (remove tabs and newlines)
                def sanitize(s):
                    return str(s).replace('\t', ' ').replace('\n', '<br>').strip()
                
                row = [
                    sanitize(cloze_simp),
                    sanitize(cloze_trad),
                    sanitize(simplified),
                    sanitize(trad_display),
                    sanitize(entry.pinyin),
                    sanitize(pinyin_vars),
                    "yes" if entry.is_name else "",
                    sanitize(entry.example_sentence_translation),
                    sanitize(entry.definition), # Definitions might have newlines, replace with <br>
                    sanitize(entry.episode)
                ]
                
                f.write('\t'.join(row) + '\n')
                exported += 1
            
            print(f"Exported {exported} words to {output_file}")
            if skipped:
                print(f"Skipped {skipped} words without example sentences")


def extract_srt_lines(srt_folder: str) -> List[Tuple[str, str, int, str]]:
    """Extract and sanitize SRT lines."""
    lines = []
    srt_path = Path(srt_folder)
    
    for srt_file in sorted(srt_path.glob('*')):
        if not srt_file.is_file():
            continue
        
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
        
        line_num = 0
        for raw_line in content.split('\n'):
            raw_line = raw_line.strip()
            if not raw_line or re.match(r'^\d+$', raw_line) or re.match(r'^\d{2}:\d{2}:\d{2}', raw_line):
                continue
            
            # Clean and sanitize
            clean_line = re.sub(r'<[^>]+>', '', raw_line)
            clean_line = re.sub(r'\{[^}]+\}', '', clean_line)
            clean_line = clean_line.replace('\t', ' ').strip() # Remove tabs
            
            if clean_line and len(clean_line) >= 2:
                line_num += 1
                lines.append((clean_line, srt_file.stem, line_num, raw_line))
    
    return lines


def simplified_to_traditional(text: str, converter=None) -> str:
    """Convert simplified to traditional."""
    if not OPENCC_AVAILABLE:
        return text
    if converter is None:
        converter = OpenCC('s2t')
    return converter.convert(text)


def create_cloze(sentence: str, word: str) -> str:
    """Create Anki cloze deletion."""
    return sentence.replace(word, f"{{{{c1::{word}}}}}", 1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract sentences for Anki flashcards')
    parser.add_argument('wordlist', help='CTA export file (TSV)')
    parser.add_argument('subtitles', help='Folder containing subtitle files')
    parser.add_argument('-o', '--output', default='anki_export.tsv', help='Output TSV file')
    parser.add_argument('--min-length', type=int, default=4, help='Minimum sentence length')
    parser.add_argument('--include-empty', action='store_true', help='Include words without sentences')
    parser.add_argument('--deepl-key', help='DeepL API key')
    parser.add_argument('--target-lang', default='EN-US', help='DeepL target language')
    parser.add_argument('--no-translate', action='store_true', help='Skip DeepL translation')
    parser.add_argument('--cedict-path', default='cedict_ts.u8', help='Path to CC-CEDICT file')
    parser.add_argument('--no-definitions', action='store_true', help='Skip CC-CEDICT definitions')
    
    args = parser.parse_args()
    
    manager = WordManager()
    
    print(f"Loading word list from {args.wordlist}...")
    manager.load_cta_export(args.wordlist)
    print(f"Loaded {len(manager.words)} unique words")
    
    print(f"\nLoading subtitles from {args.subtitles}...")
    srt_lines = extract_srt_lines(args.subtitles)
    print(f"Loaded {len(srt_lines)} subtitle lines")
    
    print(f"\nFinding example sentences...")
    manager.find_sentences(srt_lines, min_length=args.min_length)
    
    if not args.no_definitions:
        try:
            cedict = CEDICTParser(args.cedict_path)
            cedict.load()
            manager.lookup_definitions(cedict)
        except Exception as e:
            print(f"Error loading CC-CEDICT: {e}")
    
    if not args.no_translate:
        api_key = args.deepl_key or os.environ.get('DEEPL_API_KEY')
        if api_key:
            manager.translate_sentences(api_key, target_lang=args.target_lang)
        else:
            print("\nSkipping translation: No DeepL API key provided")
    
    print(f"\nExporting to {args.output}...")
    manager.export_anki(args.output, include_no_sentence=args.include_empty)
    print("\nDone!")


if __name__ == "__main__":
    main()
