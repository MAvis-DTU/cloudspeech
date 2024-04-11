from openai import OpenAI

# get the API key from the file
with open("openaiKey.txt", "r") as f:
    api_key = f.read()
    f.close()


client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
  model="gpt-3.5-turbo-1106",
  response_format={ "type": "json_object" },
  messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ]
)
print(response.choices[0].message.content)