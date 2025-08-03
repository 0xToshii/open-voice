import platform
from typing import Optional
from src.interfaces.text_insertion import ITextInserter
from src.services.cross_platform_inserter import CrossPlatformTextInserter


class TextInserterFactory:
    """Factory for creating the best available text inserter"""

    @staticmethod
    def create_best_inserter() -> ITextInserter:
        """
        Create the best available text inserter for the current platform

        Returns:
            ITextInserter: The best available text insertion implementation
        """
        current_platform = platform.system()

        # Try platform-specific implementations first
        if current_platform == "Darwin":  # macOS
            inserter = TextInserterFactory._try_mac_native_inserter()
            if inserter:
                return inserter

        # Fallback to cross-platform implementation
        return TextInserterFactory._create_cross_platform_inserter()

    @staticmethod
    def _try_mac_native_inserter() -> Optional[ITextInserter]:
        """
        Try to create a Mac-native text inserter using PyObjC

        Returns:
            ITextInserter or None: Mac-native inserter if available, None otherwise
        """
        try:
            # Future implementation: Import and test Mac-native inserter
            # from src.services.mac_native_inserter import MacNativeTextInserter
            # inserter = MacNativeTextInserter()
            # if inserter.is_available():
            #     print("✅ Using Mac-native text insertion (PyObjC)")
            #     return inserter

            # For now, this is not implemented
            print("🔄 Mac-native text insertion not yet implemented")
            return None

        except ImportError:
            print("⚠️ PyObjC not available, using cross-platform insertion")
            return None
        except Exception as e:
            print(f"⚠️ Mac-native text insertion failed to initialize: {e}")
            return None

    @staticmethod
    def _create_cross_platform_inserter() -> ITextInserter:
        """
        Create cross-platform text inserter (clipboard-only for simplicity)

        Returns:
            ITextInserter: Cross-platform text inserter
        """
        inserter = CrossPlatformTextInserter(method="clipboard")

        if inserter.is_available():
            print("✅ Using clipboard-only text insertion (simple and reliable)")
            capabilities = inserter.get_capabilities()
            print(f"   Method: {capabilities['method']}")
            print(f"   Platform: {capabilities['platform']}")
        else:
            print("❌ Warning: Clipboard text insertion may not work properly")

        return inserter

    @staticmethod
    def create_specific_inserter(inserter_type: str) -> Optional[ITextInserter]:
        """
        Create a specific type of text inserter

        Args:
            inserter_type: Type of inserter ("cross-platform", "mac-native")

        Returns:
            ITextInserter or None: Requested inserter if available, None otherwise
        """
        if inserter_type == "cross-platform":
            return TextInserterFactory._create_cross_platform_inserter()
        elif inserter_type == "mac-native":
            return TextInserterFactory._try_mac_native_inserter()
        else:
            print(f"❌ Unknown inserter type: {inserter_type}")
            return None

    @staticmethod
    def list_available_inserters() -> list:
        """
        Get list of available text inserters on current platform

        Returns:
            list: List of available inserter names
        """
        available = []

        # Cross-platform is always available (may not work, but exists)
        available.append("cross-platform")

        # Check Mac-native availability
        if platform.system() == "Darwin":
            mac_inserter = TextInserterFactory._try_mac_native_inserter()
            if mac_inserter:
                available.append("mac-native")

        return available

    @staticmethod
    def get_recommended_inserter() -> str:
        """
        Get the recommended inserter type for current platform

        Returns:
            str: Recommended inserter type
        """
        current_platform = platform.system()

        if current_platform == "Darwin":  # macOS
            # Check if Mac-native is available
            if TextInserterFactory._try_mac_native_inserter():
                return "mac-native"

        return "cross-platform"


class MockTextInserter(ITextInserter):
    """Mock text inserter for testing without actual insertion"""

    def __init__(self):
        self.inserted_texts = []  # Store inserted texts for testing

    def insert_text(self, text: str) -> bool:
        """Mock text insertion - just store the text"""
        print(f"🧪 Mock text insertion: '{text}'")
        self.inserted_texts.append(text)
        return True

    def is_available(self) -> bool:
        """Mock is always available"""
        return True

    def get_capabilities(self) -> dict:
        """Get mock capabilities"""
        return {
            "name": self.get_name(),
            "platform": "mock",
            "method": "simulation",
            "supports_long_text": True,
            "supports_special_chars": True,
            "supports_unicode": True,
            "advanced_features": False,
            "requires_permissions": False,
        }

    def get_name(self) -> str:
        """Get mock inserter name"""
        return "MockInserter"

    def get_inserted_texts(self) -> list:
        """Get all texts that were 'inserted' for testing"""
        return self.inserted_texts.copy()

    def clear_history(self):
        """Clear insertion history"""
        self.inserted_texts.clear()
