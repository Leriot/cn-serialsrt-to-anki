#!/usr/bin/env python3
"""
CC-CEDICT Dictionary Manager
Downloads and parses CC-CEDICT for local lookups
"""

import os
import gzip
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


class CEDICTParser:
    """Parse and query CC-CEDICT dictionary."""
    
    CEDICT_URL = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    
    def __init__(self, dict_path: str = "cedict_ts.u8"):
        self.dict_path = dict_path
        self.entries: Dict[str, List[Tuple[str, str, str]]] = {}  # simplified -> [(traditional, pinyin, definition)]
    
    def download(self):
        """Download CC-CEDICT from MDBG."""
        print(f"Downloading CC-CEDICT from {self.CEDICT_URL}...")
        
        gz_path = self.dict_path + ".gz"
        
        # Download compressed file
        urllib.request.urlretrieve(self.CEDICT_URL, gz_path)
        print(f"Downloaded to {gz_path}")
        
        # Decompress
        print(f"Decompressing to {self.dict_path}...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(self.dict_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Clean up compressed file
        os.remove(gz_path)
        print("Download complete!")
    
    def load(self):
        """Load and parse CC-CEDICT file."""
        if not os.path.exists(self.dict_path):
            print(f"Dictionary file not found at {self.dict_path}")
            print("Downloading...")
            self.download()
        
        print(f"Loading dictionary from {self.dict_path}...")
        
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse format: 传统 简体 [pin1 yin1] /definition1/definition2/
                parts = line.split(' ', 2)
                if len(parts) < 3:
                    continue
                
                traditional = parts[0]
                simplified = parts[1]
                
                # Extract pinyin and definitions
                rest = parts[2]
                if not rest.startswith('['):
                    continue
                
                pinyin_end = rest.find(']')
                if pinyin_end == -1:
                    continue
                
                pinyin = rest[1:pinyin_end]
                definitions_raw = rest[pinyin_end+1:].strip()
                
                # Parse definitions (between slashes)
                definitions = [d.strip() for d in definitions_raw.split('/') if d.strip()]
                definition = '; '.join(definitions)
                
                # Store entry
                if simplified not in self.entries:
                    self.entries[simplified] = []
                
                self.entries[simplified].append((traditional, pinyin, definition))
        
        print(f"Loaded {len(self.entries)} unique simplified words")
        total_entries = sum(len(v) for v in self.entries.values())
        print(f"Total entries (including variants): {total_entries}")
    
    def lookup(self, word: str, prefer_pinyin: str = None) -> List[Dict[str, str]]:
        """
        Look up a word in the dictionary.
        
        Args:
            word: Simplified Chinese word
            prefer_pinyin: If provided, prioritize entries matching this pinyin
        
        Returns:
            List of dictionaries with keys: traditional, pinyin, definition
        """
        if word not in self.entries:
            return []
        
        results = []
        entries = self.entries[word]
        
        # If pinyin preference given, sort matching entries first
        if prefer_pinyin:
            prefer_normalized = prefer_pinyin.lower().replace(' ', '').replace('5', '')
            
            def pinyin_match_score(entry):
                entry_pinyin = entry[1].lower().replace(' ', '').replace('5', '')
                if entry_pinyin == prefer_normalized:
                    return 0  # Exact match
                elif prefer_normalized in entry_pinyin or entry_pinyin in prefer_normalized:
                    return 1  # Partial match
                else:
                    return 2  # No match
            
            entries = sorted(entries, key=pinyin_match_score)
        
        for trad, pinyin, definition in entries:
            results.append({
                'traditional': trad,
                'pinyin': pinyin,
                'definition': definition
            })
        
        return results
    
    def lookup_first(self, word: str, prefer_pinyin: str = None) -> str:
        """
        Get the first (most relevant) definition for a word.
        
        Returns:
            Formatted string: "pinyin: definition" or empty string if not found
        """
        results = self.lookup(word, prefer_pinyin)
        if not results:
            return ""
        
        first = results[0]
        
        # Format: pinyin: definition
        # Return all definitions, separated by newlines
        formatted_results = []
        for r in results:
            formatted_results.append(f"{r['pinyin']}: {r['definition']}")
        
        return "\n".join(formatted_results)


def main():
    """Test/demo the dictionary."""
    import sys
    
    # Initialize dictionary
    dict_path = "cedict_ts.u8"
    if len(sys.argv) > 1:
        dict_path = sys.argv[1]
    
    cedict = CEDICTParser(dict_path)
    cedict.load()
    
    # Test lookups
    test_words = ['你好', '中国', '学习', '苏']
    
    print("\nTest lookups:")
    for word in test_words:
        results = cedict.lookup(word)
        print(f"\n{word}:")
        for r in results:
            print(f"  {r['pinyin']}: {r['definition']}")


if __name__ == "__main__":
    main()
