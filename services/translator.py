from deep_translator import GoogleTranslator, MyMemoryTranslator

def translate_text(text: str, source_lang: str, target_lang: str) -> dict:
    """
    Translates text with automatic engine failover.
    Primary Engine: GoogleTranslator
    Failover Engine: MyMemoryTranslator
    """
    clean_text = text.strip()
    src = 'auto' if source_lang.strip().lower() in ['auto', 'auto-detect'] else source_lang.strip()
    target = target_lang.strip()

    # Short-circuit if source and target languages are identical
    if src.lower() == target.lower():
        return {
            "translated_text": clean_text,
            "engine_used": "Direct Pass-through"
        }

    try:
        translated = GoogleTranslator(source=src, target=target).translate(clean_text)
        if not translated:
            raise ValueError("Primary translator returned empty output.")

        return {
            "translated_text": translated,
            "engine_used": "Google Translate"
        }
    except Exception as primary_error:
        try:
            # MyMemory requires an explicit source code if 'auto' was requested
            fallback_src = 'en' if src == 'auto' else src
            translated = MyMemoryTranslator(source=fallback_src, target=target).translate(clean_text)

            return {
                "translated_text": translated,
                "engine_used": "MyMemory (Failover)"
            }
        except Exception as fallback_error:
            raise RuntimeError(
                f"All translation engines failed. Primary: {primary_error} | Fallback: {fallback_error}"
            ) from fallback_error            