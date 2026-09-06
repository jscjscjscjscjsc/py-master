import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import setup_api


class FirstRunSetupTests(unittest.TestCase):
    def test_first_run_collects_model_url_and_key(self):
        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / '.env'
            answers = iter(['custom-model', 'https://example.com/api/v3', 'backup-model'])
            with patch.object(setup_api, 'ROOT', Path(folder)), \
                 patch.object(setup_api, 'ENV_FILE', env_file), \
                 patch('builtins.input', side_effect=lambda _: next(answers)), \
                 patch.object(setup_api, 'getpass', return_value='test-secret'):
                self.assertTrue(setup_api.prompt_setup())
            text = env_file.read_text(encoding='utf-8')
            self.assertIn('PYMASTER_AI_MODEL=custom-model', text)
            self.assertIn('PYMASTER_AI_BASE_URL=https://example.com/api/v3', text)
            self.assertIn('ARK_API_KEY=test-secret', text)
            self.assertIn('PYMASTER_AI_FALLBACK_MODELS=backup-model', text)

    def test_rejects_missing_key(self):
        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / '.env'
            answers = iter(['', '', ''])
            with patch.object(setup_api, 'ROOT', Path(folder)), \
                 patch.object(setup_api, 'ENV_FILE', env_file), \
                 patch('builtins.input', side_effect=lambda _: next(answers)), \
                 patch.object(setup_api, 'getpass', return_value=''):
                self.assertFalse(setup_api.prompt_setup())
                self.assertFalse(env_file.exists())


if __name__ == '__main__':
    unittest.main()
