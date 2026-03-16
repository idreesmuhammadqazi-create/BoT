# BoT — Banana on Twitch

> **The cloud storage solution nobody asked for, built in a way nobody should have.**

![Storage Backend](https://img.shields.io/badge/Storage-Twitch%20Chat-9146FF?style=flat-square&logo=twitch)
![Uptime](https://img.shields.io/badge/Uptime-~60%20days-yellow?style=flat-square)
![Reliability](https://img.shields.io/badge/Reliability-lol-red?style=flat-square)
![Dependencies](https://img.shields.io/badge/Dependencies-python--dotenv%20%2B%20vibes-blue?style=flat-square)
![Plan vs Reality](https://img.shields.io/badge/Plan%20vs%20Reality-diverged%20immediately-orange?style=flat-square)

---

## What Is This?

**BoT** is a *revolutionary*, *enterprise-grade*, *definitely-production-ready* cloud storage system that uses **Twitch live chat** as its persistence layer.

Yes. You read that correctly.

You take a file — say, `banana.png` — encode it in Base64, slice it into chunks, and then **spam it into a Twitch channel's chat** one message at a time, like a bot that has completely lost the plot. Later, you download the VOD chat log, parse the JSON, reassemble the chunks, decode them, and get your file back.

The success criterion is: `md5sum banana.png == md5sum banana_recovered.png`.

The bar is literally *"does the banana come back?"* We are proud to report: sometimes it does.

---

## Why?

Excellent question. We don't have a good answer.

The original plan document (`plan.md`) contains the phrase *"innovative use of Twitch's infrastructure"* which is one way to describe it. Another way is *"a hate crime against distributed systems."*

But mostly: because it's cursed, it works (loosely), and nobody can stop us.

---

## How It Works

```
┌─────────────┐     base64 + chunk      ┌──────────────────────┐
│  banana.png │ ──────────────────────► │  Twitch Chat (lmao)  │
└─────────────┘   1 msg per 1.6 seconds └──────────────────────┘
                                                   │
                                   ~2 min (banana.png, 75 chunks)
                                   or ~18 min if you're ambitious
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │  TwitchDownloaderCLI  │
                                       │  (an actual binary we │
                                       │   shell out to)       │
                                       └───────────────────────┘
                                                   │
                                          parse JSON, reassemble
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │  banana_recovered   │
                                        │  .png  🍌           │
                                        └─────────────────────┘
```

### Upload (`upload.py`)

1. Read `banana.png`
2. Base64-encode it (adding a cheerful 33% overhead — you're welcome)
3. Split into **400-character chunks** *(the plan said 200, but we felt adventurous)*
4. Open a **raw TCP socket** to Twitch IRC *(the plan said to use the `twitchio` library; the code said "no")*
5. Send `DATA:HEADER total=N`, then `DATA:00001:<chunk>`, `DATA:00002:<chunk>`, ..., then `DATA:EOF`
6. Wait **1.6 seconds between each message** to avoid Twitch's rate limiter
7. Go make a coffee. Come back. Make another coffee.

### Download (`download.py`)

1. Shell out to `TwitchDownloaderCLI` to fetch the VOD chat log as JSON
2. Parse the JSON *(described in the source as `"dowload chat logs ...."` — sic)*
3. Find all `DATA:` messages, reassemble in order
4. Verify chunk count *(the error message reads `"toatal chunks vs actual chunks dont match"` — also sic)*
5. Base64-decode
6. Write file to disk
7. Pray

---

## Advanced Usage: Deploying on a Stranger's Stream

*Congratulations. You've mastered the basics. Now let's talk about the **power user** workflow.*

The `.env` file has a field called `TWITCH_CHANNEL`. Technically, this can be set to **any** Twitch channel. Including one that belongs to someone who has no idea you exist.

This is not a hypothetical. This has been tested. In production. On a real streamer.

**un1v249** was live with ~1,000 viewers when BoT joined their chat and began its work.

```
DATA:00001:SGVsbG8gV29ybGQ=
DATA:00002:aGVsbG8gd29ybGQ=
DATA:00003:YmFuYW5hLnBuZw==
```

Every 1.6 seconds. The mods were fast. Impressively fast. **The bot was banned on chunk 10 out of 75.** That's a 13% completion rate. The banana did not come back. The file was not recovered. The storage did not work.

But the *concept* was proven. Mostly.

| Metric | Value |
|---|---|
| Streamer | un1v249 |
| Live viewers | ~1,000 |
| Chunks sent before ban | 10 / 75 |
| Completion rate | 13% |
| Banana recovered | ❌ |
| Bot banned | ✅ |
| Regrets | none |

The lesson here is that active mods are the enemy of distributed storage. A sleepy 3 AM stream with 12 viewers is a far more reliable upload target. We are not recommending this. We are simply observing it.

> **⚠️ Disclaimer:** We are *legally obligated* to tell you this is a terrible idea and you should absolutely only use your own channel. Spamming someone else's chat is against Twitch's Terms of Service, rude, chaotic, and the kind of thing that gets you banned from the platform.
>
> We are *not* legally obligated to tell you that we find the mental image of this extremely funny. But we're telling you anyway. un1v249, if you're reading this: we're sorry. The banana was worth it.

---


## Installation

You'll need:

- Python 3.x
- `python-dotenv` (the **only** dependency — we're practically minimalist)
- `TwitchDownloaderCLI` somewhere on your `PATH`
- A Twitch account and OAuth token
- A Twitch channel to desecrate
- Patience. So much patience.

```bash
git clone https://github.com/you/BoT.git
cd BoT
pip install -r requirements.txt  # it's literally just python-dotenv
```

Create a `.env` file:

```env
TWITCH_OAUTH_TOKEN=oauth:your_token_here
TWITCH_CHANNEL=some_poor_channel
TWITCH_USERNAME=your_bot_username
TWITCH_VOD_ID=the_vod_id_you_just_created
```

---

## Usage

### Upload a file

```bash
python upload.py
```

Then wait. And wait. For a 100 KB file, you're looking at approximately **18 minutes**. This is not a bug. This is the rate limiter. This is your life now.

### Download a file

```bash
python download.py
```

This shells out to `TwitchDownloaderCLI`, downloads the VOD chat log, and attempts to reconstruct your file from the digital wreckage.

### Verify success

```bash
md5sum banana.png banana_recovered.png
```

If the hashes match: 🎉 The banana has returned.  
If they don't: 🤷 The banana is gone. It was always going to be gone.

---

## Limitations

*We prefer the term "features with aggressive trade-offs," but fine.*

| Limitation | Details | Severity |
|---|---|---|
| **Upload speed** | ~1 msg/1.6s → ~18 min for 100 KB. `banana.png` is only 75 chunks (~2 min) — the one thing this project has going for it | 😬 |
| **Storage expiry** | Twitch deletes VODs after ~60 days | ⏳ |
| **Base64 overhead** | 33% size inflation, always | 📈 |
| **No retry logic** | Plan called for it. Code said no. | 🎲 |
| **No caching** | Plan called for it. Code still said no. | 🎲 |
| **Typos in error messages** | `"toatal"`, `"dowload"` | ✍️ |
| **Raw socket to Twitch IRC** | Because `twitchio` was too easy | 🔌 |
| **Chunk size disagreement** | Plan: 200 chars. Code: 400 chars. | 🤷 |
| **Single file hardcoded** | It's always `banana.png` | 🍌 |
| **Reliability** | lol | 💀 |

### On the 60-Day Expiry

Your "cloud storage" has a **built-in self-destruct timer**. Twitch deletes VODs after approximately 60 days unless you're a Partner or Affiliate. This means BoT is less "cloud storage" and more "cloud storage with a countdown clock and no warning system."

Think of it as a very slow, very expensive, very public S3 bucket with a 60-day TTL and no way to extend it.

### On the 18-Minute Upload Time

The 1.6-second delay between messages is not optional — Twitch will ban your bot if you go faster. So uploading a modest 100 KB file takes roughly **18 minutes**. A 1 MB file would take about **3 hours**. We have not tested this. We will not be testing this.

To be fair, the included `banana.png` is only **75 chunks**, which means it uploads in approximately **2 minutes** (75 × 1.6s = 120s). This is, genuinely, the fastest thing about BoT. We are choosing to frame this as a feature.

### On the Plan vs. The Code

`plan.md` is a beautiful document. It describes caching, retry logic, the `twitchio` library, and 200-character chunks. The code implements none of these things and uses a raw socket instead. The plan and the code have clearly never met. We consider this a form of creative freedom.

---

## FAQ

**Q: Is this production-ready?**  
A: Absolutely. We define "production" as "it ran once and the banana came back."

**Q: What happens if Twitch goes down during an upload?**  
A: Your file is gone. There is no retry logic. The plan mentioned retry logic. The plan was optimistic.

**Q: Can I store files other than `banana.png`?**  
A: Technically yes, if you modify the hardcoded filename. We leave this as an exercise for the reader.

**Q: Why is it called BoT?**  
A: Presumably "Banana on Twitch." Possibly "Bane of Twitch." Maybe just "Bot." 

**Q: What's the maximum file size?**  
A: Theoretically unlimited. Practically, your Twitch channel's chat history, your sanity, and the 60-day VOD window are all finite resources.

**Q: Is the Base64 overhead a problem?**  
A: A 100 KB file becomes ~133 KB after encoding. You then wait 18 minutes to upload 133 KB to a chat room. The overhead is the least of your problems.

**Q: Why not just use S3?**  
A: Because S3 doesn't have `DATA:00001:` messages scrolling through a Twitch chat at 1 AM.

**Q: The error message says `"toatal chunks vs actual chunks dont match"` — is that intentional?**  
A: It is now.

---

## Contributing

Found a bug? Great. Open an issue.  
Want to add retry logic? The plan already asked for it — go ahead, be the hero.  
Want to add caching? Same.  
Want to fix the typos? Please don't. They're load-bearing.

If you do contribute, please ensure that `md5sum banana.png == md5sum banana_recovered.png` still passes. That is the entire test suite.

---

## License

Do whatever you want with this. We cannot in good conscience claim any moral authority over code that spams Base64 into a Twitch chat.

If you use this in production, please seek help.

---

*Built with one Python dependency, zero shame, and a banana.*  
*"The cloud is just someone else's chat log."* 🍌
