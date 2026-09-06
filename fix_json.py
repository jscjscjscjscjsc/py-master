import json

with open('C:/Users/Administrator/python_tutor/data/comics.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Chinese curved quotes that break JSON
content = content.replace('“', '「')  # " -> 「
content = content.replace('”', '」')  # " -> 」

with open('C:/Users/Administrator/python_tutor/data/comics.json', 'w', encoding='utf-8') as f:
    f.write(content)

with open('C:/Users/Administrator/python_tutor/data/comics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('OK -', len(data), 'comics loaded')
for k in sorted(data.keys(), key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1]))):
    c = data[k]
    print(f'  {k}: {c["title"]} ({len(c["panels"])} panels)')
