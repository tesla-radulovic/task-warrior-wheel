from flask import Flask, request, jsonify
import random
from tasklib import TaskWarrior

app = Flask(__name__)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    n = int(request.args.get('n', 5))  # Default to 5
    k = int(request.args.get('k', 3))  # Default to 3

    tw = TaskWarrior()

    # Get all pending tasks
    pending_tasks = list(tw.tasks.pending())

    # Sort by urgency descending (higher urgency first)
    sorted_tasks = sorted(pending_tasks, key=lambda t: -float(t['urgency']))

    if len(sorted_tasks) <= n:
        top_n = sorted_tasks
        random_k = []
    else:
        top_n = sorted_tasks[:n]
        remaining = sorted_tasks[n:]

        # Select k uniformly at random without replacement
        random_k = random.sample(remaining, min(k, len(remaining)))

    # Function to convert task to dict
    def task_to_dict(task):
        return {
            'id': task['id'],
            'description': task['description'],
            'urgency': float(task['urgency']),
            # Add more fields if needed, e.g., 'due': task['due'], 'priority': task['priority']
        }

    response = {
        'top': [task_to_dict(t) for t in top_n],
        'random': [task_to_dict(t) for t in random_k]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
