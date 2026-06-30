response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": KANNADA_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    temperature=0.2  # 🔥 IMPORTANT: reduces randomness
)
