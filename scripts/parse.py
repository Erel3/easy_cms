import csv

with open("users2.csv", "r") as file:
  lines = list(csv.reader(file))

lines = lines[1:]
for line in lines:
  line = list(map(str.strip, line))
  name, grade, login, password, url = line
  first_name, last_name = name.split(' ', 1)

  contest_id = 3

  # print(f"cmsAddUser -t Asia/Almaty -p '{password}' --bcrypt '{first_name}' '{last_name}' '{login}' &&")
  # print(f"cmsRemoveUser '{login}' &&")
  print(f"cmsAddParticipation -c {contest_id} -t '{grade}' -p '{password}' --bcrypt '{login}' &&")


