import base64
from io import BytesIO
from gtts import gTTS
from gtts.lang import tts_langs

_SUPPORTED_LANGS_CACHE = None

def _get_supported_langs() -> dict:
    global _SUPPORTED_LANGS_CACHE
    if _SUPPORTED_LANGS_CACHE is None:
        try:
            _SUPPORTED_LANGS_CACHE = tts_langs()
        except Exception:
            # Return empty dict on transient failure without caching it permanently
            return {}
    return _SUPPORTED_LANGS_CACHE

def generate_tts_audio(text: str, lang: str, accent: str = "us") -> str:
    """
    Generates base64-encoded MP3 audio from text using gTTS.
    Applies regional accent (tld) routing specifically for English.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Text string cannot be empty for speech synthesis.")

    stripped_lang = lang.strip()
    clean_lang = 'en' if stripped_lang.lower() in ['auto', 'auto-detect'] else stripped_lang
    clean_accent = accent.lower().strip()
    supported = _get_supported_langs()

    if supported and clean_lang not in supported:
        raise ValueError(f"Voice playback is not available for '{clean_lang}' yet.")

    try:
        tts_kwargs = {"text": clean_text, "lang": clean_lang, "slow": False}
        if clean_lang.lower() == 'en':
            tts_kwargs["tld"] = clean_accent

        tts = gTTS(**tts_kwargs)

        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"TTS Audio Generation Failed: {str(e)}") from e