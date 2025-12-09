import json
import csv

# اقرأ بيانات المهام من ملف JSON
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# حدد أسماء الأعمدة (حقول CSV)
fieldnames = ['employee', 'description', 'status', 'date', 'attachment', 'notes', 'rating']

# افتح ملف CSV للكتابة
with open('tasks.csv', 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for task in data:
        writer.writerow(task)

print("تم تحويل البيانات إلى tasks.csv بنجاح ✅")