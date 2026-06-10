from app.tasks.test_task import add

result = add.delay(10, 20)

print(result.id)
print(result.get(timeout=10))