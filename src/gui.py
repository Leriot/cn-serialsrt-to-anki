#!/usr/bin/env python3
"""
Chinese Subtitle to Anki - GUI Application
==========================================
User-friendly interface for converting Chinese subtitles to Anki flashcards.

Features:
- Select SRT files or folders for merging
- Configure DeepL API key and target language
- Select Chinese Text Analyzer export file
- Run merge and sentence extraction workflows
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
import subprocess
from pathlib import Path
import threading


class ChineseSubtitleToAnkiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chinese Subtitle to Anki Converter")
        self.root.geometry("900x700")

        # Configuration
        self.config_file = "gui_config.json"
        self.config = self.load_config()

        # Setup UI
        self.create_widgets()
        self.load_saved_settings()

    def load_config(self):
        """Load saved configuration from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'deepl_key': '',
            'target_lang': 'EN-US',
            'subtitles_folder': '',
            'merged_output': '',
            'cta_export': '',
            'anki_output': ''
        }

    def save_config(self):
        """Save current configuration to JSON file."""
        self.config = {
            'deepl_key': self.deepl_key_var.get(),
            'target_lang': self.target_lang_var.get(),
            'subtitles_folder': self.subtitles_folder_var.get(),
            'merged_output': self.merged_output_var.get(),
            'cta_export': self.cta_export_var.get(),
            'anki_output': self.anki_output_var.get()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def load_saved_settings(self):
        """Load saved settings into GUI fields."""
        self.deepl_key_var.set(self.config.get('deepl_key', ''))
        self.target_lang_var.set(self.config.get('target_lang', 'EN-US'))
        self.subtitles_folder_var.set(self.config.get('subtitles_folder', ''))
        self.merged_output_var.set(self.config.get('merged_output', ''))
        self.cta_export_var.set(self.config.get('cta_export', ''))
        self.anki_output_var.set(self.config.get('anki_output', ''))

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        # Title
        title_label = ttk.Label(main_frame, text="Chinese Subtitle to Anki Converter",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1

        # ===== STEP 1: Merge SRT Files =====
        step1_label = ttk.Label(main_frame, text="Step 1: Merge SRT Files",
                               font=('Arial', 12, 'bold'))
        step1_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        row += 1

        # Subtitles folder selection
        ttk.Label(main_frame, text="Subtitles Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.subtitles_folder_var = tk.StringVar()
        subtitles_entry = ttk.Entry(main_frame, textvariable=self.subtitles_folder_var, width=50)
        subtitles_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_subtitles_folder).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Merged output file
        ttk.Label(main_frame, text="Merged Output:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.merged_output_var = tk.StringVar(value="merged_subtitles.txt")
        merged_entry = ttk.Entry(main_frame, textvariable=self.merged_output_var, width=50)
        merged_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_merged_output).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Merge button
        self.merge_button = ttk.Button(main_frame, text="Run Merge", command=self.run_merge,
                                       style='Accent.TButton')
        self.merge_button.grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # ===== STEP 2: Chinese Text Analyzer =====
        step2_label = ttk.Label(main_frame, text="Step 2: Process in Chinese Text Analyzer",
                               font=('Arial', 12, 'bold'))
        step2_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        row += 1

        # Instructions
        instructions = ("Open the merged file in Chinese Text Analyzer,\n"
                       "select words to learn, and export in this format:\n"
                       "殿下\t殿下[殿下]\tdiàn xià")
        ttk.Label(main_frame, text=instructions, foreground='blue').grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1

        # CTA export file selection
        ttk.Label(main_frame, text="CTA Export File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cta_export_var = tk.StringVar()
        cta_entry = ttk.Entry(main_frame, textvariable=self.cta_export_var, width=50)
        cta_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_cta_export).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # ===== STEP 3: Generate Anki Cards =====
        step3_label = ttk.Label(main_frame, text="Step 3: Generate Anki Cards",
                               font=('Arial', 12, 'bold'))
        step3_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        row += 1

        # DeepL API Key
        ttk.Label(main_frame, text="DeepL API Key:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.deepl_key_var = tk.StringVar()
        deepl_entry = ttk.Entry(main_frame, textvariable=self.deepl_key_var, width=50, show='*')
        deepl_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.show_key_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Show", variable=self.show_key_var,
                       command=lambda: deepl_entry.config(show='' if self.show_key_var.get() else '*')).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Target Language
        ttk.Label(main_frame, text="Target Language:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.target_lang_var = tk.StringVar(value="EN-US")
        lang_combo = ttk.Combobox(main_frame, textvariable=self.target_lang_var, width=47)
        lang_combo['values'] = (
            'EN-US', 'EN-GB', 'CS', 'DE', 'ES', 'FR', 'IT', 'JA', 'PL', 'PT', 'RU', 'ZH'
        )
        lang_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Anki output file
        ttk.Label(main_frame, text="Anki Output:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.anki_output_var = tk.StringVar(value="anki_cards.tsv")
        anki_entry = ttk.Entry(main_frame, textvariable=self.anki_output_var, width=50)
        anki_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_anki_output).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Generate Anki Cards button
        self.generate_button = ttk.Button(main_frame, text="Generate Anki Cards",
                                         command=self.run_generate,
                                         style='Accent.TButton')
        self.generate_button.grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # ===== Output Log =====
        ttk.Label(main_frame, text="Output Log:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=80,
                                                   wrap=tk.WORD, state='disabled')
        self.log_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        row += 1

        # Clear log button
        ttk.Button(main_frame, text="Clear Log", command=self.clear_log).grid(
            row=row, column=1, sticky=tk.W, pady=5)

    def log(self, message):
        """Add message to output log."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()

    def clear_log(self):
        """Clear the output log."""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def browse_subtitles_folder(self):
        """Browse for subtitles folder."""
        folder = filedialog.askdirectory(title="Select Subtitles Folder")
        if folder:
            self.subtitles_folder_var.set(folder)
            # Auto-suggest merged output name based on folder
            if not self.merged_output_var.get() or self.merged_output_var.get() == "merged_subtitles.txt":
                folder_name = Path(folder).name
                self.merged_output_var.set(f"{folder_name}_merged.txt")

    def browse_merged_output(self):
        """Browse for merged output file."""
        file = filedialog.asksaveasfilename(
            title="Save Merged Output As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.merged_output_var.set(file)

    def browse_cta_export(self):
        """Browse for CTA export file."""
        file = filedialog.askopenfilename(
            title="Select Chinese Text Analyzer Export",
            filetypes=[("TSV files", "*.tsv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.cta_export_var.set(file)

    def browse_anki_output(self):
        """Browse for Anki output file."""
        file = filedialog.asksaveasfilename(
            title="Save Anki Cards As",
            defaultextension=".tsv",
            filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")]
        )
        if file:
            self.anki_output_var.set(file)

    def run_merge(self):
        """Run the SRT merge process."""
        # Validate inputs
        subtitles_folder = self.subtitles_folder_var.get()
        merged_output = self.merged_output_var.get()

        if not subtitles_folder:
            messagebox.showerror("Error", "Please select a subtitles folder")
            return

        if not os.path.exists(subtitles_folder):
            messagebox.showerror("Error", f"Folder not found: {subtitles_folder}")
            return

        if not merged_output:
            messagebox.showerror("Error", "Please specify merged output filename")
            return

        # Save config
        self.save_config()

        # Disable button
        self.merge_button.config(state='disabled')

        # Run in thread
        thread = threading.Thread(target=self._run_merge_thread, args=(subtitles_folder, merged_output))
        thread.daemon = True
        thread.start()

    def _run_merge_thread(self, subtitles_folder, merged_output):
        """Run merge in background thread."""
        try:
            self.log("="*60)
            self.log("Starting SRT merge...")
            self.log(f"Subtitles folder: {subtitles_folder}")
            self.log(f"Output file: {merged_output}")
            self.log("")

            # Get path to merge_srt.py
            script_dir = Path(__file__).parent
            merge_script = script_dir / "merge_srt.py"

            # Run merge_srt.py
            result = subprocess.run(
                [sys.executable, str(merge_script), subtitles_folder, merged_output],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # Show output
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")

            if result.returncode == 0:
                self.log("")
                self.log("✓ Merge completed successfully!")
                self.log(f"✓ Next: Open {merged_output} in Chinese Text Analyzer")
                messagebox.showinfo("Success", "SRT merge completed!\n\n"
                                             f"Next step: Open {merged_output} in Chinese Text Analyzer")
            else:
                self.log("")
                self.log("✗ Merge failed!")
                messagebox.showerror("Error", "Merge failed. Check the log for details.")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to run merge: {str(e)}")

        finally:
            # Re-enable button
            self.merge_button.config(state='normal')

    def run_generate(self):
        """Run the Anki card generation process."""
        # Validate inputs
        cta_export = self.cta_export_var.get()
        subtitles_folder = self.subtitles_folder_var.get()
        anki_output = self.anki_output_var.get()
        deepl_key = self.deepl_key_var.get()
        target_lang = self.target_lang_var.get()

        if not cta_export:
            messagebox.showerror("Error", "Please select Chinese Text Analyzer export file")
            return

        if not os.path.exists(cta_export):
            messagebox.showerror("Error", f"CTA export file not found: {cta_export}")
            return

        if not subtitles_folder:
            messagebox.showerror("Error", "Please select subtitles folder")
            return

        if not os.path.exists(subtitles_folder):
            messagebox.showerror("Error", f"Subtitles folder not found: {subtitles_folder}")
            return

        if not anki_output:
            messagebox.showerror("Error", "Please specify Anki output filename")
            return

        # Save config
        self.save_config()

        # Disable button
        self.generate_button.config(state='disabled')

        # Run in thread
        thread = threading.Thread(
            target=self._run_generate_thread,
            args=(cta_export, subtitles_folder, anki_output, deepl_key, target_lang)
        )
        thread.daemon = True
        thread.start()

    def _run_generate_thread(self, cta_export, subtitles_folder, anki_output, deepl_key, target_lang):
        """Run generation in background thread."""
        try:
            self.log("="*60)
            self.log("Starting Anki card generation...")
            self.log(f"CTA export: {cta_export}")
            self.log(f"Subtitles folder: {subtitles_folder}")
            self.log(f"Output file: {anki_output}")
            self.log(f"Target language: {target_lang}")
            self.log("")

            # Get path to sentence_extractor_enhanced.py
            script_dir = Path(__file__).parent
            extractor_script = script_dir / "sentence_extractor_enhanced.py"

            # Build command
            cmd = [
                sys.executable, str(extractor_script),
                cta_export,
                subtitles_folder,
                '-o', anki_output
            ]

            # Add DeepL options if key is provided
            if deepl_key:
                cmd.extend(['--deepl-key', deepl_key])
                cmd.extend(['--target-lang', target_lang])
            else:
                self.log("Warning: No DeepL API key provided, skipping translations")
                cmd.append('--no-translate')

            self.log(f"Running: {' '.join(cmd[2:])}")  # Don't log python path
            self.log("")

            # Run sentence extractor
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # Show output
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")

            if result.returncode == 0:
                self.log("")
                self.log("✓ Anki card generation completed!")
                self.log(f"✓ Import {anki_output} into Anki")
                messagebox.showinfo("Success", "Anki cards generated!\n\n"
                                             f"Next step: Import {anki_output} into Anki")
            else:
                self.log("")
                self.log("✗ Generation failed!")
                messagebox.showerror("Error", "Generation failed. Check the log for details.")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate cards: {str(e)}")

        finally:
            # Re-enable button
            self.generate_button.config(state='normal')


def main():
    root = tk.Tk()

    # Try to apply a modern theme
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
    except:
        pass

    app = ChineseSubtitleToAnkiGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
