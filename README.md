# Open Voice

A speech-to-text application for macOS that allows you to dictate into any application using global hotkeys and AI-enhanced text processing.

## More Info

Open Voice is a Mac desktop application that transforms speech into text and intelligently inserts it into any application you're using. Simply press **Cmd+Option**, speak naturally, and watch your words appear in your current text field with AI-powered enhancements. 

It's currently implemented using the OpenAI Whisper endpoint, with Google Speech as the backup. Cerebras is used for fast LLM post-processing of the transcription. It's heavily influenced by Aqua Voice - but the idea here is that you can have the same experience while enjoying BYOK / pay-as-you-go pricing. Ideally in the future there will only be a single api to configure. Also, the current implementation isn't feature-complete, UI is clunky, and the setup is too tedious. A one click install would be much preferred.

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/0xToshii/open-voice.git
   cd open-voice
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Grant permissions when prompted:**
   - Microphone access
   - Accessibility permissions

### Basic Usage

1. **Start the app** - The GUI will open with settings and transcript history
2. **Press and hold Cmd+Option** - Recording overlay appears at bottom of screen
3. **Speak clearly** - Audio waveform shows real-time levels
4. **Release Cmd+Option** - Speech is transcribed and inserted into your current app
5. **View results** - Check the transcript history in the main window

## Configuration

### API Keys Setup

In the Settings page, you can optionally provide an OpenAI key (better transcriptions) and a Cerebras key (improved formatting of transcriptions). Even if you don't include these, the service will still work.

1. **OpenAI Whisper: (Optional)**
   - Get an API key from [OpenAI](https://platform.openai.com/api-keys)
   - Enter in Settings → Speech → OpenAI API Key

2. **LLM Processing (Optional):**
   - **Cerebras** - Get key from [Cerebras](https://cloud.cerebras.ai/)
   - Enter in Settings → LLM → Cerebras API Key

### Custom Instructions

If desired, customize how your speech is processed by the LLM before being pasted:

1. Go to **Settings → Custom Instructions**
2. Add prompts like:
   - "Use all lowercase words"
   - "Never include punctuation at the end of sentences"
