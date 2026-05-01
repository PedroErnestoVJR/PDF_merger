import customtkinter as ctk
import shutil
import webbrowser
import subprocess
from app.ui.style_manager import StyleManager
from app.core.debug import debug_trace

class PyPDFSettingsWindow(ctk.CTkToplevel):
    @debug_trace
    def __init__(self, master, strategy, **kwargs):
        super().__init__(master, **kwargs)
        self.title("PyPDF Settings")
        self.geometry("380x360")
        self.strategy = strategy
        
        self.pwd_label = ctk.CTkLabel(self, text="Protect Output PDF (Optional):")
        self.pwd_label.pack(pady=(15, 5), padx=20, anchor="w")
        
        self.password_var = ctk.StringVar(value=self.strategy.password)
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, show="*", placeholder_text="Enter password")
        self.password_entry.pack(pady=5, padx=20, fill="x")

        self.title_label = ctk.CTkLabel(self, text="Document Title (Metadata):")
        self.title_label.pack(pady=(10, 5), padx=20, anchor="w")
        self.title_var = ctk.StringVar(value=self.strategy.title)
        self.title_entry = ctk.CTkEntry(self, textvariable=self.title_var, placeholder_text="Enter title")
        self.title_entry.pack(pady=5, padx=20, fill="x")

        self.author_label = ctk.CTkLabel(self, text="Document Author (Metadata):")
        self.author_label.pack(pady=(10, 5), padx=20, anchor="w")
        self.author_var = ctk.StringVar(value=self.strategy.author)
        self.author_entry = ctk.CTkEntry(self, textvariable=self.author_var, placeholder_text="Enter author")
        self.author_entry.pack(pady=5, padx=20, fill="x")
        
        self.compress_var = ctk.BooleanVar(value=self.strategy.lossless_compression)
        self.compress_switch = ctk.CTkSwitch(self, text="Enable Lossless Compression", variable=self.compress_var)
        self.compress_switch.pack(pady=(10, 5), padx=20, anchor="w")

        self.save_button = ctk.CTkButton(self, text="Save", command=self.save)
        self.save_button.pack(pady=15)
        
        if StyleManager.get_current_mode() == "Tonton":
            self.configure(fg_color="#FCE4EC")
            for lbl in [self.pwd_label, self.title_label, self.author_label]:
                lbl.configure(text_color="#880E4F")
            for entry in [self.password_entry, self.title_entry, self.author_entry]:
                entry.configure(fg_color="#F8BBD0", text_color="#880E4F", border_color="#F06292")
            self.compress_switch.configure(text_color="#880E4F", progress_color="#F06292", button_color="#E91E63", button_hover_color="#C2185B")
            self.save_button.configure(fg_color="#F06292", hover_color="#E91E63", text_color="white")

        # Make window modal
        self.grab_set()
        self.lift()

    @debug_trace
    def save(self):
        self.strategy.password = self.password_var.get()
        self.strategy.title = self.title_var.get()
        self.strategy.author = self.author_var.get()
        self.strategy.lossless_compression = self.compress_var.get()
        self.destroy()

