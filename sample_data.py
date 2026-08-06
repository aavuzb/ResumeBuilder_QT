"""
sample_data.py
Example resume content the app opens with, so the tool is ready to edit
immediately. Same content as the Tkinter and web editions, for consistency.
"""

SAMPLE = {
    "personal": {
        "name": "Abdurakhmon Abduraimjonov",
        "title": "AI / Machine Learning Engineer  •  Software Developer",
        "location": "Seoul, South Korea",
        "phone": "+82 10-0000-0000",
        "email": "aavuzb@gmail.com",
        "visa": "Visa: F-5 (Permanent Residency)",
    },
    "links": [
        {"label": "LinkedIn", "value": ""},
        {"label": "GitHub", "value": ""},
        {"label": "Portfolio", "value": ""},
    ],
    "summary": (
        "AI Engineer and Software Developer with 6+ years of experience in Artificial "
        "Intelligence, Machine Learning, Deep Learning, Computer Vision, and full-stack "
        "application development. Skilled across the modern LLM stack, model fine-tuning, "
        "and AI coding agents. Proficient in Python, C#, C++, Java, and JavaScript/Node.js, "
        "with experience in web development and REST API design."
    ),
    "skills": [
        {"label": "AI / ML / DL", "value": "Artificial Intelligence, Machine Learning, Deep Learning, Computer Vision"},
        {"label": "LLM & GenAI", "value": "Hugging Face, Unsloth, vLLM, Ollama, LM Studio, LLaMA, Gemma, Qwen, DeepSeek"},
        {"label": "AI Coding Agents", "value": "Cline, Aider, Cursor, Codex, Claude Code"},
        {"label": "Web Development", "value": "HTML, CSS, JavaScript, Node.js"},
        {"label": "Programming", "value": "Python, C#, C++, Java, JavaScript"},
    ],
    "experience": [
        {
            "title": "Software Developer",
            "company": "Linetron",
            "company_url": "https://www.linetron.co.kr",
            "employment_type": "Full-time",
            "start_date": "Mar 2025",
            "end_date": "Present",
            "projects": [
                {
                    "name": "Auto Test — LLM-powered test generation tool",
                    "url": "",
                    "bullets": [
                        "Designed Auto Test, generating test reports and code directly from written test specifications.",
                        "Served open-source models (LLaMA, Gemma) locally via vLLM for high-speed inference.",
                        "Fine-tuned models (Full, LoRA, QLoRA) with Hugging Face and Unsloth for domain-specific tasks.",
                    ],
                },
                {
                    "name": "Sensor Dashboard",
                    "url": "",
                    "bullets": [
                        "Built a real-time dashboard integrating PLC devices via TCP/IP socket communication.",
                    ],
                },
                {
                    "name": "Air Cleaner Android App",
                    "url": "",
                    "bullets": [
                        "Built an Android application to control and monitor an air purification device.",
                    ],
                },
            ],
        },
    ],
    "education": [
        {
            "degree": "Master's Degree in Computer Engineering",
            "school": "Kumoh National Institute of Technology, Gumi, Korea",
            "school_url": "https://www.kumoh.ac.kr",
            "meta": "2017 – 2019  |  GPA: 4.1 / 4.5",
        },
    ],
    "publications": [
        {
            "title": "Specific Object Detection Technology Through Convergence of Deep "
                      "Learning and a Novel Multi-Scale Template Matching Technique",
            "detail": "Patent — Registered 2022",
        },
    ],
    "certificates": [
        {"label": "Korean Language", "value": "TOPIK Level 4 — May 2026"},
        {"label": "English Language", "value": "IELTS Band 6 — November 2024"},
    ],
    "additional": [
        {"label": "Nationality", "value": "Uzbekistan"},
    ],
}
