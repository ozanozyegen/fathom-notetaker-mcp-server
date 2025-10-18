# Fathom Meeting Transcript MCP Server

A Model Context Protocol (MCP) server that provides access to Fathom meeting recordings and transcripts through the Fathom API. Built with Python and `uv` for easy setup and deployment.

## Purpose

This MCP server provides a secure interface for AI assistants like Claude to access and search your Fathom meeting recordings and retrieve detailed transcripts with speaker information.

## Features

### Available Tools

- **`list_meetings`** - List all available Fathom meeting recordings with pagination and advanced filtering
  - Filter by calendar invitees (email addresses)
  - Filter by who recorded the meeting
  - Filter by date range (created_after, created_before)
  - Include AI-generated summaries
  - Include full transcripts
  - Pagination support with cursor

- **`get_transcript`** - Retrieve full meeting transcripts with speaker names, emails, and timestamps
  - Get detailed transcripts for any recording
  - Includes speaker identification
  - Timestamped entries

- **`search_meetings`** - Search for meetings by title keyword
  - Quick keyword search across meeting titles
  - Configurable result limits

## Prerequisites

- Python 3.10 or higher
- `uv` package manager
- Fathom API Key (get from https://app.fathom.video/settings/integrations)

## Installation

### Step 1: Install uv

If you don't have `uv` installed:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installation.

### Step 2: Clone or Download the Project

```bash
git clone https://github.com/YOUR_USERNAME/fathom-mcp.git
cd fathom-mcp/fathom-uv
```

### Step 3: Set Up Virtual Environment and Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Step 4: Configure API Key

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Fathom API key:

```
FATHOM_API_KEY=your_actual_api_key_here
```

**Getting your API key:**
1. Go to https://app.fathom.video/settings/integrations
2. Generate or copy your API key
3. Paste it into the `.env` file

**Note:** The `.env` file is gitignored for security. Never commit your actual API key to version control.

## Configuration for Claude Desktop

### Step 1: Locate Your Claude Desktop Config

Find your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add the Fathom Server

Edit the config file and add the Fathom server to the `mcpServers` section:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "fathom": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/fathom-uv",
        "run",
        "fathom.py"
      ]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "fathom": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\ABSOLUTE\\PATH\\TO\\fathom-uv",
        "run",
        "fathom.py"
      ]
    }
  }
}
```

**Important:**
- Replace `/ABSOLUTE/PATH/TO/fathom-uv` with the actual absolute path to your project directory
- You can get the absolute path by running `pwd` (macOS/Linux) or `cd` (Windows) in the project directory
- On Windows, use double backslashes (`\\`) or forward slashes (`/`) in the path

### Step 3: Optional - Override API Key in Config

If you want to override the `.env` file API key, you can add it directly to the config:

```json
{
  "mcpServers": {
    "fathom": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/fathom-uv",
        "run",
        "fathom.py"
      ],
      "env": {
        "FATHOM_API_KEY": "your_override_api_key_here"
      }
    }
  }
}
```

**Environment Variable Priority:**
1. Environment variable in Claude Desktop config (highest priority)
2. `.env` file in project directory
3. System environment variable `FATHOM_API_KEY`

### Step 4: Restart Claude Desktop

1. **Fully quit** Claude Desktop (not just close the window)
   - **macOS**: Use Cmd+Q or select "Quit Claude" from the menu
   - **Windows**: Right-click the system tray icon and select "Quit" or "Exit"
2. Start Claude Desktop again
3. Look for the tools icon to verify the server is connected

## Usage Examples

Once configured, you can ask Claude:

### List Meetings

- "Show me my recent Fathom meetings"
- "List the last 10 meetings"
- "Show me meetings with summaries included"

### Filter by Invitees

- "Show me meetings where john@example.com was invited"
- "List meetings with jane@example.com and bob@example.com as invitees"

### Filter by Recorder

- "Show me meetings recorded by alice@example.com"

### Filter by Date

- "Show me meetings created after October 1st, 2024"
- "List meetings from last week"

### Get Transcripts

- "Get the transcript for Fathom recording 12345678"
- "Show me the transcript for recording ID 95116213"

### Search Meetings

- "Search my Fathom meetings for 'project planning'"
- "Find meetings about 'sprint review'"

### Pagination

- "Show me the next page of meetings using cursor: [cursor_string]"

## Example Outputs

### list_meetings (basic)

```
✅ Found 5 meetings:

📝 Title: Team Standup
   🆔 Recording ID: 95116213
   📅 Date: 2024-10-17T22:01:35Z
   👤 Recorded by: John Smith (Engineering)
   🔗 Share: https://fathom.video/share/abc123
   👥 Invitees: john@example.com, jane@example.com

---

