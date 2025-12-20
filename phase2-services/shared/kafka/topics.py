# Kafka Topics Configuration
# All Kafka topics used in the Cloud Learning Platform

class Topics:
    """Kafka topic names."""
    
    # Document Service Topics
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    NOTES_GENERATED = "notes.generated"
    
    # Quiz Service Topics
    QUIZ_REQUESTED = "quiz.requested"
    QUIZ_GENERATED = "quiz.generated"
    
    # Audio Service Topics (TTS/STT)
    AUDIO_TRANSCRIPTION_REQUESTED = "audio.transcription.requested"
    AUDIO_TRANSCRIPTION_COMPLETED = "audio.transcription.completed"
    AUDIO_GENERATION_REQUESTED = "audio.generation.requested"
    AUDIO_GENERATION_COMPLETED = "audio.generation.completed"
    
    # Chat Service Topics
    CHAT_MESSAGE = "chat.message"
    
    @classmethod
    def all_topics(cls) -> list:
        """Get all topic names."""
        return [
            cls.DOCUMENT_UPLOADED,
            cls.DOCUMENT_PROCESSED,
            cls.NOTES_GENERATED,
            cls.QUIZ_REQUESTED,
            cls.QUIZ_GENERATED,
            cls.AUDIO_TRANSCRIPTION_REQUESTED,
            cls.AUDIO_TRANSCRIPTION_COMPLETED,
            cls.AUDIO_GENERATION_REQUESTED,
            cls.AUDIO_GENERATION_COMPLETED,
            cls.CHAT_MESSAGE,
        ]
