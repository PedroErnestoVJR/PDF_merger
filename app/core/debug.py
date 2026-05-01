import functools
import customtkinter as ctk

class Debug:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Debug, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.window = None
            cls._instance.textbox = None
        return cls._instance

    def open_window(self, master=None):
        if self.window is None or not self.window.winfo_exists():
            self.window = ctk.CTkToplevel(master)
            self.window.title("Debug Console")
            self.window.geometry("800x600")
            
            self.textbox = ctk.CTkTextbox(self.window, state="disabled", font=("Consolas", 12))
            self.textbox.pack(expand=True, fill="both", padx=5, pady=5)
            self.textbox.configure(fg_color="#1E1E1E", text_color="#00FF00")
            
            self.textbox.configure(state="normal")
            for msg in self.logs:
                self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")
        else:
            self.window.lift()

    def log(self, message):
        self.logs.append(message)
        if self.window and self.window.winfo_exists() and self.textbox:
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")

    def error(self, message):
        self.log(f"[ERROR]   {message}")

    def info(self, message):
        self.log(f"[INFO]    {message}")

def debug_trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        debug = Debug()
        try:
            # Limit the output length to avoid console hanging on large objects
            args_repr = [repr(a)[:150] + ('...' if len(repr(a)) > 150 else '') for a in args]
            kwargs_repr = [f"{k}={repr(v)[:150] + ('...' if len(repr(v)) > 150 else '')}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
        except Exception:
            signature = "<Failed to parse signature>"
        
        debug.info(f"CALL: {func.__qualname__}({signature})")
        try:
            result = func(*args, **kwargs)
            try:
                res_repr = repr(result)[:150] + ('...' if len(repr(result)) > 150 else '')
            except Exception:
                res_repr = "<Failed to parse result>"
            debug.info(f"RETURN: {func.__qualname__} -> {res_repr}")
            return result
        except Exception as e:
            import traceback
            debug.error(f"EXCEPTION in {func.__qualname__}:\n{traceback.format_exc()}")
            raise
    return wrapper