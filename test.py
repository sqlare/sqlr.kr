import redis.asyncio as redis
import asyncio

def pool():
    return redis.ConnectionPool(host='localhost', port=6379, db=0)

async def main():
    while True:
        key = "asdfasdfasdfasf"

        try:
            db = redis.Redis(connection_pool=pool())
            db_k = await db.json().get(key)
            await db.close()
            print(db_k)
        except:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(main())