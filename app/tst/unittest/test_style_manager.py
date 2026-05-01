import unittest
from unittest.mock import patch, mock_open
from app.ui.style_manager import StyleManager

class TestStyleManager(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"appearance_mode": "Dark"}')
    def test_load_config(self, mock_file, mock_exists):
        config = StyleManager.load_config()
        self.assertEqual(config, {"appearance_mode": "Dark"})

    @patch('app.ui.style_manager.StyleManager.load_config', return_value={"appearance_mode": "System"})
    @patch('app.ui.style_manager.StyleManager.save_config')
    @patch('app.ui.style_manager.ctk.set_appearance_mode')
    def test_change_appearance_mode(self, mock_set_mode, mock_save, mock_load):
        # Test standard mode
        StyleManager.change_appearance_mode("Dark")
        mock_set_mode.assert_called_with("Dark")
        
        # Test Tonton theme mode override
        StyleManager.change_appearance_mode("Tonton")
        mock_set_mode.assert_called_with("Light")