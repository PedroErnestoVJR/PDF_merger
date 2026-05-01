import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import sys
import os
from app.core.pdf_manager import PDFManager
from app.ui.frames import ExplorerFrame, WorkspaceFrame
from app.core.merge_strategies import PyPDFMergeStrategy, GhostscriptMergeStrategy
from app.ui.settings_windows import PyPDFSettingsWindow, GhostscriptSettingsWindow
from app.ui.style_manager import StyleManager
from app.core.debug import debug_trace, Debug

class MainWindow(ctk.CTk):
    @debug_trace
    def __init__(self):
        super().__init__()

        self.title("PDF Merger")
        self.geometry("900x600")

        # Set window icon
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Initialize the Model
        self.pdf_manager = PDFManager()

        # Initialize Strategies
        self.strategies = {
            "PyPDF": PyPDFMergeStrategy(),
            "Ghostscript": GhostscriptMergeStrategy()
        }

        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) # Top Menu
        self.grid_rowconfigure(1, weight=1) # Main Workspace

        # Top Menu / Header Frame
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.top_frame,
            values=["System", "Light", "Dark", "Tonton"],
            command=self.change_theme,
            width=100
        )
        self.appearance_mode_menu.set(StyleManager.get_current_mode())
        self.appearance_mode_menu.pack(side="right", padx=5)
        
        self.appearance_label = ctk.CTkLabel(self.top_frame, text="UI Theme:")
        self.appearance_label.pack(side="right", padx=5)

        # Setup the UI components (PanedWindow for dynamic resizing)
        self.paned_window = tk.PanedWindow(self, orient="horizontal", bd=0, sashwidth=6, sashcursor="sb_h_double_arrow")
        bg_color = "gray14" if ctk.get_appearance_mode() == "Dark" else "gray92"
        self.paned_window.configure(bg=bg_color)
        self.paned_window.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.explorer_frame = ExplorerFrame(self.paned_window, select_callback=self.select_files)
        self.paned_window.add(self.explorer_frame, minsize=150, width=220)

        self.workspace_frame = WorkspaceFrame(
            self.paned_window, 
            remove_callback=self.remove_file,
            move_up_callback=self.move_up,
            move_down_callback=self.move_down
        )
        self.paned_window.add(self.workspace_frame, minsize=300, width=660)

        # Status Bar / Bottom Controls
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.strategy_label = ctk.CTkLabel(self.bottom_frame, text="Merge Algorithm:")
        self.strategy_label.pack(side="left", padx=(10, 0), pady=10)

        self.strategy_var = ctk.StringVar(value="PyPDF")
        self.strategy_menu = ctk.CTkOptionMenu(self.bottom_frame, values=list(self.strategies.keys()), variable=self.strategy_var)
        self.strategy_menu.pack(side="left", padx=10, pady=10)

        self.settings_button = ctk.CTkButton(self.bottom_frame, text="⚙️ Settings", width=40, command=self.open_settings)
        self.settings_button.pack(side="left", padx=(0, 10), pady=10)

        self.merge_button = ctk.CTkButton(self.bottom_frame, text="Merge PDFs", command=self.merge_files)
        self.merge_button.pack(side="left", padx=10, pady=10)

        self.debug_button = ctk.CTkButton(self.bottom_frame, text="🐞 Debug", width=40, command=self.open_debug)
        self.debug_button.pack(side="left", padx=(0, 10), pady=10)

        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Ready")
        self.status_label.pack(side="left", padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, mode="indeterminate", width=150)
        self.progress_bar.set(0)

        if StyleManager.get_current_mode() == "Tonton":
            self.apply_tonton_theme()

    @debug_trace
    def change_theme(self, new_mode):
        StyleManager.change_appearance_mode(new_mode)
        if new_mode == "Tonton":
            self.apply_tonton_theme()
        else:
            self.revert_theme()
        self.refresh_workspace()

    @debug_trace
    def apply_tonton_theme(self):
        pig_bg, pig_frame = "#FCE4EC", "#F8BBD0"
        pig_btn, pig_hover, pig_text = "#F06292", "#E91E63", "#880E4F"

        self.configure(fg_color=pig_bg)
        self.paned_window.configure(bg=pig_bg)
        self.explorer_frame.configure(fg_color=pig_frame)
        self.workspace_frame.configure(fg_color=pig_frame)
        self.workspace_frame.scrollable_frame.configure(
            fg_color=pig_bg, 
            scrollbar_fg_color=pig_frame,
            scrollbar_button_color=pig_btn,
            scrollbar_button_hover_color=pig_hover
        )
        self.bottom_frame.configure(fg_color=pig_frame)

        for lbl in [self.appearance_label, self.strategy_label, self.status_label, self.explorer_frame.label, self.workspace_frame.label]:
            lbl.configure(text_color=pig_text)
        for btn in [self.explorer_frame.select_button, self.settings_button, self.merge_button, self.debug_button]:
            btn.configure(fg_color=pig_btn, hover_color=pig_hover, text_color="white")
            
        self.progress_bar.configure(progress_color=pig_hover, fg_color=pig_frame)
        for menu in [self.appearance_mode_menu, self.strategy_menu]:
            menu.configure(fg_color=pig_btn, button_color=pig_hover, button_hover_color="#C2185B", text_color="white")

    @debug_trace
    def revert_theme(self):
        self.configure(fg_color=("gray92", "gray14"))
        bg_color = "gray14" if ctk.get_appearance_mode() == "Dark" else "gray92"
        self.paned_window.configure(bg=bg_color)
        default_frame = ("gray86", "gray17")
        self.explorer_frame.configure(fg_color=default_frame)
        self.workspace_frame.configure(fg_color=default_frame)
        self.workspace_frame.scrollable_frame.configure(
            fg_color="transparent", 
            scrollbar_fg_color="transparent",
            scrollbar_button_color=("gray55", "gray41"),
            scrollbar_button_hover_color=("gray40", "gray53")
        )
        self.bottom_frame.configure(fg_color=default_frame)

        for lbl in [self.appearance_label, self.strategy_label, self.status_label, self.explorer_frame.label, self.workspace_frame.label]:
            lbl.configure(text_color=("gray10", "gray90"))
        for btn in [self.explorer_frame.select_button, self.settings_button, self.merge_button, self.debug_button]:
            btn.configure(fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#36719F", "#144870"), text_color="white")
            
        self.progress_bar.configure(progress_color=("#3B8ED0", "#1F6AA5"), fg_color=("gray93", "gray20"))
        for menu in [self.appearance_mode_menu, self.strategy_menu]:
            menu.configure(fg_color=("#3B8ED0", "#1F6AA5"), button_color=("#36719F", "#144870"), button_hover_color=("#27577D", "#143855"), text_color="white")

    @debug_trace
    def open_settings(self):
        selected_strategy_name = self.strategy_var.get()
        strategy = self.strategies[selected_strategy_name]
        
        if selected_strategy_name == "PyPDF":
            PyPDFSettingsWindow(self, strategy)
        elif selected_strategy_name == "Ghostscript":
            GhostscriptSettingsWindow(self, strategy)

    @debug_trace
    def open_debug(self):
        Debug().open_window(self)

    @debug_trace
    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_paths:
            self.pdf_manager.add_files(file_paths)
            self.refresh_workspace()
            self.status_label.configure(text=f"Added {len(file_paths)} files.", text_color="white")

    @debug_trace
    def remove_file(self, file_path):
        self.pdf_manager.remove_file(file_path)
        self.refresh_workspace()

    @debug_trace
    def move_up(self, index):
        self.pdf_manager.move_up(index)
        self.refresh_workspace()

    @debug_trace
    def move_down(self, index):
        self.pdf_manager.move_down(index)
        self.refresh_workspace()

    @debug_trace
    def refresh_workspace(self):
        self.workspace_frame.update_list(self.pdf_manager.get_files())

    @debug_trace
    def merge_files(self):
        try:
            output_path = filedialog.asksaveasfilename(
                title="Save Merged PDF", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
            )
            if output_path:
                selected_strategy_name = self.strategy_var.get()
                strategy = self.strategies[selected_strategy_name]
                self.status_label.configure(text=f"Merging with {selected_strategy_name}...", text_color="white")
                self.merge_button.configure(state="disabled")
                
                self.progress_bar.pack(side="left", padx=10, pady=10)
                self.progress_bar.start()

                # Inicia a mesclagem em uma Thread separada (Background)
                threading.Thread(target=self._merge_worker, args=(output_path, strategy), daemon=True).start()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    @debug_trace
    def _merge_worker(self, output_path, strategy):
        try:
            saved_path = self.pdf_manager.merge(output_path, strategy)
            self.after(0, lambda: self._merge_finished(True, f"Success! Saved to: {saved_path}"))
        except Exception as e:
            self.after(0, lambda: self._merge_finished(False, f"Error: {str(e)}"))
            
    @debug_trace
    def _merge_finished(self, success, message):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.merge_button.configure(state="normal")
        self.status_label.configure(text=message, text_color="green" if success else "red")