from taskw import TaskWarrior
w = TaskWarrior()
tasks = w.load_tasks()
print ( tasks.keys() )
print (tasks['pending'][0]) 