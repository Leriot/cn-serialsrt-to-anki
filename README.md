# Chinese Subtitle to Anki Converter

Convert Chinese subtitles (SRT files) into Anki flashcards with translations and definitions!

## ✨ Features

- **🖥️ User-Friendly GUI** - Easy-to-use graphical interface for the complete workflow
- **📁 SRT File Merging** - Combine multiple subtitle files into one for analysis
- **🔤 Chinese Text Analysis** - Integration with Chinese Text Analyzer for word selection
- **🌐 DeepL Translation** - Automatic translation of example sentences (50+ languages)
- **📚 CC-CEDICT Definitions** - Local dictionary lookups with pinyin and definitions
- **🎴 Rich Anki Cards** - 13-field flashcards with context, translations, and definitions

## 🚀 Quick Start

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cn-serialsrt-to-anki.git
   cd cn-serialsrt-to-anki
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a free DeepL API key from [DeepL](https://www.deepl.com/pro-api) (500,000 chars/month free)

### Using the GUI (Recommended)

Launch the graphical interface:

```bash
python run_gui.py
```

The GUI guides you through 3 easy steps:

1. **Merge SRT Files** - Select your subtitles folder and merge into a single text file
2. **Process in Chinese Text Analyzer** - Select words to learn and export
3. **Generate Anki Cards** - Automatic translation and definition lookup

### Using the Command Line

#### Step 1: Merge SRT Files

```bash
python src/merge_srt.py "Subtitles Folder" merged_output.txt
```

This creates two files:
- `merged_output.txt` - Plain text for Chinese Text Analyzer
- `merged_output_with_episodes.txt` - With episode markers for reference

#### Step 2: Process in Chinese Text Analyzer

1. Open `merged_output.txt` in [Chinese Text Analyzer](https://www.chinesetextanalyser.com/)
2. Select words you want to learn
3. Export word list in this format:
   ```
   殿下	殿下[殿下]	diàn xià
   苏	苏[囌]	sū
   苏	苏[蘇]	Sū
   ```

#### Step 3: Generate Anki Cards

```bash
python src/sentence_extractor_enhanced.py \
    wordlist.tsv \
    "Subtitles Folder" \
    --output anki_cards.tsv \
    --deepl-key YOUR_API_KEY \
    --target-lang EN-US
```

#### Step 4: Import to Anki

1. Open Anki
2. Import `anki_cards.tsv`
3. Use **Tab** as field separator
4. Map fields to your note type
5. Start learning!

### Automated Workflow (Advanced)

Use the batch processor for automated runs:

```bash
# Create example config
python src/batch_process.py --create-config

# Edit config_example.json with your settings

# Run automated workflow
python src/batch_process.py config_example.json
```

## 📂 Project Structure

```
cn-serialsrt-to-anki/
├── run_gui.py              # GUI launcher (start here!)
├── requirements.txt        # Python dependencies
│
├── src/                    # Core scripts
│   ├── gui.py             # Graphical user interface
│   ├── merge_srt.py       # SRT file merger
│   ├── sentence_extractor_enhanced.py  # Main processing engine
│   ├── cedict_manager.py  # Dictionary manager
│   └── batch_process.py   # Automated workflow
│
├── docs/                   # Documentation
│   ├── README.md          # Detailed feature documentation
│   └── QUICKSTART.md      # Quick start guide
│
└── data/                   # Runtime data
    └── cedict_ts.u8       # CC-CEDICT dictionary (auto-downloaded)
```

## 🔧 Configuration Options

### DeepL Translation

Set your API key in the GUI or via environment variable:

```bash
export DEEPL_API_KEY="your-key-here"
```

**Supported Languages:**
- `EN-US`, `EN-GB` - English (US/British)
- `CS` - Czech
- `DE` - German
- `ES` - Spanish
- `FR` - French
- `IT` - Italian
- `JA` - Japanese
- `PL` - Polish
- `PT` - Portuguese
- `RU` - Russian
- `ZH` - Chinese
- And many more!

### Advanced Options

For CLI users, see additional options:

```bash
python src/sentence_extractor_enhanced.py --help
```

Options include:
- `--min-length` - Minimum sentence length
- `--include-empty` - Include words without example sentences
- `--no-translate` - Skip translation
- `--no-definitions` - Skip dictionary lookups
- `--cedict-path` - Custom dictionary path

## 📊 Anki Card Fields

Generated cards include 13 fields:

1. **Cloze** - Sentence with target word hidden
2. **Simplified** - Simplified Chinese word
3. **Traditional** - Traditional Chinese variant(s)
4. **Traditional (alt)** - Alternative traditional forms
5. **Pinyin** - Pronunciation
6. **Pinyin (alt)** - Alternative pronunciations
7. **Definition** - English definition from CC-CEDICT
8. **Translation** - DeepL translation of example sentence
9. **Example (Simplified)** - Example sentence in simplified Chinese
10. **Example (Traditional)** - Example sentence in traditional Chinese
11. **Definition (alt)** - Alternative definitions
12. **Is Proper Noun** - Flag for proper nouns (names, places)
13. **Full Sentence** - Complete original sentence

## 🔍 Example Workflow

**Scenario:** You're watching the Chinese drama "隐秘的角落" and want to learn vocabulary from it.

1. **Collect subtitles** - Download SRT files for each episode
2. **Launch GUI** - Run `python run_gui.py`
3. **Merge** - Select subtitle folder, click "Run Merge"
4. **Analyze** - Open merged file in Chinese Text Analyzer, select 200 words
5. **Generate** - Enter DeepL key, select CTA export, click "Generate Anki Cards"
6. **Learn** - Import cards to Anki and start studying!

Result: 200 personalized flashcards with context from your favorite show!

## 🐛 Troubleshooting

### GUI won't start

Make sure tkinter is installed:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (included with Python)
# Windows (included with Python)
```

### "No module named 'deepl'"

Install dependencies:

```bash
pip install -r requirements.txt
```

### DeepL API errors

- Check your API key is correct
- Verify you haven't exceeded monthly quota (500k chars free tier)
- Try reducing batch size in code if rate limited

### No example sentences found

- Verify subtitle folder path is correct
- Check SRT files are properly formatted
- Try with `--include-empty` to include words without examples

## 📚 Additional Resources

- [Detailed Documentation](docs/README.md) - Complete feature documentation
- [Quick Start Guide](docs/QUICKSTART.md) - Fast setup instructions
- [Chinese Text Analyzer](https://www.chinesetextanalyser.com/) - Word selection tool
- [DeepL API](https://www.deepl.com/pro-api) - Translation service
- [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cc-cedict) - Chinese dictionary

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- CC-CEDICT for the comprehensive Chinese-English dictionary
- DeepL for high-quality translations
- Chinese Text Analyzer for word segmentation and selection
- The Anki community for making language learning accessible
