#!/usr/bin/env python3
"""
Fathom Meeting Transcript MCP Server - Access Fathom meeting recordings and transcripts
"""

import os
import sys
import logging
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("fathom-server")

# Initialize MCP server
mcp = FastMCP("fathom")

# Configuration
API_KEY = os.environ.get("FATHOM_API_KEY", "")
BASE_URL = "https://api.fathom.ai/external/v1"

# === UTILITY FUNCTIONS ===


async def make_fathom_request(endpoint, params=None):
    """Make authenticated request to Fathom API"""
    if not API_KEY.strip():
        raise ValueError("FATHOM_API_KEY not configured")

    url = f"{BASE_URL}{endpoint}"
    headers = {"X-Api-Key": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()


# === MCP TOOLS ===


@mcp.tool()
async def list_meetings(
    limit: str = "20",
    cursor: str = "",
    calendar_invitees: str = "",
    include_summary: str = "false",
    include_transcript: str = "false",
    created_after: str = "",
    created_before: str = "",
    recorded_by: str = "",
) -> str:
    """List all available Fathom meeting recordings with pagination and filtering support.

    Args:
        limit: Number of meetings to return (1-100)
        cursor: Pagination cursor from previous response
        calendar_invitees: Comma-separated email addresses to filter by invitees (e.g. "user1@example.com,user2@example.com")
        include_summary: Include AI-generated meeting summary (default: false)
        include_transcript: Include full meeting transcript (default: false)
        created_after: Filter meetings created after this ISO 8601 timestamp (e.g. "2024-01-01T00:00:00Z")
        created_before: Filter meetings created before this ISO 8601 timestamp (e.g. "2024-12-31T23:59:59Z")
        recorded_by: Comma-separated email addresses to filter by who recorded the meeting (e.g. "user1@example.com,user2@example.com")
    """
    logger.info(
        f"Listing meetings with limit={limit}, cursor={cursor}, calendar_invitees={calendar_invitees}"
    )

    try:
        # Convert limit to int
        limit_int = int(limit) if limit.strip() else 20
        if limit_int < 1 or limit_int > 100:
            return "❌ Error: Limit must be between 1 and 100"

        # Build query parameters
        params = {"limit": limit_int}

        if cursor.strip():
            params["cursor"] = cursor

        # Handle calendar_invitees (can be comma-separated)
        if calendar_invitees.strip():
            invitee_list = [
                email.strip() for email in calendar_invitees.split(",") if email.strip()
            ]
            for invitee in invitee_list:
                if "calendar_invitees[]" not in params:
                    params["calendar_invitees[]"] = []
                if isinstance(params["calendar_invitees[]"], list):
                    params["calendar_invitees[]"].append(invitee)

        # Handle boolean flags
        if include_summary.lower() == "true":
            params["include_summary"] = "true"

        if include_transcript.lower() == "true":
            params["include_transcript"] = "true"

        # Handle date filters
        if created_after.strip():
            params["created_after"] = created_after

        if created_before.strip():
            params["created_before"] = created_before

        # Handle recorded_by filter (can be comma-separated)
        if recorded_by.strip():
            recorded_by_list = [
                email.strip() for email in recorded_by.split(",") if email.strip()
            ]
            for email in recorded_by_list:
                if "recorded_by[]" not in params:
                    params["recorded_by[]"] = []
                if isinstance(params["recorded_by[]"], list):
                    params["recorded_by[]"].append(email)

        # Make API request
        data = await make_fathom_request("/meetings", params)

        # Format results
        items = data.get("items", [])
        if not items:
            return "📭 No meetings found"

        meetings_list = []
        for meeting in items:
            recording_id = meeting.get("recording_id", "N/A")
            title = meeting.get("title", "Untitled")
            date = meeting.get("recording_start_time", "Unknown date")
            recorded_by_info = meeting.get("recorded_by", {})
            name = recorded_by_info.get("name", "Unknown")
            team = recorded_by_info.get("team", "Unknown team")
            share_url = meeting.get("share_url", "No URL")

            # Build meeting info
            meeting_info = (
                f"📝 Title: {title}\n"
                f"   🆔 Recording ID: {recording_id}\n"
                f"   📅 Date: {date}\n"
                f"   👤 Recorded by: {name} ({team})\n"
                f"   🔗 Share: {share_url}"
            )

            # Add calendar invitees if available
            invitees = meeting.get("calendar_invitees", [])
            if invitees:
                invitee_emails = [inv.get("email", "N/A") for inv in invitees]
                meeting_info += f"\n   👥 Invitees: {', '.join(invitee_emails)}"

            # Add summary if included
            summary = meeting.get("summary")
            if summary:
                meeting_info += f"\n   📋 Summary: {summary}"

            # Add transcript if included
            transcript = meeting.get("transcript", [])
            if transcript:
                meeting_info += f"\n   📄 Transcript: {len(transcript)} entries"

            meetings_list.append(meeting_info)

        result = f"✅ Found {len(items)} meetings:\n\n" + "\n\n---\n\n".join(
            meetings_list
        )

        # Add pagination info
        next_cursor = data.get("next_cursor", "")
        if next_cursor:
            result += f"\n\n---\n\n⏭️  Next page cursor: {next_cursor}"

        return result

    except ValueError as e:
        logger.error(f"Invalid limit value: {e}")
        return f"❌ Error: Invalid limit value - must be a number"
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e}")
        return f"❌ API Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        logger.error(f"Error listing meetings: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_transcript(recording_id: str = "") -> str:
    """Get the full transcript of a specific recording with speaker names, emails, and timestamps."""
    logger.info(f"Getting transcript for recording_id={recording_id}")

    try:
        if not recording_id.strip():
            return "❌ Error: recording_id is required"

        # Convert to int to validate
        rec_id = int(recording_id)

        # Make API request
        endpoint = f"/recordings/{rec_id}/transcript"
        data = await make_fathom_request(endpoint)

        # Check for transcript
        transcript = data.get("transcript", [])
        if not transcript:
            return "📭 No transcript available for this recording"

        # Format transcript
        transcript_lines = []
        for entry in transcript:
            speaker_info = entry.get("speaker", {})
            speaker_name = speaker_info.get("display_name", "Unknown")
            speaker_email = speaker_info.get("matched_calendar_invitee_email", "")
            text = entry.get("text", "")
            timestamp = entry.get("timestamp", "00:00:00")

            email_part = f" ({speaker_email})" if speaker_email else ""
            transcript_lines.append(f"[{timestamp}] {speaker_name}{email_part}: {text}")

        result = f"✅ Transcript for recording {recording_id}:\n\n" + "\n".join(
            transcript_lines
        )
        return result

    except ValueError:
        logger.error(f"Invalid recording_id: {recording_id}")
        return f"❌ Error: recording_id must be a number"
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e}")
        if e.response.status_code == 404:
            return f"❌ Error: Recording {recording_id} not found"
        return f"❌ API Error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error getting transcript: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def search_meetings(query: str = "", limit: str = "10") -> str:
    """Search meetings by title keyword."""
    logger.info(f"Searching meetings with query='{query}', limit={limit}")

    try:
        if not query.strip():
            return "❌ Error: search query is required"

        # Convert limit to int
        limit_int = int(limit) if limit.strip() else 10
        if limit_int < 1 or limit_int > 50:
            return "❌ Error: Limit must be between 1 and 50"

        # Fetch more meetings than limit to filter
        fetch_limit = min(limit_int * 3, 100)
        endpoint = f"/meetings?limit={fetch_limit}"

        # Make API request
        data = await make_fathom_request(endpoint)

        # Filter by query
        items = data.get("items", [])
        query_lower = query.lower()
        filtered = [m for m in items if query_lower in m.get("title", "").lower()]

        # Limit results
        filtered = filtered[:limit_int]

        if not filtered:
            return f"🔍 No meetings found matching '{query}'"

        # Format results
        meetings_list = []
        for meeting in filtered:
            recording_id = meeting.get("recording_id", "N/A")
            title = meeting.get("title", "Untitled")
            date = meeting.get("recording_start_time", "Unknown date")
            recorded_by = meeting.get("recorded_by", {})
            name = recorded_by.get("name", "Unknown")
            share_url = meeting.get("share_url", "No URL")

            meetings_list.append(
                f"📝 Title: {title}\n"
                f"   🆔 Recording ID: {recording_id}\n"
                f"   📅 Date: {date}\n"
                f"   👤 Recorded by: {name}\n"
                f"   🔗 Share: {share_url}"
            )

        result = (
            f"✅ Found {len(filtered)} meetings matching '{query}':\n\n"
            + "\n\n---\n\n".join(meetings_list)
        )
        return result

    except ValueError:
        logger.error(f"Invalid limit value: {limit}")
        return f"❌ Error: Invalid limit value - must be a number"
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e}")
        return f"❌ API Error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error searching meetings: {e}")
        return f"❌ Error: {str(e)}"


# === SERVER STARTUP ===
def main():
    logger.info("Starting Fathom MCP server...")

    if not API_KEY.strip():
        logger.warning(
            "FATHOM_API_KEY not set - server will return errors until configured"
        )
    else:
        logger.info("FATHOM_API_KEY configured")

    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
