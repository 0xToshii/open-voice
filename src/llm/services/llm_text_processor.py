from src.interfaces.text_processing import ITextProcessor
from src.llm.interfaces.llm_router import ILLMRouter
from src.llm.services.prompt_loader import SimplePromptLoader
from src.interfaces.settings import ISettingsManager


class LLMTextProcessor(ITextProcessor):
    """LLM-powered text processor with dynamic LLM routing"""

    def __init__(
        self,
        llm_router: ILLMRouter,
        settings_manager: ISettingsManager,
        prompt_loader: SimplePromptLoader = None,
    ):
        self.llm_router = llm_router
        self.settings_manager = settings_manager
        self.prompt_loader = prompt_loader or SimplePromptLoader()

    def process_text(self, text: str) -> str:
        """Process text through single LLM call with optional custom instructions"""
        if not text or not text.strip():
            return text

        # Store original text for fallback
        original_text = text.strip()

        print(f"LLM Single-Call: Starting text processing")
        print(f"   Input: '{original_text}'")

        # Check if LLM router is available
        if not self.llm_router.is_available():
            print("LLM router not available, returning original text")
            return original_text

        try:
            # Load the base text rewriter prompt
            try:
                base_prompt = self.prompt_loader.get_transcription_prompt()
            except Exception as e:
                print(f"Failed to load transcription prompt: {e}")
                return original_text

            # Check for custom instructions and append if present
            custom_instructions = self.settings_manager.get_custom_instructions()
            if custom_instructions and custom_instructions.strip():
                custom_section = f"\n\n## Additional Instructions\n\nAlso apply the following custom user preferences / instructions to the text: {custom_instructions}"
                final_prompt = base_prompt + custom_section
                print(
                    f"Added custom instructions: '{custom_instructions[:50]}{'...' if len(custom_instructions) > 50 else ''}'"
                )
            else:
                final_prompt = base_prompt
                print("No custom instructions provided")

            print("Making LLM router call...")

            # Single LLM call through router (with automatic fallback)
            processed_text = self.llm_router.process_with_best_llm(
                final_prompt, original_text
            )

            # Log which LLM was actually used
            llm_info = self.llm_router.get_last_used_llm_info()
            if llm_info["success"]:
                print(f"Used LLM: {llm_info['provider']} ({llm_info['model']})")
            else:
                print(f"LLM failed: {llm_info.get('error', 'Unknown error')}")

            if (
                processed_text
                and processed_text.strip()
                and processed_text != original_text
            ):
                result = processed_text.strip()
                print(
                    f"LLM processing complete: '{result[:50]}{'...' if len(result) > 50 else ''}'"
                )
                return result
            else:
                print("LLM returned original text, no processing applied")
                return original_text

        except Exception as e:
            print(f"LLM processing unexpected error: {e}")
            print(f"Returning original text due to processing failure")
            return original_text

    def get_processing_info(self) -> dict:
        """Get information about the current LLM processing configuration"""
        try:
            custom_instructions = self.settings_manager.get_custom_instructions()
            has_custom_instructions = bool(
                custom_instructions and custom_instructions.strip()
            )

            # Get router info
            available_llms = self.llm_router.get_available_llms()
            last_used_llm = self.llm_router.get_last_used_llm_info()

            return {
                "llm_router": {
                    "available_llms": available_llms,
                    "last_used_llm": last_used_llm,
                    "router_available": self.llm_router.is_available(),
                },
                "base_prompt": "TranscriptionRewrite",
                "has_custom_instructions": has_custom_instructions,
                "custom_instructions_preview": (
                    custom_instructions[:100] if has_custom_instructions else None
                ),
                "processing_type": "single_call_with_router",
            }
        except Exception as e:
            return {
                "error": str(e),
                "llm_router": "unknown",
                "processing_type": "single_call_with_router",
                "has_custom_instructions": False,
            }


class PassthroughTextProcessor(ITextProcessor):
    """Simple passthrough processor that doesn't modify text"""

    def process_text(self, text: str) -> str:
        """Return text as-is with basic cleanup"""
        print("Passthrough processor: No LLM processing")
        return text.strip() if text else ""
