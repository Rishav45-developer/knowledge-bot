
import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

cache_key = "demo:python"
answer = "Redis cache is working!"

cached_answer = client.get(cache_key)

if cached_answer is not None:
    print("CACHE HIT")
    print("Answer:", cached_answer)
else:
    print("CACHE MISS")
    client.set(cache_key, answer, ex=60)
    print("Answer:", answer)

client.close()
