#!/usr/bin/env python3
"""
twitch-storage CLI
  upload   - encode a file as base64 chunks and send it via Twitch IRC chat
  download - pull a VOD's chat log and reassemble the original file
"""

import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def make_chunks(path: str, chunksize: int = 400) -> list[str]:
    data = open(path, "rb").read()
    b64 = base64.b64encode(data).decode()
    return [b64[i : i + chunksize] for i in range(0, len(b64), chunksize)]


def cmd_upload(args: argparse.Namespace) -> None:
    token   = os.getenv("BOT_TOKEN")
    nick    = os.getenv("BOT_USERNAME")
    channel = "#" + os.getenv("CHANNEL", "")

    if not token or not nick or not os.getenv("CHANNEL"):
        sys.exit("Error: BOT_TOKEN, BOT_USERNAME, and CHANNEL must be set in .env")

    if not os.path.isfile(args.file):
        sys.exit(f"Error: file not found: {args.file}")

    chunks = make_chunks(args.file, args.chunk_size)

    irc = socket.socket()
    irc.connect(("irc.chat.twitch.tv", 6667))
    irc.send(f"PASS {token}\r\n".encode())
    irc.send(f"NICK {nick}\r\n".encode())
    irc.send(f"JOIN {channel}\r\n".encode())
    time.sleep(2)

    def send(msg: str) -> None:
        irc.send(f"PRIVMSG {channel} :{msg}\r\n".encode())
        time.sleep(args.delay)

    print(f"Sending {len(chunks)} chunks...")
    send(f"DATA:HEADER total={len(chunks)}")
    for i, chunk in enumerate(chunks):
        send(f"DATA:{i:05d}:{chunk}")
        if i % 10 == 0:
            print(f"  {i}/{len(chunks)}")
    send("DATA:EOF")
    print("Upload complete.")
    irc.close()


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def cmd_download(args: argparse.Namespace) -> None:
    bot_username = os.getenv("BOT_USERNAME")
    if not bot_username:
        sys.exit("Error: BOT_USERNAME must be set in .env")

    prefix    = "DATA:"
    chatlogs  = f"chat_{args.vod_id}.json"

    print("Downloading chat logs...")
    subprocess.run(
        ["./TwitchDownloaderCLI", "ChatDownload", "--id", args.vod_id, "--output", chatlogs],
        check=True,
    )

    with open(chatlogs) as f:
        data = json.load(f)

    chunks: dict[int, str] = {}
    total = 1

    for comment in data["comments"]:
        name = comment["commenter"]["name"].lower()
        msg  = comment["message"]["body"]

        if name != bot_username.lower():
            continue
        if not msg.startswith(prefix):
            continue

        payload = msg[len(prefix):]

        if payload.startswith("HEADER"):
            parts = dict(p.split("=") for p in payload[7:].split())
            total = int(parts["total"])
            print(f"Found {total} chunks in header.")
            continue

        if payload == "EOF":
            continue

        idx, _, chunk = payload.partition(":")
        chunks[int(idx)] = chunk

    print(f"Recovered {len(chunks)} chunks.")

    if total != len(chunks):
        print(
            f"Warning: expected {total} chunks but got {len(chunks)}. "
            "Some messages may have been dropped."
        )

    b64 = "".join(chunks[i] for i in sorted(chunks))
    raw = base64.b64decode(b64)

    with open(args.output, "wb") as out:
        out.write(raw)

    print(f"Done. File saved to: {args.output}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="twitch-storage",
        description="Store and retrieve files via Twitch VOD chat.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- upload --------------------------------------------------------------
    up = sub.add_parser("upload", help="Upload a file through Twitch chat.")
    up.add_argument("file", help="Path to the file you want to upload.")
    up.add_argument(
        "--chunk-size",
        type=int,
        default=400,
        metavar="N",
        help="Base64 characters per chat message (default: 400).",
    )
    up.add_argument(
        "--delay",
        type=float,
        default=1.6,
        metavar="SECONDS",
        help="Delay between messages in seconds (default: 1.6).",
    )

    # -- download ------------------------------------------------------------
    dl = sub.add_parser("download", help="Download a file from a Twitch VOD chat.")
    dl.add_argument("vod_id", help="Twitch VOD ID to download chat from.")
    dl.add_argument("output", help="Filename to save the recovered file as.")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.command == "upload":
        cmd_upload(args)
    elif args.command == "download":
        cmd_download(args)


if __name__ == "__main__":
    main()
