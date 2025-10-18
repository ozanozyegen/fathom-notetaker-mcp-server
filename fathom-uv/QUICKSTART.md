# Fathom MCP Server - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install uv (if not already installed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installation.

### 2. Set Up Your API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# Get your key from: https://app.fathom.video/settings/integrations
```

Your `.env` file should look like:
```
FATHOM_API_KEY=sk_live_abc123xyz...
```

### 3. Install Dependencies

```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -e .
```

### 4. Test the Server

```bash
# Run the server to verify it works
uv run fathom.py
```

You should see:
```
Starting Fathom MCP server...
FATHOM_API_KEY configured
```

Press Ctrl+C to stop.

### 5. Configure Claude Desktop

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace with your actual path):

```json
{
  "mcpServers": {
    "fathom": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/YOUR_USERNAME/path/to/fathom-uv",
        "run",
        "fathom.py"
      ]
    }
  }
}
```

**Get your absolute path:**
```bash
# Run this in the fathom-uv directory
pwd
```

### 6. Restart Claude Desktop

1. **Fully quit** Claude Desktop (Cmd+Q on Mac, or right-click tray icon on Windows)
2. Start Claude Desktop again
3. Look for the tools icon 🔧 to verify the server is connected

## ✅ Test It Out

Try these commands in Claude:

1. **"Show me my recent Fathom meetings"**
2. **"Get the transcript for recording 12345678"** (use an actual recording ID)
3. **"Search my meetings for 'standup'"**

## 🔧 Troubleshooting

### Server not showing up?

1. Check the config file path is correct (use absolute path)
2. Verify `uv` is installed: `which uv` (Mac/Linux) or `where uv` (Windows)
3. Check Claude logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

### API key errors?

1. Verify your `.env` file exists in the project directory
2. Check the API key is valid at https://app.fathom.video/settings/integrations
3. Make sure there are no extra spaces in the `.env` file

## 📚 Full Documentation

See [README.md](README.md) for complete documentation, including:
- Detailed usage examples
- All available tools and parameters
- Advanced filtering options
- Security considerations
- Development guide

## 🎯 Quick Reference

### Available Tools

1. **list_meetings** - List meetings with filters
   - Parameters: limit, cursor, calendar_invitees, include_summary, include_transcript, created_after, created_before, recorded_by

2. **get_transcript** - Get full transcript
   - Parameters: recording_id

3. **search_meetings** - Search by title
   - Parameters: query, limit

### Example Queries

- "List my last 5 meetings"
- "Show meetings where john@example.com was invited"
- "Get transcript for recording 95116213"
- "Search for 'planning' meetings"
- "Show meetings from last week with summaries"

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review Claude Desktop logs for error messages
- Verify your Fathom API key is valid
- Make sure the `.env` file is in the correct location

---

**Ready to go?** Start asking Claude about your Fathom meetings! 🎉

