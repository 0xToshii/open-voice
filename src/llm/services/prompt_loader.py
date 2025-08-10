import os


class SimplePromptLoader:
    """Simple prompt loader for transcription rewriting"""

    def __init__(self, prompts_directory: str = "prompts"):
        self.prompts_directory = prompts_directory

    def get_transcription_prompt(self) -> str:
        """Load the transcription rewrite prompt"""
        prompt_path = os.path.join(self.prompts_directory, "transcription_rewrite.md")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read().strip()

            if not prompt:
                raise Exception(f"Empty prompt file: {prompt_path}")

            print(f"Loaded transcription prompt from {prompt_path}")
            return prompt

        except FileNotFoundError:
            raise Exception(f"Transcription prompt file not found: {prompt_path}")
        except Exception as e:
            raise Exception(f"Failed to load transcription prompt: {e}")