class GhostscriptSettingsWindow(ctk.CTkToplevel):
    @debug_trace
    def __init__(self, master, strategy, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Ghostscript Settings")
        self.geometry("420x510")
        self.strategy = strategy
        
        gs_cmd = shutil.which('gswin64c') or shutil.which('gswin32c') or shutil.which('gs')
        
        gs_working = False
        if gs_cmd:
            try:
                subprocess.run([gs_cmd, '--version'], check=True, capture_output=True)
                gs_working = True
            except (OSError, subprocess.CalledProcessError):
                gs_working = False

        if not gs_working:
            self.warning_label = ctk.CTkLabel(self, text="⚠️ Ghostscript not found or incompatible!\nClick here to download for Windows.", text_color="#D32F2F", font=ctk.CTkFont(weight="bold", underline=True), cursor="hand2")
            self.warning_label.pack(pady=(15, 0), padx=20)
            self.warning_label.bind("<Button-1>", lambda e: webbrowser.open("https://ghostscript.com/releases/gsdnld.html"))

        self.label_quality = ctk.CTkLabel(self, text="Output Quality Profile:")
        self.label_quality.pack(pady=(15, 5), padx=20, anchor="w")
        
        self.settings_var = ctk.StringVar(value=self.strategy.pdf_settings)
        self.dropdown = ctk.CTkOptionMenu(
            self, 
            variable=self.settings_var, 
            values=["/default", "/screen", "/ebook", "/printer", "/prepress"],
            command=self.update_help_text
        )
        self.dropdown.pack(pady=5, padx=20, fill="x")
        
        self.help_label = ctk.CTkLabel(self, text="", justify="left", wraplength=380)
        self.help_label.pack(pady=(0, 10), padx=20, anchor="w", fill="x")

        self.label_compat = ctk.CTkLabel(self, text="Compatibility Level:")
        self.label_compat.pack(pady=(5, 0), padx=20, anchor="w")
        self.compat_var = ctk.StringVar(value=self.strategy.compatibility_level)
        self.compat_dropdown = ctk.CTkOptionMenu(self, variable=self.compat_var, values=["1.4", "1.5", "1.6", "1.7"])
        self.compat_dropdown.pack(pady=5, padx=20, fill="x")
        
        self.help_compat = ctk.CTkLabel(self, text="Versão do PDF (Ex: 1.4 = Acrobat 5).", justify="left", text_color="gray")
        self.help_compat.pack(pady=(0, 10), padx=20, anchor="w", fill="x")

        self.label_color = ctk.CTkLabel(self, text="Color Conversion:")
        self.label_color.pack(pady=(5, 0), padx=20, anchor="w")
        self.color_var = ctk.StringVar(value=self.strategy.color_conversion)
        self.color_dropdown = ctk.CTkOptionMenu(self, variable=self.color_var, values=["LeaveColorUnchanged", "Gray", "RGB", "CMYK"])
        self.color_dropdown.pack(pady=5, padx=20, fill="x")
        
        self.help_color = ctk.CTkLabel(self, text="Modo de cor (ex: 'Gray' para salvar em Preto e Branco).", justify="left", text_color="gray")
        self.help_color.pack(pady=(0, 10), padx=20, anchor="w", fill="x")
        
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save)
        self.save_button.pack(pady=15)
        
        self.update_help_text(self.strategy.pdf_settings)
        
        if StyleManager.get_current_mode() == "Tonton":
            self.configure(fg_color="#FCE4EC")
            for lbl in [self.label_quality, self.help_label, self.label_compat, self.help_compat, self.label_color, self.help_color]:
                lbl.configure(text_color="#880E4F")
            for dropdown in [self.dropdown, self.compat_dropdown, self.color_dropdown]:
                dropdown.configure(fg_color="#F06292", button_color="#E91E63", button_hover_color="#C2185B", text_color="white")
            self.save_button.configure(fg_color="#F06292", hover_color="#E91E63", text_color="white")

        self.grab_set()
        self.lift()

    @debug_trace
    def update_help_text(self, choice):
        help_texts = {
            "/default": "Configuração padrão. Uso geral.\nExemplo: Mesclar arquivos mantendo a estrutura padrão sem focar em reduzir tamanho.",
            "/screen": "Qualidade baixa (72 dpi). Menor tamanho de arquivo.\nExemplo: Arquivos leves ideais para enviar rapidamente por e-mail.",
            "/ebook": "Qualidade média (150 dpi). Bom equilíbrio.\nExemplo: PDFs para leitura confortável em tablets, monitores e e-readers.",
            "/printer": "Alta resolução (300 dpi). Ideal para impressão.\nExemplo: Imprimir relatórios e documentos em impressoras de escritório.",
            "/prepress": "Qualidade máxima (300 dpi) e preservação de cores.\nExemplo: Envio de arquivos de alta fidelidade para gráficas comerciais profissionais."
        }
        self.help_label.configure(text=help_texts.get(choice, ""))

    @debug_trace
    def save(self):
        self.strategy.pdf_settings = self.settings_var.get()
        self.strategy.compatibility_level = self.compat_var.get()
        self.strategy.color_conversion = self.color_var.get()
        self.destroy()