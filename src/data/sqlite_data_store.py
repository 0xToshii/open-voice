import sqlite3
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.interfaces.data_store import IDataStore, TranscriptEntry


class SQLiteDataStore(IDataStore):
    """SQLite-based data store for persistent transcript storage"""

    def __init__(self):
        self.app_data_dir = self._get_app_data_directory()
        self.audio_dir = self.app_data_dir / "audio"
        self.db_path = self.app_data_dir / "transcripts.db"
        self._initialize_storage()

    def _get_app_data_directory(self) -> Path:
        """Get the application data directory (Mac-compatible)"""
        if os.name == "posix":  # macOS/Linux
            app_data_dir = Path.home() / "Library" / "Application Support" / "OpenVoice"
        else:  # Windows
            app_data_dir = Path.home() / "AppData" / "Roaming" / "OpenVoice"

        return app_data_dir

    def _initialize_storage(self):
        """Create database and audio directory if they don't exist"""
        try:
            # Create directories
            self.app_data_dir.mkdir(parents=True, exist_ok=True)
            self.audio_dir.mkdir(exist_ok=True)

            # Create database and tables
            self._create_tables()
            print(f"SQLite storage initialized at: {self.app_data_dir}")

        except Exception as e:
            print(f"Failed to initialize SQLite storage: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    processed_text TEXT,
                    timestamp DATETIME NOT NULL,
                    duration REAL NOT NULL,
                    inserted_successfully BOOLEAN NOT NULL DEFAULT 0,
                    audio_file_path TEXT,
                    provider_used TEXT NOT NULL DEFAULT 'unknown'
                )
            """
            )

            # Create index for faster timestamp queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_transcripts_timestamp 
                ON transcripts(timestamp)
            """
            )

            conn.commit()

    def save_transcript(
        self,
        original_text: str,
        processed_text: str,
        duration: float,
        audio_file_path: Optional[str] = None,
        provider_used: str = "unknown",
    ) -> int:
        """Save a transcript entry and return its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO transcripts 
                    (original_text, processed_text, timestamp, duration, inserted_successfully, audio_file_path, provider_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        original_text,
                        processed_text,
                        datetime.now(),
                        duration,
                        False,  # Will be updated later via mark_insertion_status
                        audio_file_path,
                        provider_used,
                    ),
                )

                transcript_id = cursor.lastrowid
                conn.commit()

                print(f"Saved transcript {transcript_id}: '{original_text[:50]}...'")
                return transcript_id

        except Exception as e:
            print(f"Failed to save transcript: {e}")
            raise

    def get_transcripts(self, limit: int = 100) -> List[TranscriptEntry]:
        """Get recent transcript entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name

                cursor = conn.execute(
                    """
                    SELECT * FROM transcripts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """,
                    (limit,),
                )

                transcripts = []
                for row in cursor:
                    entry = TranscriptEntry(
                        id=row["id"],
                        original_text=row["original_text"],
                        processed_text=row["processed_text"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        duration=row["duration"],
                        inserted_successfully=bool(row["inserted_successfully"]),
                        audio_file_path=row["audio_file_path"],
                        provider_used=row["provider_used"],
                    )
                    transcripts.append(entry)

                return transcripts

        except Exception as e:
            print(f"Failed to get transcripts: {e}")
            return []

    def mark_insertion_status(self, transcript_id: int, success: bool) -> None:
        """Mark whether text insertion was successful"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE transcripts 
                    SET inserted_successfully = ?
                    WHERE id = ?
                """,
                    (success, transcript_id),
                )

                conn.commit()

        except Exception as e:
            print(f"Failed to update insertion status: {e}")

    def delete_transcript(self, transcript_id: int) -> bool:
        """Delete a transcript entry and its audio file. Returns True if successful"""
        try:
            # First, get the audio file path
            audio_path = self.get_transcript_audio_path(transcript_id)

            # Delete from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM transcripts WHERE id = ?
                """,
                    (transcript_id,),
                )

                if cursor.rowcount == 0:
                    print(f"Transcript {transcript_id} not found")
                    return False

                conn.commit()

            # Delete audio file if it exists
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    print(f"Deleted audio file: {audio_path}")
                except Exception as e:
                    print(f"Failed to delete audio file {audio_path}: {e}")

            print(f"Deleted transcript {transcript_id}")
            return True

        except Exception as e:
            print(f"Failed to delete transcript {transcript_id}: {e}")
            return False

    def get_transcript_audio_path(self, transcript_id: int) -> Optional[str]:
        """Get the audio file path for a transcript"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT audio_file_path FROM transcripts WHERE id = ?
                """,
                    (transcript_id,),
                )

                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            print(f"Failed to get audio path for transcript {transcript_id}: {e}")
            return None

    def save_audio_file(self, audio_data: bytes, transcript_id: int) -> Optional[str]:
        """Save audio data to file and return the file path"""
        try:
            audio_filename = f"transcript_{transcript_id}.wav"
            audio_path = self.audio_dir / audio_filename

            with open(audio_path, "wb") as f:
                f.write(audio_data)

            print(f"Saved audio file: {audio_path}")
            return str(audio_path)

        except Exception as e:
            print(f"Failed to save audio file: {e}")
            return None

    def update_audio_path(self, transcript_id: int, audio_file_path: str) -> bool:
        """Update the audio file path for a transcript"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    UPDATE transcripts 
                    SET audio_file_path = ?
                    WHERE id = ?
                """,
                    (audio_file_path, transcript_id),
                )

                if cursor.rowcount == 0:
                    print(f"Transcript {transcript_id} not found for audio path update")
                    return False

                conn.commit()
                print(f"Updated audio path for transcript {transcript_id}")
                return True

        except Exception as e:
            print(f"Failed to update audio path for transcript {transcript_id}: {e}")
            return False

    def get_storage_stats(self) -> dict:
        """Get storage statistics for debugging/monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM transcripts")
                total_transcripts = cursor.fetchone()[0]

                cursor = conn.execute(
                    "SELECT COUNT(*) FROM transcripts WHERE inserted_successfully = 1"
                )
                successful_insertions = cursor.fetchone()[0]

                # Calculate total audio files
                audio_files = (
                    len(list(self.audio_dir.glob("*.wav")))
                    if self.audio_dir.exists()
                    else 0
                )

                # Calculate storage size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                audio_size = (
                    sum(f.stat().st_size for f in self.audio_dir.glob("*.wav"))
                    if self.audio_dir.exists()
                    else 0
                )

                return {
                    "total_transcripts": total_transcripts,
                    "successful_insertions": successful_insertions,
                    "audio_files": audio_files,
                    "database_size_bytes": db_size,
                    "audio_size_bytes": audio_size,
                    "total_size_bytes": db_size + audio_size,
                    "storage_path": str(self.app_data_dir),
                }

        except Exception as e:
            print(f"Failed to get storage stats: {e}")
            return {}
