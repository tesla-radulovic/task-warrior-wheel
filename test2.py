from flask import Flask, request, jsonify
import random
from tasklib import TaskWarrior
import json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
DATA_FILE = 'task_data.json'

def serialize_task(task):
    d = dict(task)
    print (d)
    date_fields = ['entry', 'start', 'end', 'due', 'until', 'scheduled', 'wait', 'modified']
    for field in date_fields:
        if field in d and d[field] is not None:
            d[field] = d[field].isoformat()
    if 'urgency' in d:
        d['urgency'] = float(d['urgency'])
    # Tags are list, should be fine
    # Other fields like priority str, etc.
    return d

@app.route('/most_urgent', methods=['GET', 'POST'])
def get_most_urgent():
    data = request.get_json(silent=True) or {}
    if 'excluded' in data:
        excluded = set(data['excluded'])
    else:
        excluded_str = request.args.get('excluded', '')
        excluded = set(excluded_str.split(',')) if excluded_str else set()

    tw = TaskWarrior()
    pending_tasks = list(tw.tasks.pending())
    filtered_tasks = [t for t in pending_tasks if t['uuid'] not in excluded]

    if not filtered_tasks:
        return jsonify({'uuid': None})

    sorted_tasks = sorted(filtered_tasks, key=lambda t: -float(t['urgency']))
    return jsonify({'uuid': sorted_tasks[0]['uuid']})

@app.route('/random', methods=['GET', 'POST'])
def get_random():
    data = request.get_json(silent=True) or {}
    if 'excluded' in data:
        excluded = set(data['excluded'])
    else:
        excluded_str = request.args.get('excluded', '')
        excluded = set(excluded_str.split(',')) if excluded_str else set()

    tw = TaskWarrior()
    pending_tasks = list(tw.tasks.pending())
    filtered_tasks = [t for t in pending_tasks if t['uuid'] not in excluded]

    if not filtered_tasks:
        return jsonify({'uuid': None})

    random_task = random.choice(filtered_tasks)
    print(random_task)
    return jsonify({'uuid': random_task['uuid']})

@app.route('/dict', methods=['POST'])
def write_dict():
    data = request.get_json(force=True)  # Expects {uuid: [int1, int2], ...}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({'status': 'ok'})

@app.route('/dict', methods=['GET'])
def get_dict():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    return jsonify(data)

@app.route('/task', methods=['GET', 'POST'])
def get_task():
    data = request.get_json(silent=True) or {}
    uuid = data.get('uuid') or request.args.get('uuid')

    if not uuid:
        return jsonify({'error': 'Missing uuid parameter'}), 400

    tw = TaskWarrior()
    task = tw.tasks.get(uuid=uuid)
    print (task)
    return jsonify({'description': task['description'], 'uuid': uuid})
    # try:
    #     
    # except Exception as e:
    #     return jsonify({'error': f'Task not found: {str(e)}'}), 404

if __name__ == '__main__':
    app.run(debug=True)
