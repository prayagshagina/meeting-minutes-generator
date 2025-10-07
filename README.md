# meeting-minutes-generator# 🗒️ Meeting Minutes Generator

**An AI-powered system that automatically converts meeting audio into summarized and structured meeting minutes — highlighting key discussion points, decisions, action items, and deadlines.**

---

## 📘 Project Overview

The **Meeting Minutes Generator** is designed to simplify the process of recording and summarizing meetings by leveraging **Speech Recognition** and **Natural Language Processing (NLP)**.  
It captures spoken audio, transcribes it into text, cleans and processes the transcript, identifies key items, and finally generates a concise meeting summary report in **PDF** and **Word** formats.

---

## 🎯 Objectives

- Automate transcription of meeting audio into accurate text.  
- Clean the transcript and extract relevant information (decisions, action items, deadlines).  
- Summarize long meetings into short, structured reports.  
- Export the minutes in multiple formats (PDF, Word, Text).  
- Provide a simple and user-friendly web interface.

---

## 🧩 Key Features

| Feature | Description |
|----------|-------------|
| 🎙️ **Speech-to-Text** | Converts meeting audio into text using OpenAI Whisper / SpeechRecognition. |
| 🧹 **Text Cleaning** | Removes fillers, redundant phrases, and corrects punctuation using spaCy & NLTK. |
| 🧠 **Summarization** | Generates concise summaries using transformer models (T5 / BART). |
| ✅ **Information Extraction** | Identifies and classifies decisions, action items, and deadlines. |
| 📄 **Document Generation** | Exports summarized minutes in PDF and Word formats using ReportLab & python-docx. |
| 🌐 **Web Interface** | Provides an upload-based UI (Flask/Streamlit) for users to process audio easily. |

---

## 🧰 Tech Stack

| Category | Tools / Libraries |
|-----------|------------------|
| **Programming Language** | Python 3.9+ |
| **Speech Recognition** | OpenAI Whisper, SpeechRecognition |
| **Text Processing** | spaCy, NLTK, Regex |
| **Summarization** | Hugging Face Transformers (T5, BART, Pegasus) |
| **Document Generation** | python-docx, ReportLab |
| **Web Framework** | Flask or Streamlit |
| **Evaluation Metrics** | WER (jiwer), ROUGE |
| **Version Control** | Git & GitHub |

---

## 🗂️ Project Structure

