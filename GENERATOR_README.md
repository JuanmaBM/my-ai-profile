# My AI Profile Generator

An automated tool that analyzes your digital presence across multiple platforms to generate a comprehensive AI profile. This profile captures your personality traits, writing style, coding preferences, and personal interests by examining your LinkedIn posts, GitHub repositories, and RSS feeds.

## 🚀 How It Works

The AI Profile Generator analyzes three main data sources:

1. **LinkedIn Analysis**: Extracts text from your recent posts to analyze personality traits and derive personal interests from hashtags and keywords
2. **GitHub Analysis**: Examines your public repositories to understand your coding style, preferred languages, and development patterns
3. **RSS Feed Analysis**: Analyzes content from your blog, newsletter, or any RSS feed to understand your writing style across different platforms
4. **Content Synthesis**: Combines all analyses using an LLM to generate a coherent, comprehensive AI profile

## 📋 Features

- **Multi-platform Analysis**: LinkedIn, GitHub, and RSS feeds
- **Personality Insights**: Derived from social media activity
- **Coding Style Analysis**: Based on repository structure and code patterns
- **Writing Style Analysis**: Platform-specific analysis (Medium, personal blog, newsletters, etc.)
- **Interest Extraction**: Automatic identification of topics and interests
- **GitHub Actions Integration**: Fully automated CI/CD pipeline
- **Docker Support**: Containerized for consistent execution
- **Flexible Configuration**: Support for multiple RSS sources and optional components

## 🛠️ Setup Instructions

### Prerequisites

- GitHub account
- LinkedIn account (public profile recommended)
- LLM API access (OpenAI, Anthropic, or compatible API)
- Optional: RSS feed URL (blog, newsletter, etc.)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/my-ai-profile.git
cd my-ai-profile
```

### 2. Configure GitHub Secrets

Go to your repository settings → Secrets and variables → Actions, and add the following secrets:

#### Required Secrets:
- `LLM_API_KEY`: Your LLM API key (OpenAI, Anthropic, etc.)
- `LLM_BASE_URL`: Base URL for your LLM API (e.g., `https://api.openai.com/v1`)
- `LLM_MODEL`: Model name (e.g., `gpt-4`, `claude-3-sonnet-20240229`)

#### LinkedIn Authentication (choose one method):

**Option A: Session Cookies (Recommended)**
- `LINKEDIN_LI_AT`: LinkedIn session cookie (`li_at` value)
- `LINKEDIN_JSESSIONID`: LinkedIn session ID (`JSESSIONID` value)

**Option B: Username/Password (LinkedIn can block this method)**
- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password

#### How to Get LinkedIn Session Cookies:

1. Install dependencies locally:
   ```bash
   pip install -e .
   ```

2. Run the session token script:
   ```bash
   python scripts/get_linkedin_session_token.py your-email@example.com your-password
   ```

3. Copy the output values to GitHub secrets

### 3. Run the GitHub Action

1. Go to your repository → Actions tab
2. Select "Generate AI Profile" workflow
3. Click "Run workflow"
4. Fill in the required inputs:
   - **GitHub Username**: Your GitHub username
   - **LinkedIn Username**: Your LinkedIn public ID/username
   - **Display Name**: Name for the final profile
   - **RSS URL** (optional): Your blog/newsletter RSS feed
   - **RSS Name** (optional): Platform name (e.g., "Medium", "Blog")
   - **Important Notes** (optional): Critical restrictions or clarifications

5. The workflow will automatically:
   - Analyze your GitHub repositories
   - Extract content from LinkedIn posts
   - Process RSS feed content (if provided)
   - Generate and commit `MyAIProfile.md` to your repository

## 💻 Local Development

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/my-ai-profile.git
cd my-ai-profile

# Install dependencies
pip install -e .

# Or using Docker
docker build -t my-ai-profile .
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# LLM Configuration
LLM_API_KEY=your-llm-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# LinkedIn Authentication (choose one method)
# Option A: Session cookies
LINKEDIN_LI_AT=your-li-at-cookie
LINKEDIN_JSESSIONID=your-jsessionid-cookie

# Option B: Username/Password
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# GitHub (optional - uses public API)
GITHUB_TOKEN=your-github-token
```

### CLI Usage

The tool provides several CLI commands:

```bash
# Analyze GitHub repositories
python cli.py github yourusername

# Analyze LinkedIn posts
python cli.py linkedin your-linkedin-username

# Analyze RSS feed
python cli.py rss "https://yourblog.com/rss" "Blog"

# Add important notes
python cli.py important_notes "Avoid political discussions"

# Generate final profile
python cli.py merge "Your Name"

# Run complete analysis
python scripts/run_all.py --github-user yourusername --linkedin-user your-linkedin-username --name "Your Name"
```

### Docker Usage

```bash
# Build the image
docker build -t my-ai-profile .

# Run analysis
docker run --env-file .env my-ai-profile github yourusername
docker run --env-file .env my-ai-profile linkedin your-linkedin-username
docker run --env-file .env my-ai-profile merge "Your Name"
```

## 📁 Project Structure

```
my-ai-profile/
├── sources/              # Data extraction modules
│   ├── github.py        # GitHub repository analysis
│   ├── linkedin.py      # LinkedIn post extraction
│   └── rss.py          # RSS feed processing
├── analyzers/           # Analysis modules
│   ├── code_style.py   # Code style analysis
│   └── text_style.py   # Text and personality analysis
├── generators/          # Output generation
│   └── markdown_gen.py # Markdown profile generator
├── scripts/             # Utility scripts
│   ├── run_all.py      # Complete analysis orchestration
│   └── get_linkedin_session_token.py # LinkedIn auth helper
├── .github/workflows/   # GitHub Actions CI/CD
│   └── generate-profile.yml
├── cli.py              # Command-line interface
├── llm_client.py       # LLM API client
├── Dockerfile          # Container configuration
└── README.md
```

## 🔧 Configuration Options

### RSS Feed Sources

You can analyze multiple RSS sources by running the RSS command multiple times:

```bash
python cli.py rss "https://medium.com/@username/feed" "Medium"
python cli.py rss "https://yourblog.com/rss" "Personal Blog"
python cli.py rss "https://newsletter.com/feed" "Newsletter"
```

Each source will be analyzed separately and included in the final profile under its respective platform section.

### LinkedIn Authentication

The tool supports two authentication methods:

1. **Session Cookies** (Recommended): More reliable and doesn't require password storage
2. **Username/Password**: Fallback option if cookies don't work

### LLM Configuration

Compatible with any OpenAI-compatible API:
- OpenAI GPT models
- Anthropic Claude models
- Local LLM servers (Ollama, vLLM, etc.)
- Other compatible APIs

## 📊 Output

The tool generates a `MyAIProfile.md` file containing:

- **Personality Analysis**: Traits derived from social media content
- **Writing Style**: Platform-specific analysis showing style variations
- **Code Style**: Development preferences and patterns
- **Interests**: Automatically extracted topics and keywords
- **Important Notes**: Critical context or restrictions (if provided)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Privacy Note

This tool analyzes publicly available information from your digital presence. Ensure you're comfortable with the data being processed and review the generated profile before sharing it.