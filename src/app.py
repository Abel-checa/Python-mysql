from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:abel@localhost/flaskmysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

app.app_context().push() #abriendo un contexto de manera manual si no no se puede usar db.create_all()
db = SQLAlchemy(app)
ma = Marshmallow(app)

## Creamos el modelo
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))

    def __init__(self,title,description):
        self.title = title
        self.description = description

##Lee todas las clases que sean db.Models.
##Crea todas las tablas que tengamos definidas como en este caso Task
db.create_all()

## Creamos un esquema para interactuar de forma facil con nuestros modelos.
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many = True)

#Ruta de creacion de Tareas con el metodo POST
@app.route('/tasks', methods=['POST'])### La funcion que maneja la ruta es la de abajo.

def create_task():
    title = request.json['title']
    description = request.json['description']
    
    ##Llamamos a el constructor de Task para crear una nueva tarea
    new_task = Task(title,description)
    print("Tarea creada con exito.")

    ##Almacenamos lo datos en la BD
    db.session.add(new_task)
    db.session.commit()
    print("Almacenamiento en la bd ---> OK")
    
    return task_schema.jsonify(new_task)

#Ruta de read con metodo get para visualizar las tareas.
@app.route('/tasks',methods=['GET'])

def get_tasks():
    ##Nos devuelve las tareas
    all_tasks = Task.query.all()
    #lista con los datos 
    result = tasks_schema.dump(all_tasks)

    ## Convertimos en json los resultados de la base de datos por el ORM
    return jsonify(result)

##Ruta de read Task get
@app.route('/task/<id>',methods=['GET'])

def get_task(id):
    mytask = Task.query.get(id)

    return task_schema.jsonify(mytask)


##  Ruta de update para la base de datos 
@app.route('/tasks/<id>',methods=['PUT'])

def update_task(id):
    task = Task.query.session.get(Task, id)
    title = request.json['title']
    description = request.json['description']
    task.title = title
    task.description = description
    db.session.commit()
    print(title,description)

    return task_schema.jsonify(task)

## Ruta Delete Task  -- DELETE 

@app.route('/tasks/<id>',methods=['DELETE'])

def delete_task(id):
    task = Task.query.session.get(Task, id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)


@app.route('/',methods=['GET'])

def index():
    content = """<html>
    
    <body>
    <h1>Bienvenido a la Api de Abel</h1>
    </body>
    </html>"""

    return content


@app.route('/tasks/delete',methods=["DELETE"])

def delete_tasks():
    db.session.query(Task).delete()
    db.session.commit()
    
    return jsonify({'mensage':"All task deleted"})


if __name__ == '__main__':
    app.run(debug=True)