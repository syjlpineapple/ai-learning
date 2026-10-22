
text = "我 喜欢 NLP"
tokens = text.split()

vocab = {
    "我":0,
    "喜欢":1,
    "NLP":2
}

token_ids = [vocab[token] for token in tokens]

print(tokens)
print(token_ids)