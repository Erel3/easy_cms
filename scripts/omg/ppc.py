with open("access.log", "r") as f:
  lines = f.readlines()
with open("access.log.1", "r") as f:
  lines += f.readlines()

lines = list(map(str.split, lines))

d = dict()

print(len(lines))

for line in lines:
  # print(line[0])
  assert(len(line[0].split('.')) == 4)
  # print(' '.join(line).find("/aws/notifications"))
  if ' '.join(line).find("notifications") != -1:
    d[line[0]] = True

print(len(d))
