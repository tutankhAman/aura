import logging
import functools
import asyncio
from typing import Any, Callable, TypeVar, Coroutine

T = TypeVar('T')

def setup_logger(name: str) -> logging.Logger:
    """Setup logger with consistent format"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def async_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Retry decorator for async functions
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
                        
            raise last_exception
            
        return wrapper
    return decorator

def format_audio_chunk(chunk: bytes, sample_rate: int = 16000) -> bytes:
    """
    Format audio chunk for Deepgram API
    
    Args:
        chunk: Raw audio bytes
        sample_rate: Sample rate of audio
        
    Returns:
        bytes: Formatted audio chunk
    """
    # Add WAV header if needed
    if not chunk.startswith(b'RIFF'):
        # Simple WAV header for 16-bit PCM
        header = (
            b'RIFF' +   # ChunkID
            b'\x00\x00\x00\x00'  +# ChunkSize (to be filled)
            b'WAVE' + # Format
            b'fmt ' + # Subchunk1ID
            b'\x10\x00\x00\x00'  +# Subchunk1Size
            b'\x01\x00'  +# AudioFormat (PCM)
            b'\x01\x00' + # NumChannels (Mono)
            + sample_rate.to_bytes(4, 'little')  +# SampleRate
            + (sample_rate * 2).to_bytes(4, 'little')  +# ByteRate
            b'\x02\x00'  +# BlockAlign
            b'\x10\x00'  +# BitsPerSample
            b'data'  +# Subchunk2ID
            b'\x00\x00\x00\x00'  # Subchunk2Size (to be filled)
        )
        
        # Update chunk sizes
        data_size = len(chunk)
        chunk_size = data_size + 36
        header = header[:4] + chunk_size.to_bytes(4, 'little') + header[8:]
        header = header[:-4] + data_size.to_bytes(4, 'little')
        
        return header + chunk
    
    return chunk 