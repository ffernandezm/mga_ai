

from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Write a one-sentence bedtime story about a unicorn."
    }]
)

print(completion.choices[0].message.content)



# curl https://api.openai.com/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer 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" \
#   -d '{
#     "model": "gpt-4o-mini",
#     "store": true,
#     "messages": [
#       {"role": "user", "content": "write a haiku about ai"}
#     ]
#   }'
