import subprocess, json, base64, sys, os
from dotenv import load_dotenv
load_dotenv()
VOD_ID = input("VOD ID : ")
BOT_USERNAME =  os.getenv("BOT_USERNAME")
PREFIX = "DATA:"
CHATLOGS = f"chat_{VOD_ID}.json"
OUTPUTFILE = input("enter the filename of the recovered image(what YOU want it to be named )(add .png in the end plz) : ")
print("dowload chat logs ....")
subprocess.run([
    "./TwitchDownloaderCLI", "ChatDownload", "--id" , VOD_ID, "--output", CHATLOGS], check = True)

with open(CHATLOGS) as f:
    data = json.load(f)
chunks = {}
total = 1
for comment in data["comments"]:
    name = comment["commenter"]["name"].lower()
    msg = comment["message"]["body"]
    if name != BOT_USERNAME.lower():
        continue
    if not msg.startswith(PREFIX):
        continue
    payload = msg[len(PREFIX):]
    if payload.startswith("HEADER"):
        parts = dict(p.split("=") for p in payload[7:].split())
        total = int(parts["total"])
        print(f"found {total} chunks in the header")
        continue
    if payload == "EOF":
        continue
    idx, _, chunk = payload.partition(":")
    chunks[int(idx)] = chunk
print(f"found {len(chunks)} actual  chunks")
if total != len(chunks):
    print("toatal chunks vs actual chunks dont match some message probably got dropped or smtg")
b64 = "".join(chunks[i] for i in sorted(chunks))
raw = base64.b64decode(b64)
with open(OUTPUTFILE, "wb") as d:
    d.write(raw)
    print(f"done file is at {OUTPUTFILE}")