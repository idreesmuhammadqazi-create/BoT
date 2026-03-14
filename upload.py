import asyncio, base64, os
from dotenv import load_dotenv
from twitchio.ext import commands
load_dotenv()
def makechunks(path, chunksize=400):
    bytes = open(path, "rb").read()
    base64str = base64.b64encode(bytes).decode()
    chunks = []
    for i in range(0,len(base64str), chunksize):
        chunks.append(base64str[i : i +chunksize])
    return chunks
location = str(input("where is the file and whats its name? : ")) 
chunks = makechunks(location)
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("BOT_TOKEN"),
            client_id=os.getenv("CLIENT_ID"),
            prefix="!",
            initial_channels=[os.getenv("CHANNEL")],
            bot_id=os.getenv("BOT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
        )
    async def event_ready(self):
        ch = self.get_channel(os.getenv("CHANNEL"))
        await ch.send(f"DATA:HEADER total={len(chunks)}")
        for i, chunk in enumerate(chunks):
            await ch.send(f"DATA:{i:05d}:{chunk}")
            await asyncio.sleep(1.6)
        await ch.send("DATA:EOF")
        print("spamming successful")
Bot().run()