import socket, base64, os, time
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("BOT_TOKEN")
NICK    = os.getenv("BOT_USERNAME")
CHANNEL = "#" + os.getenv("CHANNEL")

def makechunks(path, chunksize=400):
    bytes = open(path, "rb").read()
    base64str = base64.b64encode(bytes).decode()
    chunks = []
    for i in range(0, len(base64str), chunksize):
        chunks.append(base64str[i : i + chunksize])
    return chunks

location = input("where is the file and whats its name? : ")
chunks = makechunks(location)

# connect to twitch IRC
irc = socket.socket()
irc.connect(("irc.chat.twitch.tv", 6667))
irc.send(f"PASS {TOKEN}\r\n".encode())
irc.send(f"NICK {NICK}\r\n".encode())
irc.send(f"JOIN {CHANNEL}\r\n".encode())
time.sleep(2)

def send(msg):
    irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())
    time.sleep(1.6)

print(f"sending {len(chunks)} chunks...")
send(f"DATA:HEADER total={len(chunks)}")
for i, chunk in enumerate(chunks):
    send(f"DATA:{i:05d}:{chunk}")
    if i % 10 == 0:
        print(f"  {i}/{len(chunks)}")
send("DATA:EOF")
print("spamming successful")
irc.close()