import os
import re
from typing import List, Dict
from src.llm.interfaces.prompt_provider import IPromptProvider, PromptConfig


class FilePromptProvider(IPromptProvider):
    """File-based prompt provider that loads prompts from .txt files"""

    def __init__(self, prompts_directory: str = "prompts"):
        self.prompts_directory = prompts_directory
        self._prompts_cache: Dict[str, PromptConfig] = {}
        self._load_prompts()

    def get_prompts(self) -> List[PromptConfig]:
        """Get all prompts sorted by processing order"""
        prompts = list(self._prompts_cache.values())
        return sorted(prompts, key=lambda p: p.order)

    def reload_prompts(self) -> None:
        """Reload prompts from filesystem"""
        self._prompts_cache.clear()
        self._load_prompts()

    def get_prompt_by_name(self, name: str) -> PromptConfig:
        """Get a specific prompt by name"""
        if name not in self._prompts_cache:
            raise KeyError(f"Prompt '{name}' not found")
        return self._prompts_cache[name]

    def _load_prompts(self) -> None:
        """Load all prompt files from the prompts directory"""
        if not os.path.exists(self.prompts_directory):
            print(f"⚠️ Prompts directory '{self.prompts_directory}' not found")
            return

        try:
            files = os.listdir(self.prompts_directory)
            txt_files = [f for f in files if f.endswith(".txt")]

            print(f"📁 Loading prompts from '{self.prompts_directory}/'")

            for filename in txt_files:
                try:
                    prompt_config = self._parse_prompt_file(filename)
                    if prompt_config:
                        self._prompts_cache[prompt_config.name] = prompt_config
                        print(
                            f"   ✅ Loaded: {filename} -> {prompt_config.name} (order: {prompt_config.order})"
                        )
                    else:
                        print(f"   ⚠️ Skipped: {filename} (invalid format)")
                except Exception as e:
                    print(f"   ❌ Failed to load {filename}: {e}")

            if not self._prompts_cache:
                print("⚠️ No valid prompts loaded")
            else:
                print(f"✅ Loaded {len(self._prompts_cache)} prompts")

        except Exception as e:
            print(f"❌ Failed to load prompts: {e}")

    def _parse_prompt_file(self, filename: str) -> PromptConfig:
        """Parse a prompt file and extract configuration"""
        # Parse filename format: 01_grammar_fix.txt, 99_custom_instructions.txt
        match = re.match(r"^(\d+)_(.+)\.txt$", filename)
        if not match:
            return None

        order_str, name_part = match.groups()
        order = int(order_str)

        # Convert filename to clean name (remove underscores, etc.)
        name = name_part.replace("_", " ").title().replace(" ", "")

        # Read file content
        filepath = os.path.join(self.prompts_directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except Exception as e:
            raise Exception(f"Failed to read {filepath}: {e}")

        if not content:
            raise Exception(f"Empty prompt file: {filepath}")

        # Determine if this is a conditional prompt
        conditional = name_part == "custom_instructions"

        # Check if this is a template (contains placeholders)
        template = "{" in content and "}" in content

        return PromptConfig(
            name=name,
            content=content,
            order=order,
            enabled=True,
            conditional=conditional,
            template=template,
        )


class MockPromptProvider(IPromptProvider):
    """Mock prompt provider for testing"""

    def __init__(self):
        self._mock_prompts = [
            PromptConfig(
                name="TextRewriter",
                content="You are a text processing system that transforms raw speech-to-text transcriptions into clean, readable text. Remove filler words, add proper formatting, and fix grammar while preserving the speaker's intended meaning. Return only the processed text without explanations.",
                order=1,
                enabled=True,
                conditional=False,
                template=False,
            )
        ]

    def get_prompts(self) -> List[PromptConfig]:
        """Get mock prompts"""
        return sorted(self._mock_prompts, key=lambda p: p.order)

    def reload_prompts(self) -> None:
        """Mock reload - no-op"""
        print("🔄 Mock prompt provider: reload_prompts called")

    def get_prompt_by_name(self, name: str) -> PromptConfig:
        """Get mock prompt by name"""
        for prompt in self._mock_prompts:
            if prompt.name == name:
                return prompt
        raise KeyError(f"Mock prompt '{name}' not found")
