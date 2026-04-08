import socket, base64, os, time, sys
from dotenv import load_dotenv

load_dotenv()

# Args: token, nick, channel, filepath
TOKEN   = sys.argv[1]
NICK    = sys.argv[2]
CHANNEL = "#" + sys.argv[3]
location = sys.argv[4]

def makechunks(path, chunksize=400):
    bytes = open(path, "rb").read()
    base64str = base64.b64encode(bytes).decode()
    chunks = []
    for i in range(0, len(base64str), chunksize):
        chunks.append(base64str[i : i + chunksize])
    return chunks

chunks = makechunks(location)

irc = socket.socket()
irc.connect(("irc.chat.twitch.tv", 6667))
irc.send(f"PASS {TOKEN}\r\n".encode())
irc.send(f"NICK {NICK}\r\n".encode())
irc.send(f"JOIN {CHANNEL}\r\n".encode())
time.sleep(2)

def send(msg):
    irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())
    time.sleep(1.6)

print(f"CHUNKS:{len(chunks)}", flush=True)
send(f"DATA:HEADER total={len(chunks)}")
for i, chunk in enumerate(chunks):
    send(f"DATA:{i:05d}:{chunk}")
    print(f"PROGRESS:{i+1}", flush=True)
send("DATA:EOF")
print("DONE", flush=True)
irc.close()
