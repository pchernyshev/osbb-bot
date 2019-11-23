import re


def resolve(phone: str):
    pattern = re.compile('\d+')
    matches = pattern.findall(phone)
    result = ''.join(matches)
    print('+'+result)
    return '+' + result
