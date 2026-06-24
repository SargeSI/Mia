---
name: voice-transcription-for-forwarding
description: "Обработка голосовых сообщений, которые Сергей надиктовал для пересылки другому человеку. Чистая дословная расшифровка в формате для копирования и пересылки."
version: 2.0.0
category: mia
---

# Voice Transcription for Forwarding

Когда Сергей говорит «запиши для <Имя>», «расшифруй, я перешлю», «надиктовал для <Имя>» — это значит, что голосовое предназначено для пересылки другому человеку.

## Правила

1. **Расшифровка СТРОГО дословная** — слово в слово, как сказано. Никакой литературной обработки, улучшений или сокращений
2. **Формат ответа** — ОДНО отдельное сообщение через send_message. Два варианта:

**Вариант A — Сергей надиктовал для кого-то:**
```
Это расшифровка голосового, которое Сергей надиктовал для тебя:

«<дословный текст расшифровки>»

— расшифровано Мией
```

**Вариант B — Сергей переслал чужое голосовое мне для расшифровки:**
```
Это расшифровка голосового сообщения от <Имя> (получатель — Сергей):

«<дословный текст расшифровки>»

— расшифровано Мией
```

3. **НИКАКОЙ обвязки:** не добавлять «Готово», «Вот сообщение», «Можешь пересылать» и т.п.
4. **НИКАКИХ обращений:** не добавлять «Привет», «Здравствуй» и имя получателя. Обращение добавит сам Сергей
5. **НИКАКИХ комментариев по содержанию:** не анализировать, не предлагать ответ. Просто расшифровка
6. **Игнорировать предыдущие голосовые** — расшифровывать только то, которое только что прислано, а не более ранние из контекста

## Механика

- Голосовое расшифровывается через Groq Whisper
- Расшифровка отправляется через send_message отдельным сообщением
- Основной ответ в чате — минимальный: «Отправила отдельным сообщением» или просто «Готово»
- Если расшифровка не получилась — честно сказать «Groq Whisper не справился, вот что получилось: ...», но НЕ придумывать текст

## ⚠️ Critical Pitfall: Serving stale transcriptions

**Do NOT reuse a transcription from an earlier voice message.** When a new voice arrives, ALWAYS run Groq Whisper on the NEW audio file — never reach back into the conversation history and re-serve a previous transcription. This happened at least 3 times in one session: the user sent a new voice message (about skill format corrections) but the agent kept outputting the transcription of the PREVIOUS voice message (about беспилотные советы and детская коляска). The agent was responding to the NEW message's content correctly (addressing the format issues), yet the transcription block it output was the OLD one — a complete mismatch visible to the user.

**Root cause:** The agent cached or re-used a transcription from context instead of processing the actual incoming audio.

**Prevention:** Always call Groq Whisper on the incoming audio file. Never assume the transcription in the current context is the right one — it may be stale from a previous message.\n\n**Verification protocol (added after 3 repeated failures in one session):**\n1. After transcription, compare the FIRST SENTENCE of the output against the voice message that just arrived\n2. If the transcription starts with content from a PREVIOUS voice message (e.g., about «беспилотные советы» when the new message is about «скилл отработал неидеально») — DISCARD and re-transcribe\n3. The agent may correctly respond to the new message's MEANING while outputting the OLD text as the transcription block — this is a context-caching hallucination. The response correctness does NOT validate the transcription correctness\n4. When in doubt, ask Сергей: «это расшифровка того голосового, что ты только что прислал?» — before formatting for forwarding

## ⚠️ Pitfall: STT misrecognition of technical abbreviations

Groq Whisper may misrecognize technical abbreviations spoken in voice messages:
- «CRPA» → «Сюрприз» (confirmed error)
- Always keep the RAW transcription as-is. If a technical term sounds suspicious, flag it to Сергей but do NOT "fix" it silently
- If the user corrects a term, update the transcription and remember the correction
