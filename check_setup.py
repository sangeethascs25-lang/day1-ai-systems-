from config import client, MODEL, PROVIDER

print("Provider:", PROVIDER)
print("Model:", MODEL)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Say Hello in one word"}
    ]
)

print("AI:", response.choices[0].message.content)