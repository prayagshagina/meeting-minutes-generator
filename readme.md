AI Meeting Minutes Generator
(Voice → Text → Summary → Export)

A Flask-based AI/ML web application that automatically converts meeting audio recordings into well-structured meeting minutes containing summaries, key points, decisions, action items, and deadlines.

📋 Project Overview

The AI Meeting Minutes Generator automates the process of creating meeting minutes by leveraging advanced speech recognition and natural language processing (NLP) technologies.
It allows users to upload an audio file, automatically transcribes it using OpenAI Whisper, cleans the transcript using NLTK, and summarizes it with OpenAI GPT-3.5 / GPT-4 API into clear, structured notes.

Finally, the summarized minutes can be exported in .txt, .docx, or .pdf formats for professional reporting.

⚙️ Workflow

Audio Upload: User uploads a meeting recording through the Flask interface.

Speech-to-Text Conversion: Audio is transcribed using OpenAI Whisper.

Text Cleaning: The transcript is processed using NLTK to remove filler words, repetitions, and noise.

Summarization: The cleaned text is summarized using OpenAI GPT-3.5 / GPT-4 API into structured meeting notes.

Display Results: The final summary is displayed on an HTML results page.

Export: The summary and key points are exported into .txt, .docx, and .pdf using python-docx and reportlab libraries.

🧩 Features

🎙️ Upload audio in .wav, .mp3, or .m4a formats

🗣️ High-accuracy transcription with OpenAI Whisper

🧹 Text cleaning using NLTK and regex

🤖 AI-powered summarization using OpenAI GPT-3.5 / GPT-4

📑 Structured outputs — Summary, Key Points, Decisions, and Action Items

💾 Export meeting minutes to TXT, DOCX, or PDF

🌐 Simple, clean Flask-based web interface