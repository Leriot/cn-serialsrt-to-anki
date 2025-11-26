# Enhanced Chinese Subtitle Learning Workflow

Complete workflow for creating Anki flashcards from Chinese subtitles with DeepL translations and CC-CEDICT definitions.

## 🆕 New Features

- **DeepL Translation**: Automatically translate example sentences to English (or any language)
- **CC-CEDICT Definitions**: Local dictionary lookups with pinyin and definitions
- **Extended Anki Cards**: 13 fields including translations and definitions

## 📋 Requirements

```bash
pip install -r requirements.txt
```

### DeepL API Key

Get a free API key from [DeepL](https://www.deepl.com/pro-api):
- Free tier: 500,000 characters/month
- More than enough for most subtitle projects

Set your API key:
```bash
export DEEPL_API_KEY="your-key-here"
```

Or pass it directly with `--deepl-key`

## 🚀 Quick Start

### Complete Workflow

```bash
# 1. Merge SRT files (unchanged)
python merge_srt.py "Subtitles Folder" merged_output.txt

# 2. Open merged_output.txt in Chinese Text Analyzer
#    Export word list to: wordlist.tsv

# 3. Run enhanced sentence extractor
python sentence_extractor_enhanced.py \
    wordlist.tsv \
    "Subtitles Folder" \
    --output anki_cards.tsv \
    --deepl-key YOUR_KEY \
    --target-lang EN-US

# 4. Import anki_cards.tsv into Anki
```

### First Run Setup

The script will automatically:
1. Download CC-CEDICT dictionary (~30MB) on first run
2. Cache it locally as `cedict_ts.u8`
3. Use cached version for future runs

## 📖 Usage Examples

### Basic Usage (no translation/definitions)

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" -o output.tsv
```

### With DeepL Translation Only

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --deepl-key YOUR_KEY \
    --target-lang EN-US
```

### With CC-CEDICT Definitions Only

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --no-translate
```

### Full Features (Translation + Definitions)

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --deepl-key YOUR_KEY \
    --target-lang CS  # Czech, for example
```

### Translate to Different Languages

Supported languages: `EN-US`, `EN-GB`, `CS` (Czech), `DE`, `ES`, `FR`, `IT`, `JA`, `PL`, `PT`, `RU`, etc.

```bash
# German
--target-lang DE

# Czech
--target-lang CS

# Japanese
--target-lang JA
```

## 📊 Output Fields (Anki TSV)

The enhanced output includes **13 fields**:

1. **cloze_simplified** - Sentence with cloze deletion (简体)
2. **cloze_traditional** - Sentence with cloze deletion (繁體)
3. **word_simplified** - Target word (简体)
4. **word_traditional** - Target word with variants (繁體)
5. **pinyin** - Primary pinyin reading
6. **pinyin_variants** - Alternative readings
7. **is_name** - Proper noun indicator
8. **sentence_simplified** - Full sentence (简体)
9. **sentence_traditional** - Full sentence (繁體)
10. **translation** - 🆕 DeepL translation
11. **definition** - 🆕 CC-CEDICT definition
12. **episode** - Source episode/file
13. *(Line number not exported)*

## 🎴 Anki Card Template

### Front Template
```html
<div class="sentence">{{cloze_simplified}}</div>
<div class="pinyin">{{pinyin}}</div>
```

### Back Template
```html
{{FrontSide}}
<hr>
<div class="word">{{word_simplified}} - {{word_traditional}}</div>
<div class="translation">{{translation}}</div>
<div class="definition">{{definition}}</div>
{{#pinyin_variants}}
<div class="variants">Also: {{pinyin_variants}}</div>
{{/pinyin_variants}}
<div class="source">{{episode}}</div>
```

## 🛠️ Advanced Options

### Skip Translation (Use Cached Definitions Only)

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --no-translate
```

### Skip Definitions (Translation Only)

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --deepl-key YOUR_KEY \
    --no-definitions
```

### Custom CC-CEDICT Path

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --cedict-path /path/to/custom/cedict.u8
```

### Include Words Without Example Sentences

```bash
python sentence_extractor_enhanced.py wordlist.tsv "Subtitles" \
    --include-empty
```

## 🔧 Standalone Tools

### Test CC-CEDICT Dictionary

```bash
# Download and test dictionary lookups
python cedict_manager.py

# Use custom path
python cedict_manager.py /path/to/cedict.u8
```

### Merge SRT Files (Original)

```bash
python merge_srt.py "Subtitles Folder" output.txt
```

Creates two files:
- `output.txt` - Clean text for Chinese Text Analyzer
- `output_with_episodes.txt` - Text with episode markers

## 💡 Tips

### Rate Limits
- DeepL Free: 500,000 chars/month
- Script includes rate limiting (0.5s between batches)
- Batch size: 50 sentences at a time

### Definition Format
Definitions show as: `pinyin: definition [+N more]`
- Example: `Sū: surname Su; [+2 more]`
- Pinyin matching prefers CTA export pinyin

### Translation Quality
- DeepL is context-aware for Chinese
- Works well with colloquial dialogue
- Preserves meaning better than Google Translate

### Storage
- CC-CEDICT file: ~30MB
- Loads in 2-3 seconds
- Contains ~120,000 entries

## 🐛 Troubleshooting

### "DeepL not installed"
```bash
pip install deepl
```

### "No API key provided"
```bash
export DEEPL_API_KEY="your-key"
# Or use --deepl-key flag
```

### "Dictionary file not found"
Script auto-downloads on first run. If download fails:
```bash
python cedict_manager.py  # Manual download
```

### Translation Errors
- Check API key is valid
- Check character limit (500k free tier)
- Script continues on errors, check console output

## 📝 Example Output

```tsv
cloze_simplified	cloze_traditional	word_simplified	word_traditional	pinyin	pinyin_variants	is_name	sentence_simplified	sentence_traditional	translation	definition	episode
我{{c1::需要}}帮助	我{{c1::需要}}幫助	需要	需要	xūyào		需要	我需要帮助	我需要幫助	I need help	xū yào: to need; to want; to demand; needs; to require	ep01
```

## 🔄 Workflow Diagram

```
SRT Files
    ↓ [merge_srt.py]
Merged Text
    ↓ [Chinese Text Analyzer]
Word List (TSV)
    ↓ [sentence_extractor_enhanced.py]
    ├─→ Match sentences from SRTs
    ├─→ Look up in CC-CEDICT
    └─→ Translate via DeepL
    ↓
Anki TSV (with translations & definitions)
    ↓ [Import to Anki]
Flashcards Ready! 🎴
```

## 📚 Resources

- [DeepL API Docs](https://www.deepl.com/docs-api)
- [CC-CEDICT Project](https://cc-cedict.org/)
- [Chinese Text Analyzer](https://www.chinesetextanalyser.com/)
- [Anki Manual](https://docs.ankiweb.net/)

## 📄 License

Scripts are provided as-is. CC-CEDICT is licensed under Creative Commons BY-SA 4.0.

---

**Questions?** Check the troubleshooting section or open an issue!
