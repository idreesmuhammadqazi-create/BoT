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
├── main.py            # unified CLI entry point (upload + download subcommands)
├── upload.py          # original upload script (superseded by main.py)
├── download.py        # original download script (superseded by main.py)
├── build.bat          # Windows build script → compiles main.py to dist\twitch-storage.exe
├── build.sh           # Linux/macOS build script (if needed)
├── requirements.txt
├── .env               # tokens and config (never commit this)
├── banana.png         # test input
└── plan.md            # this file
```

---

## One-Time Setup Checklist

- [ ] Create a second Twitch account for the bot (e.g. `banana_storage_bot`)
- [ ] Register a Twitch Developer App at dev.twitch.tv/console (logged in as main account)
- [ ] Generate a bot OAuth token with scopes `user:bot`, `user:read:chat`, `user:write:chat` via twitchtokengenerator.com (logged in as bot account)
- [ ] Save Bot Token, Bot Username, and channel name to `.env` as `BOT_TOKEN`, `BOT_USERNAME`, `CHANNEL`
- [ ] Download TwitchDownloaderCLI binary for your OS from GitHub releases
- [ ] Install ffmpeg (TwitchDownloader dependency)
- [ ] Run `build.bat` to compile the standalone `dist\twitch-storage.exe`
- [ ] Verify bot account is email-verified on Twitch

---

## Implementation Plan

### Phase 1 — Encoder (`upload.py` → `main.py upload`)

- [x] Load config from `.env`
- [x] Read file, base64-encode, split into chunks (400 chars; plan said 200 — we felt adventurous)
- [ ] Print estimated send time before starting
- [x] Connect bot to channel via raw TCP socket (plan said `twitchio`; the socket disagreed)
- [x] Send `DATA:HEADER` message with total chunk count
- [x] Send each chunk as `DATA:XXXXX:...` with zero-padded index
- [x] 1.6 second delay between messages (configurable via `--delay`)
- [x] Print progress every 10 chunks
- [x] Send `DATA:EOF` on completion
- [ ] Prompt user to save the VOD ID

### Phase 2 — Decoder (`download.py` → `main.py download`)

- [x] Accept VOD ID as CLI argument
- [x] Call TwitchDownloaderCLI via subprocess to download chat JSON
- [ ] Cache the JSON locally so re-runs don't re-download
- [x] Parse JSON, filter messages by bot username and `DATA:` prefix
- [x] Handle HEADER, chunk, and EOF message types
- [x] Warn if chunk count doesn't match HEADER total
- [x] Sort chunks by index, join base64, decode to bytes
- [x] Write output file
- [x] Print recovered file path

### Phase 3 — Polish

- [x] `.env` file with all config (no hardcoded secrets)
- [x] `requirements.txt`
- [ ] Graceful handling if bot gets rate-limited mid-upload (retry logic)
- [x] CLI flag `--chunk-size` to tune message length
- [x] CLI flag `--delay` to tune message delay
- [x] README with full setup + usage instructions
- [x] Compiled to standalone `.exe` via PyInstaller (`build.bat`)
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

- [x] `banana.png` uploads via bot without errors
- [x] VOD chat log downloadable via TwitchDownloaderCLI
- [x] Decoded file is byte-for-byte identical to the original
- [x] `md5sum banana.png` == `md5sum banana_recovered.png`
- [x] Full round-trip works start to finish with no manual steps beyond starting the stream
- [x] Compiled to a standalone `twitch-storage.exe` — no Python required on target machine