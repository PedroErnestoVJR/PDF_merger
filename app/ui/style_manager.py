import customtkinter as ctk
import json
import os
from app.core.debug import debug_trace

class StyleManager:
    CONFIG_FILE = "config.json"

    @classmethod
    @debug_trace
    def load_config(cls):
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"appearance_mode": "System"}

    @classmethod
    @debug_trace
    def save_config(cls, config):
        with open(cls.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    @classmethod
    @debug_trace
    def setup_initial_style(cls):
        """Sets the default theme and appearance mode at startup from config."""
        config = cls.load_config()
        mode = config.get("appearance_mode", "System")
        if mode == "Tonton":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")

    @classmethod
    @debug_trace
    def change_appearance_mode(cls, new_appearance_mode: str):
        """Changes between Light, Dark, and System modes and saves to config."""
        if new_appearance_mode == "Tonton":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode(new_appearance_mode)
        config = cls.load_config()
        config["appearance_mode"] = new_appearance_mode
        cls.save_config(config)

    @classmethod
    @debug_trace
    def get_current_mode(cls):
        return cls.load_config().get("appearance_mode", "System")