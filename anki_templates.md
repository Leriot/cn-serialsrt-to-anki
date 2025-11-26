# Anki Card Templates

Copy the following into your Anki card styling and templates.

## Styling (CSS)

```css
.card {
  font-family: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #eee;
  text-align: center;
  padding: 20px;
}

.sentence-box {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 25px 20px;
  margin: 15px auto;
  max-width: 600px;
  border: 1px solid rgba(255,255,255,0.1);
}

.sentence-box.traditional {
  background: rgba(255,200,100,0.05);
  border: 1px solid rgba(255,200,100,0.2);
}

.cloze-sentence {
  font-size: 28px;
  line-height: 1.6;
  letter-spacing: 2px;
}

.script-label {
  font-size: 11px;
  color: #888;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Cloze colors - hidden vs revealed */
.cloze-inactive {
  background: #e94560;
  color: #e94560;
  padding: 2px 15px;
  border-radius: 4px;
}

.cloze {
  background: linear-gradient(90deg, #00b894, #00cec9);
  color: #fff;
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: bold;
}

/* Word panel grid */
.word-panel {
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 20px;
  margin: 25px auto;
  max-width: 500px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  text-align: left;
}

.word-display {
  grid-column: 1 / -1;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.word-main {
  font-size: 48px;
  font-weight: bold;
  background: linear-gradient(90deg, #74b9ff, #a29bfe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.word-traditional {
  font-size: 24px;
  color: #f9ca24;
  margin-top: 5px;
}

.info-item {
  padding: 10px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
}

.info-label {
  font-size: 10px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 5px;
}

.info-value {
  font-size: 16px;
  color: #fff;
}

.info-value.pinyin {
  font-style: italic;
  font-size: 20px;
}

.info-value.variants {
  font-size: 13px;
  color: #aaa;
}

.name-badge {
  display: inline-block;
  background: #0f3460;
  color: #53d8fb;
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.hint-section {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.pinyin-hint {
  font-size: 18px;
  color: #888;
  font-style: italic;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  margin: 20px 0;
}

.episode-tag {
  font-size: 11px;
  color: #666;
  margin-top: 20px;
}

.episode-tag span {
  background: rgba(255,255,255,0.1);
  padding: 4px 10px;
  border-radius: 10px;
}

/* NEW: Translation and Definitions */
.translation-box {
  font-style: italic;
  color: #aaa;
  margin: 10px auto;
  max-width: 600px;
  padding: 10px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.definition-box {
  text-align: left;
  background: rgba(0,0,0,0.2);
  padding: 15px;
  border-radius: 8px;
  margin: 15px auto;
  max-width: 500px;
  color: #ddd;
  font-size: 14px;
  line-height: 1.4;
}
```

## Front Template

```html
<div class="sentence-box traditional">
  <div class="script-label">繁體 Traditional</div>
  <div class="cloze-sentence">
    {{cloze:cloze_traditional}}
  </div>
</div>

<div class="hint-section">
  <div class="info-label">Hint Translation</div>
  {{#translation}}
  <div class="translation-box" style="border: none; font-style: normal; color: #888;">
    {{translation}}
  </div>
  {{/translation}}
</div>

{{#is_name}}
<div style="margin-top: 15px;">
  <span class="name-badge">📛 Proper Noun</span>
</div>
{{/is_name}}

<div class="episode-tag">
  <span>🎬 {{episode}}</span>
</div>
```

## Back Template

```html
<!-- Traditional (Answer) -->
<div class="sentence-box traditional">
  <div class="script-label">繁體 Traditional</div>
  <div class="cloze-sentence">
    {{cloze:cloze_traditional}}
  </div>
</div>

<!-- Simplified -->
<div class="sentence-box">
  <div class="script-label">简体 Simplified</div>
  <div class="cloze-sentence">
    {{cloze:cloze_simplified}}
  </div>
</div>

<!-- Translation -->
{{#translation}}
<div class="translation-box">
  {{translation}}
</div>
{{/translation}}

<div class="divider"></div>

<!-- Word info panel -->
<div class="word-panel">
  
  <div class="word-display">
    <div class="word-main">{{word_simplified}}</div>
    <div class="word-traditional">{{word_traditional}}</div>
  </div>
  
  <div class="info-item">
    <div class="info-label">Pinyin</div>
    <div class="info-value pinyin">{{pinyin}}</div>
    {{#pinyin_variants}}
    <div class="info-value variants">also: {{pinyin_variants}}</div>
    {{/pinyin_variants}}
  </div>
  
  <div class="info-item">
    <div class="info-label">Type</div>
    <div class="info-value">
      {{#is_name}}
      <span class="name-badge">📛 Name</span>
      {{/is_name}}
      {{^is_name}}
      <span style="color: #666;">—</span>
      {{/is_name}}
    </div>
  </div>
  
</div>

<!-- Definitions -->
{{#definition}}
<div class="definition-box">
  <div class="info-label">Definitions</div>
  {{definition}}
</div>
{{/definition}}

<div class="episode-tag">
  <span>🎬 {{episode}}</span>
</div>
```
