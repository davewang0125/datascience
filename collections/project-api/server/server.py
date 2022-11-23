from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from app import translate_text 

app = Flask(__name__)
api = Api(app)

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')

# Todo
#   show a single todo item and lets you delete them
class Translation(Resource):
    def get(self, text ):
        return translate_text(text) 

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(Translation, '/translate/<string:text>')
api.add_resource(Customer, '/customer/<string:text>')
api.add_resource(Meeting, '/meeting/<string:text>')


if __name__ == '__main__':
    app.run(debug=True)
