#!/usr/bin/env python3
"""
Automated Batch Processor for Chinese Subtitle Learning
========================================================
Automates the complete workflow:
1. Merge SRT files
2. Wait for user to process in Chinese Text Analyzer
3. Generate Anki cards with translations and definitions

Usage:
    python batch_process.py config.json
"""

import json
import os
import sys
from pathlib import Path
import subprocess


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_merge_srt(config: dict):
    """Step 1: Merge SRT files."""
    print("=" * 60)
    print("STEP 1: Merging SRT Files")
    print("=" * 60)
    
    subtitles_folder = config['subtitles_folder']
    merged_output = config.get('merged_output', 'merged_subtitles.txt')
    
    if not os.path.exists(subtitles_folder):
        print(f"Error: Subtitles folder not found: {subtitles_folder}")
        return False
    
    # Get path to merge_srt.py in the same directory
    script_dir = Path(__file__).parent
    merge_script = script_dir / "merge_srt.py"

    cmd = [
        'python', str(merge_script),
        subtitles_folder,
        merged_output
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✓ Merged subtitles saved to: {merged_output}")
        print(f"✓ With episode markers: {Path(merged_output).stem}_with_episodes.txt")
        return True
    else:
        print("\n✗ Error merging SRT files")
        return False


def wait_for_cta_export(config: dict):
    """Step 2: Wait for user to process in Chinese Text Analyzer."""
    print("\n" + "=" * 60)
    print("STEP 2: Process in Chinese Text Analyzer")
    print("=" * 60)
    
    merged_output = config.get('merged_output', 'merged_subtitles.txt')
    wordlist_output = config.get('wordlist_output', 'wordlist.tsv')
    
    print(f"\nNow:")
    print(f"1. Open {merged_output} in Chinese Text Analyzer")
    print(f"2. Review and select words to learn")
    print(f"3. Export word list to: {wordlist_output}")
    print(f"\nPress Enter when you've exported the word list...")
    
    input()
    
    if not os.path.exists(wordlist_output):
        print(f"\n✗ Word list not found: {wordlist_output}")
        print("Please export from CTA and try again")
        return False
    
    print(f"\n✓ Found word list: {wordlist_output}")
    return True


def run_sentence_extractor(config: dict):
    """Step 3: Generate Anki cards with translations and definitions."""
    print("\n" + "=" * 60)
    print("STEP 3: Generating Anki Cards")
    print("=" * 60)
    
    wordlist = config.get('wordlist_output', 'wordlist.tsv')
    subtitles_folder = config['subtitles_folder']
    anki_output = config.get('anki_output', 'anki_cards.tsv')
    
    # Get path to sentence_extractor_enhanced.py in the same directory
    script_dir = Path(__file__).parent
    extractor_script = script_dir / "sentence_extractor_enhanced.py"

    # Build command
    cmd = [
        'python', str(extractor_script),
        wordlist,
        subtitles_folder,
        '-o', anki_output
    ]
    
    # Add optional parameters
    if 'min_length' in config:
        cmd.extend(['--min-length', str(config['min_length'])])
    
    if config.get('include_empty', False):
        cmd.append('--include-empty')
    
    # DeepL options
    if not config.get('skip_translation', False):
        deepl_key = config.get('deepl_key') or os.environ.get('DEEPL_API_KEY')
        if deepl_key:
            cmd.extend(['--deepl-key', deepl_key])
            if 'target_lang' in config:
                cmd.extend(['--target-lang', config['target_lang']])
        else:
            print("\nWarning: No DeepL API key found")
            print("Set 'deepl_key' in config or DEEPL_API_KEY environment variable")
            print("Continuing without translations...\n")
            cmd.append('--no-translate')
    else:
        cmd.append('--no-translate')
    
    # CC-CEDICT options
    if config.get('skip_definitions', False):
        cmd.append('--no-definitions')
    
    if 'cedict_path' in config:
        cmd.extend(['--cedict-path', config['cedict_path']])
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✓ Anki cards generated: {anki_output}")
        return True
    else:
        print("\n✗ Error generating Anki cards")
        return False


def show_next_steps(config: dict):
    """Show final instructions."""
    print("\n" + "=" * 60)
    print("✓ WORKFLOW COMPLETE!")
    print("=" * 60)
    
    anki_output = config.get('anki_output', 'anki_cards.tsv')
    
    print(f"\nNext steps:")
    print(f"1. Open Anki")
    print(f"2. Import {anki_output}")
    print(f"3. Select 'Tab' as field separator")
    print(f"4. Map fields to your note type")
    print(f"5. Start learning! 🎴")
    
    print(f"\nFiles created:")
    print(f"  - {config.get('merged_output', 'merged_subtitles.txt')}")
    print(f"  - {config.get('wordlist_output', 'wordlist.tsv')}")
    print(f"  - {anki_output}")


def create_example_config():
    """Create an example configuration file."""
    example = {
        "subtitles_folder": "Nirvana Subtitles",
        "merged_output": "nirvana_merged.txt",
        "wordlist_output": "nirvana_wordlist.tsv",
        "anki_output": "nirvana_anki.tsv",
        
        "deepl_key": "",
        "target_lang": "EN-US",
        
        "min_length": 4,
        "include_empty": False,
        
        "skip_translation": False,
        "skip_definitions": False,
        "cedict_path": "cedict_ts.u8"
    }
    
    with open('config_example.json', 'w', encoding='utf-8') as f:
        json.dump(example, f, indent=2, ensure_ascii=False)
    
    print("Created config_example.json")


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py config.json")
        print("\nTo create example config:")
        print("  python batch_process.py --create-config")
        return
    
    if sys.argv[1] == '--create-config':
        create_example_config()
        return
    
    config_path = sys.argv[1]
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        print("Create one with: python batch_process.py --create-config")
        return
    
    print("=" * 60)
    print("AUTOMATED CHINESE SUBTITLE TO ANKI WORKFLOW")
    print("=" * 60)
    
    config = load_config(config_path)
    print(f"\nLoaded configuration from: {config_path}")
    print(f"Project: {config.get('subtitles_folder', 'Unknown')}")
    
    # Step 1: Merge SRT files
    if not run_merge_srt(config):
        print("\n✗ Workflow failed at Step 1")
        return
    
    # Step 2: Wait for CTA export
    if not wait_for_cta_export(config):
        print("\n✗ Workflow failed at Step 2")
        return
    
    # Step 3: Generate Anki cards
    if not run_sentence_extractor(config):
        print("\n✗ Workflow failed at Step 3")
        return
    
    # Done!
    show_next_steps(config)


if __name__ == "__main__":
    main()
