# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Get your DeepL API key (free tier: 500k chars/month)
# Visit: https://www.deepl.com/pro-api
# Set it as environment variable:
export DEEPL_API_KEY="your-key-here"
```

## 🎯 Option 1: Automated Workflow (Recommended)

```bash
# 1. Create configuration file
python batch_process.py --create-config

# 2. Edit config_example.json with your settings:
{
  "subtitles_folder": "Your_Subtitles_Folder",
  "deepl_key": "your-deepl-key",  # or leave empty to use env var
  "target_lang": "EN-US"
}

# 3. Run automated workflow
python batch_process.py config_example.json
```

The script will:
1. ✅ Merge your SRT files
2. ⏸️ Pause for you to use Chinese Text Analyzer
3. ✅ Generate Anki cards with translations & definitions

## 🔧 Option 2: Manual Steps

### Step 1: Merge Subtitles
```bash
python merge_srt.py "Subtitles_Folder" merged.txt
```

### Step 2: Chinese Text Analyzer
1. Open `merged.txt` in Chinese Text Analyzer
2. Select words to learn
3. Export as `wordlist.tsv`

### Step 3: Generate Anki Cards
```bash
python sentence_extractor_enhanced.py \
    wordlist.tsv \
    "Subtitles_Folder" \
    --output anki_cards.tsv \
    --deepl-key YOUR_KEY
```

### Step 4: Import to Anki
1. Open Anki
2. File → Import
3. Select `anki_cards.tsv`
4. Choose Tab as separator
5. Done! 🎴

## 🌍 Language Options

Change `--target-lang`:
- English (US): `EN-US`
- English (UK): `EN-GB`
- Czech: `CS`
- German: `DE`
- Spanish: `ES`
- French: `FR`
- Japanese: `JA`
- And more...

## 💾 What Gets Created

```
📁 Your Project/
├── merged.txt                    # Clean Chinese text
├── merged_with_episodes.txt      # Text with episode markers
├── wordlist.tsv                  # From Chinese Text Analyzer
├── anki_cards.tsv               # Ready to import to Anki
└── cedict_ts.u8                  # Dictionary (auto-downloaded)
```

## 🎴 Anki Fields You Get

1. Cloze sentences (simplified & traditional)
2. Target words (simplified & traditional)
3. Pinyin + variants
4. Full sentences (simplified & traditional)
5. **🆕 English translation**
6. **🆕 Dictionary definition**
7. Episode source

## 💡 Pro Tips

### Save Money on API Calls
- Free DeepL: 500,000 characters/month
- A typical drama (40 episodes) ≈ 50,000 characters
- You can do ~10 dramas per month free!

### Speed Things Up
- CC-CEDICT downloads once and caches
- Translations batch 50 sentences at a time
- Typical processing: 1000 words in ~2-3 minutes

### Customize Cards
Edit the fields you want:
- Skip translation: `--no-translate`
- Skip definitions: `--no-definitions`
- Different target language: `--target-lang CS`

## ❓ Troubleshooting

### "DeepL not installed"
```bash
pip install deepl
```

### "No API key"
```bash
# Option 1: Set environment variable
export DEEPL_API_KEY="your-key"

# Option 2: Pass as flag
--deepl-key YOUR_KEY

# Option 3: Add to config file
"deepl_key": "your-key"
```

### "Dictionary not found"
The script auto-downloads it. If it fails:
```bash
python cedict_manager.py
```

## 📚 Example Workflow

Let's say you're learning from "琅琊榜" (Nirvana in Fire):

```bash
# 1. Setup
pip install -r requirements.txt
export DEEPL_API_KEY="your-key"

# 2. Create config
python batch_process.py --create-config
# Edit config_example.json → change subtitles_folder to "Nirvana_Subtitles"

# 3. Run workflow
python batch_process.py config_example.json

# Script merges → You process in CTA → Script creates Anki cards
# 4. Import to Anki and start learning!
```

## 🎓 Learning Resources

- [DeepL API Docs](https://www.deepl.com/docs-api)
- [Chinese Text Analyzer](https://www.chinesetextanalyser.com/)
- [CC-CEDICT](https://cc-cedict.org/)
- [Anki User Manual](https://docs.ankiweb.net/)

---

**Ready to start?** Run the automated workflow and you'll have Anki cards in minutes! 🚀
