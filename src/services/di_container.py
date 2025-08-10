from typing import Optional
from src.interfaces.speech_factory import ISpeechEngineRegistry
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager
from src.interfaces.data_store import IDataStore
from src.interfaces.hotkey import IHotkeyHandler
from src.interfaces.text_processing import ITextProcessor
from src.interfaces.audio_recorder import IAudioRecorder
from src.services.speech_registry import SpeechEngineRegistry
from src.engines.speech_factories import (
    OpenAISpeechFactory,
    GroqSpeechFactory,
    LocalWhisperFactory,
)
from src.services.recording_service import VoiceRecordingService
from src.services.settings_manager import SettingsManager
from src.data.mock_data_store import MockDataStore
from src.data.sqlite_data_store import SQLiteDataStore
from src.services.text_processor import TextProcessor
from src.services.audio_recorder import PyAudioRecorder, MockAudioRecorder
from src.services.hotkey_handler import CmdOptionHandler, MockHotkeyHandler

# LLM Pipeline imports
from src.llm.interfaces.llm_client import ILLMClient
from src.llm.interfaces.llm_router import ILLMRouter
from src.llm.clients.openai_client import OpenAILLMClient
from src.llm.clients.groq_client import GroqLLMClient
from src.llm.clients.passthrough_client import PassthroughLLMClient
from src.llm.services.llm_router import LLMRouter
from src.llm.services.llm_text_processor import (
    LLMTextProcessor,
    PassthroughTextProcessor,
)

# Speech Router imports
from src.interfaces.speech_router import ISpeechEngineRouter
from src.services.speech_engine_router import SpeechEngineRouter


