# 🎬 YouTube Automation System

> **Automate the repetitive parts of running a YouTube channel — from script writing to publishing — powered by AI.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🧠 **Script Generator** | AI-powered video script generator (hook, intro, body sections, CTA, outro) |
| 🔍 **SEO Optimizer** | Generates 10 ranked titles, keyword-rich description, 30+ tags, hashtags |
| 🖼️ **Thumbnail Generator** | Auto-creates 1280×720 PNG thumbnails using Pillow |
| 📅 **Content Calendar** | 30-day content planner saved as JSON + CSV |
| 📤 **Upload Scheduler** | YouTube Data API v3 uploader with OAuth2 and scheduled publishing |
| 📊 **Analytics Dashboard** | Channel analytics report with top videos and engagement metrics |

---

## 🛠️ Prerequisites

- **Python 3.8+**
- **OpenAI API key** — for script generation, SEO, and content calendar
- **Google Cloud project** with YouTube Data API v3 enabled — for upload and analytics

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/panchalyuvraj125/youtube-automation.git
cd youtube-automation

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate.bat       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your actual API keys
```

---

## 🔑 How to Get API Keys

### OpenAI API Key

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Sign in or create an account
3. Go to **API keys** → **Create new secret key**
4. Copy the key and add it to your `.env` file as `OPENAI_API_KEY`

### YouTube Data API (Google Cloud Console)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Library**
4. Search for and enable **YouTube Data API v3** and **YouTube Analytics API**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → OAuth 2.0 Client ID** (type: Desktop app)
7. Download the JSON file and rename it to `client_secret.json` in the project root
8. For the API key: **Create Credentials → API key** and add it as `YOUTUBE_API_KEY`
9. Add your `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` from the downloaded JSON

---

## 💻 Usage

### Generate a Video Script

```bash
python main.py script --topic "10 Best AI Tools in 2024" --niche "tech"
```

```
ℹ Generating script for topic='10 Best AI Tools in 2024', niche='tech'...
✓ Script generated and saved to: output/scripts/script_10_Best_AI_Tools_20240115_143022.json
```

### Optimize SEO Metadata

```bash
python main.py seo --topic "10 Best AI Tools in 2024" --niche "tech" --audience "developers"
```

```
ℹ Optimizing SEO for topic='10 Best AI Tools in 2024', niche='tech'...
✓ SEO metadata saved to: output/seo/seo_10_Best_AI_Tools_20240115_143100.json
ℹ Best title: 10 AI Tools That Will 10x Your Productivity in 2024
```

### Create a Thumbnail

```bash
python main.py thumbnail --title "10 Best AI Tools" --subtitle "You Need These NOW" --bg-color "#1A1A2E" --text-color "#E94560"
```

```
ℹ Creating thumbnail for title='10 Best AI Tools'...
✓ Thumbnail saved to: output/thumbnails/thumbnail_10_Best_AI_Tools_20240115_143200.png
```

### Generate Content Calendar

```bash
python main.py calendar --niche "personal finance" --days 30 --videos-per-week 3
```

```
ℹ Generating 30-day calendar for niche='personal finance', 3 videos/week...
✓ Calendar with 13 entries saved to: output/calendars/calendar_personal_finance_20240115_143300.json
```

### Upload a Video

```bash
python main.py upload --video /path/to/video.mp4 --title "My Video Title" \
  --description "Video description here" --tags "ai,tools,productivity" \
  --privacy private --publish-at "2024-02-01T14:00:00Z"
```

### Fetch Analytics

```bash
python main.py analytics --days 30
```

```
ℹ Fetching analytics for the past 30 days...
✓ Analytics report saved to: output/analytics_report_20240115_143400.md
ℹ Views: 12,345 | Watch time: 45,678.9 min
```

### Run Full Pipeline (Script + SEO + Thumbnail)

```bash
python main.py all --topic "10 Best AI Tools" --niche "tech"
```

---

## 📁 Project Structure

```
youtube-automation/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── .env.example                  # API key template
├── .gitignore
├── config.py                     # Central configuration (loads .env)
├── main.py                       # CLI entry point
├── modules/
│   ├── __init__.py
│   ├── script_generator.py       # AI-powered script generator
│   ├── seo_optimizer.py          # SEO metadata generator
│   ├── thumbnail_generator.py    # Pillow thumbnail creator
│   ├── content_calendar.py       # 30-day content planner
│   ├── upload_scheduler.py       # YouTube Data API v3 uploader
│   └── analytics_dashboard.py   # YouTube Analytics reporter
├── output/
│   ├── scripts/                  # Generated scripts (JSON)
│   ├── thumbnails/               # Generated thumbnails (PNG)
│   ├── seo/                      # SEO metadata (JSON)
│   └── calendars/                # Content calendars (JSON + CSV)
└── tests/
    ├── __init__.py
    ├── test_script_generator.py
    ├── test_seo_optimizer.py
    ├── test_thumbnail_generator.py
    ├── test_content_calendar.py
    └── test_upload_scheduler.py
```

---

## 📦 Module Reference

| Module | Function | Description |
|--------|----------|-------------|
| `script_generator` | `generate_script(topic, niche, tone, duration_minutes)` | Generates a complete video script using GPT |
| `seo_optimizer` | `optimize_seo(topic, niche, target_audience)` | Generates titles, description, tags, hashtags |
| `thumbnail_generator` | `create_thumbnail(title, subtitle, bg_color, text_color, output_path)` | Creates a 1280×720 PNG thumbnail |
| `content_calendar` | `generate_calendar(niche, days, videos_per_week)` | Generates a content calendar as JSON + CSV |
| `upload_scheduler` | `upload_video(video_path, title, description, tags, ...)` | Uploads video to YouTube with metadata |
| `analytics_dashboard` | `get_channel_analytics(days)`, `generate_report(data)` | Fetches analytics and generates Markdown report |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All modules are tested with mocked external APIs (OpenAI and YouTube) so no real credentials are needed to run tests.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please follow PEP 8 style guidelines and include docstrings for all public functions.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is intended to assist content creators with repetitive tasks. Please ensure your use complies with [YouTube's Terms of Service](https://www.youtube.com/t/terms) and [Community Guidelines](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/). Automated uploading and scheduling should be done responsibly and in accordance with YouTube's API usage policies.

---

## ⭐ Star This Repo

If this project helps you save time on your YouTube workflow, please consider giving it a star! ⭐ It helps others discover the project and motivates continued development.

[![Star on GitHub](https://img.shields.io/github/stars/panchalyuvraj125/youtube-automation?style=social)](https://github.com/panchalyuvraj125/youtube-automation)