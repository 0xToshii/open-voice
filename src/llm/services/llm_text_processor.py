from src.interfaces.text_processing import ITextProcessor
from src.llm.interfaces.llm_client import ILLMClient
from src.llm.interfaces.prompt_provider import IPromptProvider
from src.interfaces.settings import ISettingsManager


class LLMTextProcessor(ITextProcessor):
    """LLM-powered text processor that applies a pipeline of prompts"""

    def __init__(
        self,
        llm_client: ILLMClient,
        prompt_provider: IPromptProvider,
        settings_manager: ISettingsManager,
    ):
        self.llm_client = llm_client
        self.prompt_provider = prompt_provider
        self.settings_manager = settings_manager

    def process_text(self, text: str) -> str:
        """Process text through single LLM call with optional custom instructions"""
        if not text or not text.strip():
            return text

        # Store original text for fallback
        original_text = text.strip()

        print(f"🔄 LLM Single-Call: Starting text processing")
        print(f"   Input: '{original_text}'")

        # Check if LLM is available
        if not self.llm_client.is_available():
            print("⚠️ LLM client not available, returning original text")
            return original_text

        try:
            # Load the base text rewriter prompt
            try:
                base_prompt_config = self.prompt_provider.get_prompt_by_name(
                    "TextRewriter"
                )
                base_prompt = base_prompt_config.content
                print("✅ Loaded base text rewriter prompt")
            except KeyError:
                print("❌ TextRewriter prompt not found, returning original text")
                return original_text

            # Check for custom instructions and append if present
            custom_instructions = self.settings_manager.get_custom_instructions()
            if custom_instructions and custom_instructions.strip():
                custom_section = f"\n\n## Additional Instructions\n\nAlso apply the following custom user preferences / instructions to the text: {custom_instructions}"
                final_prompt = base_prompt + custom_section
                print(
                    f"✅ Added custom instructions: '{custom_instructions[:50]}{'...' if len(custom_instructions) > 50 else ''}'"
                )
            else:
                final_prompt = base_prompt
                print("ℹ️ No custom instructions provided")

            print("🧠 Making single LLM call...")

            # Single LLM call
            try:
                processed_text = self.llm_client.generate(final_prompt, original_text)

                if processed_text and processed_text.strip():
                    result = processed_text.strip()
                    print(
                        f"✅ LLM processing complete: '{result[:50]}{'...' if len(result) > 50 else ''}'"
                    )
                    return result
                else:
                    print("⚠️ Empty response from LLM, returning original text")
                    return original_text

            except Exception as e:
                print(f"❌ LLM call failed: {e}")
                print(f"🚨 Returning original text due to LLM failure")
                return original_text

        except Exception as e:
            print(f"❌ LLM processing unexpected error: {e}")
            print(f"🚨 Returning original text due to processing failure")
            return original_text

    def get_processing_info(self) -> dict:
        """Get information about the current LLM processing configuration"""
        try:
            custom_instructions = self.settings_manager.get_custom_instructions()
            has_custom_instructions = bool(
                custom_instructions and custom_instructions.strip()
            )

            return {
                "llm_client": self.llm_client.get_model_info(),
                "base_prompt": "TextRewriter",
                "has_custom_instructions": has_custom_instructions,
                "custom_instructions_preview": (
                    custom_instructions[:100] if has_custom_instructions else None
                ),
                "processing_type": "single_call",
            }
        except Exception as e:
            return {
                "error": str(e),
                "llm_client": "unknown",
                "processing_type": "single_call",
                "has_custom_instructions": False,
            }


class PassthroughTextProcessor(ITextProcessor):
    """Simple passthrough processor that doesn't modify text"""

    def process_text(self, text: str) -> str:
        """Return text as-is with basic cleanup"""
        print("📝 Passthrough processor: No LLM processing")
        return text.strip() if text else ""