class DIContainer:
    """Dependency Injection Container for managing application dependencies"""

    def __init__(self):
        # Singletons
        self._settings_manager: Optional[ISettingsManager] = None
        self._data_store: Optional[IDataStore] = None
        self._text_processor: Optional[ITextProcessor] = None
        self._speech_registry: Optional[ISpeechEngineRegistry] = None
        self._audio_recorder: Optional[IAudioRecorder] = None
        self._hotkey_handler: Optional[IHotkeyHandler] = None

        # LLM Pipeline singletons
        self._llm_client: Optional[ILLMClient] = None
        self._llm_router: Optional[ILLMRouter] = None

        # Speech Router singleton
        self._speech_router: Optional[ISpeechEngineRouter] = None

        # Configuration flags
        self._use_mock_audio = False
        self._use_mock_hotkey = False
        self._use_mock_llm = False

    def configure_for_testing(
        self,
        use_mock_audio: bool = True,
        use_mock_hotkey: bool = True,
        use_mock_llm: bool = True,
    ):
        """Configure container to use mock implementations for testing"""
        self._use_mock_audio = use_mock_audio
        self._use_mock_hotkey = use_mock_hotkey
        self._use_mock_llm = use_mock_llm

    def get_settings_manager(self) -> ISettingsManager:
        """Get settings manager singleton"""
        if self._settings_manager is None:
            self._settings_manager = SettingsManager()
        return self._settings_manager

    def get_data_store(self) -> IDataStore:
        """Get data store singleton"""
        if self._data_store is None:
            self._data_store = SQLiteDataStore()
        return self._data_store

    def get_llm_client(self) -> ILLMClient:
        """Get LLM client based on selected provider"""
        if self._llm_client is None:
            if self._use_mock_llm:
                print("Using passthrough LLM client for testing")
                self._llm_client = PassthroughLLMClient()
            else:
                settings = self.get_settings_manager()
                selected_provider = settings.get_selected_provider()

                if selected_provider == "openai":
                    self._llm_client = OpenAILLMClient(settings)
                    print(f"Using OpenAI LLM client")
                elif selected_provider == "groq":
                    self._llm_client = GroqLLMClient(settings)
                    print(f"Using Groq LLM client")
                elif selected_provider == "local":
                    self._llm_client = PassthroughLLMClient()
                    print("Using passthrough LLM client (local provider)")
                else:
                    raise Exception(f"Unknown provider: {selected_provider}")
        return self._llm_client

    def get_llm_router(self) -> ILLMRouter:
        """Get LLM router with provider-based selection"""
        if self._llm_router is None:
            settings_manager = self.get_settings_manager()
            self._llm_router = LLMRouter(settings_manager=settings_manager)
            print("Using provider-based LLM router")

        return self._llm_router

    def get_text_processor(self) -> ITextProcessor:
        """Get text processor with LLM router pipeline"""
        if self._text_processor is None:
            llm_router = self.get_llm_router()
            settings = self.get_settings_manager()

            self._text_processor = LLMTextProcessor(
                llm_router=llm_router,
                settings_manager=settings,
            )
            print("Using LLM text processor with simple prompt loader")

        return self._text_processor

    def get_speech_router(self) -> ISpeechEngineRouter:
        """Get speech engine router with provider-based selection"""
        if self._speech_router is None:
            speech_registry = self.get_speech_registry()
            settings_manager = self.get_settings_manager()

            self._speech_router = SpeechEngineRouter(
                speech_registry=speech_registry, settings_manager=settings_manager
            )
            print("Using provider-based speech engine router")

        return self._speech_router

    def get_speech_registry(self) -> ISpeechEngineRegistry:
        """Get speech engine registry singleton with registered engines"""
        if self._speech_registry is None:
            self._speech_registry = SpeechEngineRegistry()
            self._register_speech_engines()
        return self._speech_registry

    def get_audio_recorder(self) -> IAudioRecorder:
        """Get audio recorder (mock or real based on configuration)"""
        if self._audio_recorder is None:
            if self._use_mock_audio:
                print("Using mock audio recorder")
                self._audio_recorder = MockAudioRecorder()
            else:
                self._audio_recorder = PyAudioRecorder()
                print("Using real audio recorder")
        return self._audio_recorder

    def get_hotkey_handler(self) -> IHotkeyHandler:
        """Get hotkey handler (mock or real based on configuration)"""
        if self._hotkey_handler is None:
            if self._use_mock_hotkey:
                print("Using mock hotkey handler")
                self._hotkey_handler = MockHotkeyHandler()
            else:
                self._hotkey_handler = CmdOptionHandler()
                print("Using Cmd+Option hotkey handler")
        return self._hotkey_handler

    def get_speech_engine(self) -> ISpeechEngine:
        """Get the best available speech engine"""
        registry = self.get_speech_registry()
        settings = self.get_settings_manager()
        return registry.create_best_engine(settings)

    def get_recording_service(self) -> VoiceRecordingService:
        """Get recording service with all dependencies injected"""
        return VoiceRecordingService(
            speech_router=self.get_speech_router(),
            data_store=self.get_data_store(),
            hotkey_handler=self.get_hotkey_handler(),
            text_processor=self.get_text_processor(),
            audio_recorder=self.get_audio_recorder(),
        )

    def _register_speech_engines(self):
        """Register all available speech engines with priorities"""
        registry = self._speech_registry

        # Register engines with priorities (higher = preferred)
        # OpenAI Speech has highest priority when available
        registry.register_engine(
            name="openai", factory=OpenAISpeechFactory(), priority=100
        )

        # Groq Speech as high priority alternative
        registry.register_engine(name="groq", factory=GroqSpeechFactory(), priority=90)

        # Local Whisper as additional fallback (no internet required)
        registry.register_engine(
            name="local_whisper", factory=LocalWhisperFactory(), priority=10
        )

    def create_speech_engine_by_name(self, engine_name: str) -> ISpeechEngine:
        """Create a specific speech engine by name"""
        registry = self.get_speech_registry()
        settings = self.get_settings_manager()
        return registry.create_engine_by_name(engine_name, settings)

    def get_available_speech_engines(self) -> list:
        """Get list of available speech engines"""
        registry = self.get_speech_registry()
        settings = self.get_settings_manager()
        return registry.get_available_engines(settings)

    def init_critical_services(self):
        """Initialize all performance-critical services at startup"""
        print("Initializing critical services...")

        # Core recording pipeline - must be instant when user hits hotkey
        print("  - Audio recorder...")
        self.get_audio_recorder()

        print("  - Speech router...")
        self.get_speech_router()

        print("  - Speech registry...")
        self.get_speech_registry()

        print("  - Hotkey handler...")
        self.get_hotkey_handler()

        print("  - Text processor...")
        self.get_text_processor()

        print("Critical services initialized successfully")

    def reset(self):
        """Reset all singletons (useful for testing)"""
        self._settings_manager = None
        self._data_store = None
        self._text_processor = None
        self._speech_registry = None
        self._audio_recorder = None
        self._hotkey_handler = None
        self._llm_client = None
        self._llm_router = None
        self._speech_router = None
        print("DI Container reset")
