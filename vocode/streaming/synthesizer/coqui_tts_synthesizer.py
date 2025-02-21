import logging
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from pydub import AudioSegment
import numpy as np
import io
from vocode.streaming.agent.bot_sentiment_analyser import BotSentiment
from vocode.streaming.models.audio_encoding import AudioEncoding
from vocode.streaming.models.message import BaseMessage

from .base_synthesizer import BaseSynthesizer, SynthesisResult

from vocode.streaming.models.synthesizer import CoquiTTSSynthesizerConfig
from TTS.api import TTS



class CoquiTTSSynthesizer(BaseSynthesizer):
    def __init__(
        self, config: CoquiTTSSynthesizerConfig, logger: Optional[logging.Logger] = None
    ):
        super().__init__(config)
        self.tts = TTS(**config.tts_kwargs)
        self.speaker = config.speaker
        self.language = config.language

    def create_speech(
        self,
        message: BaseMessage,
        chunk_size: int,
        bot_sentiment: Optional[BotSentiment] = None,
    ) -> SynthesisResult:
        
        tts = self.tts
        audio_data = np.array(tts.tts(message.text, self.speaker, self.language))

        # Convert the NumPy array to bytes
        audio_data_bytes = (audio_data * 32767).astype(np.int16).tobytes()

        # Create an in-memory file-like object (BytesIO) to store the audio data
        buffer = io.BytesIO(audio_data_bytes)

        audio_segment: AudioSegment = AudioSegment.from_raw(buffer, frame_rate=22050, channels=1, sample_width=2)

        output_bytes_io = io.BytesIO()
        audio_segment.export(output_bytes_io, format="wav")
        return self.create_synthesis_result_from_wav(
            file=output_bytes_io, message=message, chunk_size=chunk_size
        )
