#!/usr/bin/env python3
"""
SRT File Merger
===============
Merges multiple .srt subtitle files into a single text file.
Creates two versions:
1. Plain merged text without episode markers
2. Merged text with episode markers for tracking

Usage:
    python merge_srt.py <subtitles_folder> <output_file>
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple


def parse_srt_file(filepath: str) -> List[str]:
    """
    Parse SRT file and extract subtitle text lines.

    Args:
        filepath: Path to .srt file

    Returns:
        List of subtitle text lines (no timestamps or numbers)
    """
    lines = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try alternative encodings
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            with open(filepath, 'r', encoding='gb2312') as f:
                content = f.read()

    # Split into subtitle blocks (separated by blank lines)
    blocks = content.strip().split('\n\n')

    for block in blocks:
        block_lines = block.strip().split('\n')

        # Skip if block is too short
        if len(block_lines) < 3:
            continue

        # First line is number, second is timestamp, rest is text
        # Skip number and timestamp, keep only text
        text_lines = block_lines[2:]

        # Filter out lines that look like timestamps or numbers
        for line in text_lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip lines that are just numbers
            if re.match(r'^\d+$', line):
                continue
            # Skip lines that look like timestamps
            if re.match(r'\d{2}:\d{2}:\d{2}', line):
                continue

            lines.append(line)

    return lines


def get_srt_files(folder: str) -> List[Tuple[str, str]]:
    """
    Get all .srt files in folder, sorted naturally.

    Args:
        folder: Path to folder containing .srt files

    Returns:
        List of tuples (filepath, filename)
    """
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"Error: Folder not found: {folder}")
        return []

    # Find all .srt files
    srt_files = list(folder_path.glob("**/*.srt"))

    if not srt_files:
        print(f"Warning: No .srt files found in {folder}")
        return []

    # Sort naturally (handling episode numbers correctly)
    def natural_sort_key(path):
        # Extract numbers from filename for natural sorting
        parts = re.split(r'(\d+)', path.name.lower())
        return [int(part) if part.isdigit() else part for part in parts]

    srt_files.sort(key=natural_sort_key)

    return [(str(f), f.name) for f in srt_files]


def merge_srt_files(folder: str, output_file: str):
    """
    Merge all SRT files in folder into a single text file.
    Creates two versions: with and without episode markers.

    Args:
        folder: Path to folder containing .srt files
        output_file: Path to output file
    """
    print(f"Searching for .srt files in: {folder}")

    srt_files = get_srt_files(folder)

    if not srt_files:
        print("No .srt files to merge")
        return

    print(f"Found {len(srt_files)} .srt files")

    # Prepare output files
    output_path = Path(output_file)
    output_with_episodes = output_path.parent / f"{output_path.stem}_with_episodes.txt"

    all_lines = []
    all_lines_with_markers = []

    # Process each SRT file
    for i, (filepath, filename) in enumerate(srt_files, 1):
        print(f"  [{i}/{len(srt_files)}] Processing: {filename}")

        lines = parse_srt_file(filepath)

        if not lines:
            print(f"    Warning: No text extracted from {filename}")
            continue

        print(f"    Extracted {len(lines)} lines")

        # Add to plain merged output
        all_lines.extend(lines)

        # Add episode marker and lines to marked output
        episode_marker = f"\n{'='*60}\n{filename}\n{'='*60}\n"
        all_lines_with_markers.append(episode_marker)
        all_lines_with_markers.extend(lines)

    # Write plain merged output
    print(f"\nWriting merged output to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines))

    print(f"[OK] Wrote {len(all_lines)} lines")

    # Write output with episode markers
    print(f"\nWriting output with episode markers to: {output_with_episodes}")
    with open(output_with_episodes, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines_with_markers))

    print(f"[OK] Wrote {len(all_lines_with_markers)} lines")

    print("\n" + "="*60)
    print("[OK] Merge complete!")
    print("="*60)
    print(f"\nFiles created:")
    print(f"  1. {output_file}")
    print(f"     - Plain merged text (for Chinese Text Analyzer)")
    print(f"  2. {output_with_episodes}")
    print(f"     - With episode markers (for reference)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_srt.py <subtitles_folder> <output_file>")
        print("\nExample:")
        print("  python merge_srt.py 'Nirvana Subtitles' merged.txt")
        return

    folder = sys.argv[1]
    output_file = sys.argv[2]

    merge_srt_files(folder, output_file)


if __name__ == "__main__":
    main()
