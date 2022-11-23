""" jiani, customer """
import mysql.connector
import json
from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import sys  

app = Flask(__name__)
api = Api(app)

meetingdb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="meeting"
)
cursor = meetingdb.cursor() 

# set table contents for API contact
parser = reqparse.RequestParser()
parser.add_argument('username',  location='args')
parser.add_argument('email', location='args')
parser.add_argument('id', type=int, location='args')

# get table terms in userkey
cursor.execute("desc users")
userkeys = [column[0] for column in cursor.fetchall()]

class Customer(Resource):
    """ customer class """
   
    def get(self, id):
        query = ("SELECT * FROM users where id=%s;" % (id))
        cursor.execute(query)
        for content in cursor:
            userInfo = {k:c for k, c in zip(userkeys, content)}
            userjson = json.dumps(userInfo)
        return userjson

    def put(self, id):
        args = parser.parse_args()
        try:
            updateContents = ""
            for k, v in args.items():
                if v:
                    if k == "id":
                        updateContents+=k+"="+str(v)+","
                    else:
                        updateContents+=k+"='"+v+"',"
            updateContents = updateContents[:-1]
            updatequery = "UPDATE users SET " + updateContents + " WHERE id=%s;" % (id)
            cursor.execute(updatequery)
        except:
            # if id not found then create new
            insertKeys = "(id, "
            insertVals = "(%s, " %id
            for k, v in args.items():
                if v:
                    insertKeys += k+","
                    if k == "id":
                        continue
                    else:
                        insertVals += "'"+v+"'"+","
            insertKeys = insertKeys[:-1]+")"
            insertVals = insertVals[:-1]+");"
            insertquery = "INSERT INTO users "+  insertKeys + " VALUES " + insertVals
            cursor.execute(insertquery)
        return "", 201

    def delete(self, id):
        query = ("DELETE FROM users where id=%s;" % (id))
        cursor.execute(query)
        return '', 201

 
class Customers(Resource):
    def get(self):
        query = ("SELECT * FROM users;")
        cursor.execute(query)
        contents = []
        for content in cursor:
            contents.append({k:c for k, c in zip(userkeys, content)})

        contentsjson = json.dumps(contents)
        return contentsjson

    def post(self, id):
        args = parser.parse_args()
        insertKeys = "(id, "
        insertVals = "(%s, " %id
        for k, v in args.items():
            if v:
                insertKeys += k+","
                if k == "id":
                    continue
                else:
                    insertVals += "'"+v+"'"+","
        insertKeys = insertKeys[:-1]+")"
        insertVals = insertVals[:-1]+");"
        insertquery = "INSERT INTO users "+  insertKeys + " VALUES " + insertVals
        cursor.execute(insertquery)
        return "", 201

api.add_resource(Customers, '/customers')
api.add_resource(Customer, '/customer/<id>')

if __name__ == '__main__':
    app.run(debug=True)

    cursor.close()
    meetingdb.close()
