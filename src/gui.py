import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from src.parser import extract_text
from src.checker import check_citations
from src.report import generate_report

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pre-filing Brief Checker")
        self.geometry("600x500")
        
        self.filepath = None
        self.results = None
        
        # UI Elements
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10, fill=tk.X, padx=10)
        
        self.select_btn = tk.Button(btn_frame, text="Select File (PDF/DOCX)", command=self.select_file)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_label = tk.Label(btn_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.check_btn = tk.Button(btn_frame, text="Check Citations", command=self.run_checks, state=tk.DISABLED)
        self.check_btn.pack(side=tk.RIGHT, padx=5)
        
        self.text_area = tk.Text(self, wrap=tk.WORD, height=15)
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.save_btn = tk.Button(self, text="Save Detailed Report", command=self.save_report, state=tk.DISABLED)
        self.save_btn.pack(pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.docx")])
        if path:
            self.filepath = path
            self.file_label.config(text=path)
            self.check_btn.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.save_btn.config(state=tk.DISABLED)

    def run_checks(self):
        self.check_btn.config(state=tk.DISABLED)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Running checks... Please wait.\n")
        
        def worker():
            try:
                # 1. Extract
                text = extract_text(self.filepath)
                self.text_area.insert(tk.END, "Text extracted successfully.\nChecking citations...\n")
                
                # 2. Check
                self.results = check_citations(text)
                
                # 3. Display
                total = self.results.get("total", 0)
                verified = len(self.results.get("verified_correct", []))
                incorrect = len(self.results.get("verified_incorrect", []))
                unverified = len(self.results.get("not_verified", []))
                
                res_text = (
                    f"\n--- High-Level Results ---\n"
                    f"Total Citations Found: {total}\n"
                    f"Verified Correct: {verified}\n"
                    f"Verified Incorrect: {incorrect}\n"
                    f"Not Verified: {unverified}\n"
                )
                self.text_area.insert(tk.END, res_text)
                self.save_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                # Can't easily use messagebox from non-main thread in Tkinter, but for POC it usually works on some OS
                # Better to update text area
                self.text_area.insert(tk.END, f"\nError: {e}")
            finally:
                self.check_btn.config(state=tk.NORMAL)
                
        threading.Thread(target=worker, daemon=True).start()

    def save_report(self):
        if not self.results:
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
        if path:
            try:
                generate_report(self.results, path)
                messagebox.showinfo("Success", f"Report saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save report: {e}")
