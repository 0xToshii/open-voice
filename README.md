# Open Voice

A speech-to-text application for macOS that allows you to dictate into any application using global hotkeys and AI-enhanced text processing.

## More Info

Open Voice is a Mac desktop application that transforms speech into text and intelligently inserts it into any application you're using. Simply press **Cmd+Option**, speak naturally, and watch your words appear in your current text field with AI-powered enhancements.

It's heavily influenced by Aqua Voice - but the idea here is that you can have the same experience while enjoying BYOK (bring your own key) and pay-as-you-go pricing across multiple providers.

### Multi-Provider Architecture

Open Voice supports multiple AI providers, each offering both **speech-to-text** and **LLM processing** capabilities. These are all plug-and-play, and just require you to get a key:

**Providers:**
1. **OpenAI:** Get a [key](https://platform.openai.com/).
2. **Groq:** Get a [key](https://console.groq.com/).

There is also a **Local Whisper** option which runs locally, without LLM processing, requiring no setup.

## Quick Start

### Requirements

- **Python 3.9+**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/0xToshii/open-voice.git
   cd open-voice
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On macOS/Linux
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Grant permissions when prompted:**
   - Microphone access
   - Accessibility permissions

### Basic Usage

1. **Start the app** - The GUI will open on the settings page
2. **Add a key to desired provider** - Optionally select your provider of choice from the dropdown and paste key
2. **Press and hold Cmd+Option** - Recording overlay appears at bottom of screen
3. **Speak clearly** - Audio waveform shows real-time levels
4. **Release Cmd+Option** - Speech is transcribed and inserted into your current app
5. **View results** - Check the transcript history in the main window

### Custom Instructions

If desired, customize how your speech is processed by the LLM before being pasted:

1. Go to **Settings → Custom Instructions**
2. Add prompts like:
   - "Use all lowercase words"
   - "Never include punctuation at the end of sentences"