...
```

### get_transcript

```
✅ Transcript for recording 95116213:

[00:00:01] John Smith (john@example.com): Good morning everyone
[00:00:03] Jane Doe (jane@example.com): Morning! How's everyone doing?
[00:00:05] John Smith (john@example.com): Great! Let's get started with the standup
...
```

### search_meetings

```
✅ Found 2 meetings matching 'planning':

📝 Title: Sprint Planning Meeting
   🆔 Recording ID: 95100807
   📅 Date: 2024-10-15T20:03:55Z
   👤 Recorded by: John Smith
   🔗 Share: https://fathom.video/share/xyz789

---

...
```

## Testing Locally

You can test the server locally before connecting it to Claude:

```bash
# Make sure your .env file is configured
# Run the server
uv run fathom.py
```

The server will start and listen for MCP protocol messages on stdin/stdout. You should see:

```
Starting Fathom MCP server...
FATHOM_API_KEY configured
```

Press Ctrl+C to stop the server.

## Troubleshooting

### Server Not Showing Up in Claude

1. **Check the config file syntax** - Make sure your JSON is valid
2. **Verify the absolute path** - Use `pwd` or `cd` to get the correct path
3. **Check uv installation** - Run `which uv` (macOS/Linux) or `where uv` (Windows)
4. **Restart Claude Desktop completely** - Make sure to fully quit, not just close the window

### API Key Issues

**Error: "FATHOM_API_KEY not configured"**
- Check that your `.env` file exists in the project directory
- Verify the API key is correctly formatted in the `.env` file
- Make sure there are no extra spaces or quotes around the key

**Error: "401 Unauthorized"**
- Your API key may be invalid or expired
- Generate a new key at https://app.fathom.video/settings/integrations
- Update your `.env` file with the new key

### Tool Call Failures

1. **Check Claude's logs** for detailed error messages:
   ```bash
   # macOS/Linux
   tail -n 20 -f ~/Library/Logs/Claude/mcp*.log

   # Windows
   type %APPDATA%\Claude\Logs\mcp*.log
   ```

2. **Verify API connectivity** - Test that you can reach the Fathom API
3. **Check recording IDs** - Make sure the recording ID exists and you have access to it

### No Transcripts Available

- Transcripts may take time to process after a meeting ends
- Some meetings may not have transcripts enabled
- Verify the recording exists in the Fathom web interface first

### Rate Limiting

If you see "429 Rate Limited" errors:
- Wait a few minutes before retrying
- Reduce the frequency of requests
- Consider using pagination instead of fetching all meetings at once

## Development

### Project Structure

```
fathom-mcp/
├── fathom-uv/
│   ├── fathom.py                          # Main MCP server implementation
│   ├── pyproject.toml                     # Project dependencies and metadata
│   ├── .env.example                       # Template for environment variables
│   ├── .env                               # Your actual API key (gitignored)
│   ├── .gitignore                         # Git ignore rules
│   ├── claude_desktop_config.example.json # Example Claude Desktop config
│   └── uv.lock                           # Dependency lock file
├── README.md                              # This file
├── QUICKSTART.md                          # Quick start guide
└── LICENSE                                # MIT License
```

### Adding New Features

1. Edit `fathom.py` to add new tools
2. Use the `@mcp.tool()` decorator for new functions
3. Follow the existing pattern for error handling and logging
4. Test locally with `uv run fathom.py`
5. Restart Claude Desktop to pick up changes

### Logging

The server logs to stderr (not stdout) to avoid interfering with the MCP protocol:
- Info level: General operations
- Warning level: Configuration issues
- Error level: API errors and exceptions

## Security Considerations

- **API Key Storage**: Never commit your `.env` file to version control
- **Gitignore**: The `.env` file is automatically ignored
- **Environment Variables**: API key can be overridden via environment variables
- **Logging**: API keys are never logged or exposed in responses
- **HTTPS**: All API requests use HTTPS encryption

## Performance Notes

- Transcript requests may take longer for meetings with many speakers
- Search is performed client-side (fetches meetings then filters)
- Pagination is recommended for large meeting lists
- Default limits: 20 meetings for list, 10 for search

## API Details

- **Base URL**: `https://api.fathom.ai/external/v1`
- **Authentication**: API Key via `X-Api-Key` header
- **Endpoints Used**:
  - `GET /meetings` - List meetings with metadata
  - `GET /recordings/{id}/transcript` - Get transcript
- **API Reference**: https://developers.fathom.ai/api-reference/meetings/list-meetings

## License

MIT License

## Support

For issues or questions:
- Fathom API Documentation: https://docs.fathom.video/
- MCP Documentation: https://modelcontextprotocol.io/
- Check Claude Desktop logs for debugging information

