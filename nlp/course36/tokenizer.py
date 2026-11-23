
import jieba

def chinese_tokenizer(text):
    return jieba.lcut(text)
