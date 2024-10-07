from flask import Flask, jsonify, request
import os
import pickle

app = Flask(__name__)
data_file = './main.dat'

def load_data():
    if os.path.isfile(data_file):
        with open(data_file, 'rb') as file:
            return pickle.load(file)
    else:
        return {}

def save_data(data):
    with open(data_file, 'wb') as file:
        pickle.dump(data, file)

@app.route('/data', methods=['GET'])
def get_data():
    data = load_data()
    return jsonify(data)

@app.route('/data', methods=['POST'])
def update_data():
    data = request.json
    save_data(data)
    return jsonify({'status': 'success'})

@app.route('/add_event', methods=['POST'])
def add_event():
    data = load_data()
    event_data = request.json
    year = event_data['year']
    month = event_data['month']
    day = event_data['day']
    description = event_data['description']
    diamonds = event_data['diamonds']

    if year not in data:
        data[year] = {}
    if month not in data[year]:
        data[year][month] = {}
    if day not in data[year][month]:
        data[year][month][day] = {'total': 0, 'events': []}

    event = {'description': description, 'diamonds': diamonds}
    data[year][month][day]['events'].append(event)
    data[year][month][day]['total'] += diamonds

    save_data(data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)