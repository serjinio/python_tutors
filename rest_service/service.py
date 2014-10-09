
import pdb
import flask
from flask import Flask, jsonify, abort, make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy

import sqlalchemy
import inspect


# Flask top-levels
############################################################


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
auth = HTTPBasicAuth()


# Database top-levels
############################################################


db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.done
            }

    def __getitem__(self, name):
        if hasattr(self, name) and type(getattr(type(self), name)) == \
           sqlalchemy.orm.attributes.InstrumentedAttribute:
            return getattr(self, name)
        else:
            raise KeyError('No "{}" item found.'.format(name))

    def __repr__(self):
        return '<Task({})>'.format(self.title)

    def __str__(self):
        return 'Task:\n \tTitle: {}\n \tDescription: {}'.format(
            self.title, self.description)


# Routes
############################################################


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
# @auth.login_required
def get_tasks():
    tasks = Task.query.all()
    print 'tasks'
    print 'task name: ', tasks[0]['title']
    return jsonify(tasks=[t.as_dict() for t in tasks])


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.filter(Task.id == task_id).one()
    except:
        abort(404)

    return jsonify({'task': task.as_dict()})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or 'title' not in request.json:
        abort(400)

    new_task = Task(
        title=request.json['title'],
        description=request.json.get('description'))
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({'task': new_task.as_dict()}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.filter(Task.id == task_id).one()
    except:
        abort(404)
        
    conds_400 = [
        'description' in request.json and
        type(request.json['description']) is not unicode,
        
        'done' in request.json and type(request.json['done']) is not bool
    ]
    
    if any(conds_400):
        abort(400)

    task.title = request.json.get('title', task.title)
    task.description = request.json.get(
        'description', task.description)
    task.done = request.json.get('done', task.done)

    db.session.commit()
    
    return jsonify({'task': task.as_dict()})

    
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.filter(Task.id == task_id).one()
    except:
        abort(404)
    
    db.session.remove(task)
    db.session.commit()
    
    return jsonify({'result': True})


@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def get_user_attributes(cls):
    boring = dir(type('dummy', (object,), {}))
    return [item
            for item in inspect.getmembers(cls)
            if item[0] not in boring]


if __name__ == '__main__':
    # app.run(debug=True)
    t = Task(title='some title')
    print get_user_attributes(t)

    pdb.set_trace()

