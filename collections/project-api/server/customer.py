""" jiani, customer """

import sys   


class Customer:
    """ customer class """
   
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

 
# table sql save the customer.
# api create, read, update, delete. 