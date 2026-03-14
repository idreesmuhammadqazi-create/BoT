# 🍌 Project #09 — Twitch Chat Storage
> Go live. Spam your file into chat. The banana lives forever in Twitch's servers.

---

## What We're Building

A two-script system that encodes any file as base64, sends it chunk-by-chunk into a live Twitch chat via a bot, and recovers it later by downloading the VOD chat log and reconstructing the original file.

Your "storage address" is a Twitch VOD ID. Your "hard drive" is Twitch's servers.

---

## File Structure

```
twitch-storage/
├── upload.py          # bot that sends file → chat
├── download.py        # pulls chat log → reconstructs file
├── requirements.txt
├── .env               # tokens and config (never commit this)
├── banana.png         # test input
└── PLANNING.md        # this file
```

---

## One-Time Setup Checklist

- [ ] Create a second Twitch account for the bot (e.g. `banana_storage_bot`)
- [ ] Register a Twitch Developer App at dev.twitch.tv/console (logged in as main account)
- [ ] Generate a bot OAuth token with scopes `user:bot`, `user:read:chat`, `user:write:chat` via twitchtokengenerator.com (logged in as bot account)
- [ ] Save Client ID, Client Secret, Bot Token, Bot User ID, and channel name to `.env`
- [ ] Download TwitchDownloaderCLI binary for your OS from GitHub releases
- [ ] Install ffmpeg (TwitchDownloader dependency)
- [ ] `pip install twitchio python-dotenv`
- [ ] Verify bot account is email-verified on Twitch

---

## Implementation Plan

### Phase 1 — Encoder (`upload.py`)

- [ ] Load config from `.env`
- [ ] Read file, base64-encode, split into 200-char chunks
- [ ] Print estimated send time before starting
- [ ] Connect bot to channel via twitchio
- [ ] On `event_ready`: send `DATA:HEADER` message with total chunk count and filename
- [ ] Send each chunk as `DATA:XXXXX:...` with zero-padded index
- [ ] 1.6 second delay between messages (rate limit safety)
- [ ] Print progress every 10 chunks
- [ ] Send `DATA:EOF` on completion
- [ ] Prompt user to save the VOD ID

### Phase 2 — Decoder (`download.py`)

- [ ] Accept VOD ID as CLI argument or prompt
- [ ] Call TwitchDownloaderCLI via subprocess to download chat JSON
- [ ] Cache the JSON locally so re-runs don't re-download
- [ ] Parse JSON, filter messages by bot username and `DATA:` prefix
- [ ] Handle HEADER, chunk, and EOF message types
- [ ] Warn if chunk count doesn't match HEADER total
- [ ] Sort chunks by index, join base64, decode to bytes
- [ ] Write output file
- [ ] Print recovered file size and path

### Phase 3 — Polish

- [ ] `.env` file with all config (no hardcoded secrets)
- [ ] `requirements.txt`
- [ ] Graceful handling if bot gets rate-limited mid-upload (retry logic)
- [ ] CLI flag `--chunk-size` to tune message length
- [ ] README with full setup + usage instructions
- [ ] Hackatime tracking active in editor

---

## Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `CHUNK_SIZE` | 200 chars | Safe Twitch message length |
| `MSG_DELAY` | 1.6 sec | ~37 msg/min, within rate limits |
| `PREFIX` | `DATA:` | Tags bot messages for easy filtering |
| Base64 overhead | ~1.33× | A 100KB file → ~136KB encoded |
| 100KB file stream time | ~18 min | 680 chunks × 1.6s |

---

## Risk & Mitigations

| Risk | Mitigation |
|------|------------|
| Twitch silently drops messages | Warn on chunk count mismatch at decode time |
| VOD deleted after 60 days | Highlight the VOD immediately after streaming |
| Bot account not verified | Verify email before starting |
| Rate limit mid-upload | Add retry with backoff in Phase 3 |
| Wrong token scopes | Use twitchtokengenerator.com, double-check scopes |

---

## Success Criteria

- [ ] `banana.png` uploads via bot without errors
- [ ] VOD chat log downloadable via TwitchDownloaderCLI
- [ ] Decoded file is byte-for-byte identical to the original
- [ ] `md5sum banana.png` == `md5sum banana_recovered.png`
- [ ] Full round-trip works start to finish with no manual steps beyond starting the stream