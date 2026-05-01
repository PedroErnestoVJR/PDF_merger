import customtkinter as ctk
from app.ui.style_manager import StyleManager
from app.core.debug import debug_trace

class ExplorerFrame(ctk.CTkFrame):
    @debug_trace
    def __init__(self, master, select_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="File Explorer", font=ctk.CTkFont(weight="bold"))
        self.label.pack(pady=10, padx=10, anchor="w")
        
        self.select_button = ctk.CTkButton(self, text="Select PDF Files", command=select_callback)
        self.select_button.pack(pady=10, padx=10, fill="x")

class WorkspaceFrame(ctk.CTkFrame):
    @debug_trace
    def __init__(self, master, remove_callback, move_up_callback, move_down_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.remove_callback = remove_callback
        self.move_up_callback = move_up_callback
        self.move_down_callback = move_down_callback
        
        self.label = ctk.CTkLabel(self, text="Files to Merge (Order Matters)", font=ctk.CTkFont(weight="bold"))
        self.label.pack(pady=10, padx=10, anchor="w")
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        self.file_widgets = []

    @debug_trace
    def update_list(self, files):
        # Clear existing widgets
        for widget in self.file_widgets:
            widget.destroy()
        self.file_widgets.clear()
        
        # Re-populate the list
        is_tonton = StyleManager.get_current_mode() == "Tonton"
        text_color = "#880E4F" if is_tonton else ("gray10", "gray90")
        btn_color = "#F06292" if is_tonton else ("#3B8ED0", "#1F6AA5")
        btn_hover = "#E91E63" if is_tonton else ("#36719F", "#144870")

        for idx, file_path in enumerate(files):
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(row_frame, text=file_path, anchor="w", width=300)
            lbl.configure(text_color=text_color)
            lbl.pack(side="left", padx=5, fill="x", expand=True)
            
            btn_up = ctk.CTkButton(row_frame, text="↑", width=30, command=lambda i=idx: self.move_up_callback(i))
            btn_up.configure(fg_color=btn_color, hover_color=btn_hover)
            btn_up.pack(side="left", padx=2)
            
            btn_down = ctk.CTkButton(row_frame, text="↓", width=30, command=lambda i=idx: self.move_down_callback(i))
            btn_down.configure(fg_color=btn_color, hover_color=btn_hover)
            btn_down.pack(side="left", padx=2)
            
            btn_rem = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#C62828", hover_color="#B71C1C", command=lambda f=file_path: self.remove_callback(f))
            btn_rem.pack(side="right", padx=5)
            
            self.file_widgets.append(row_frame)