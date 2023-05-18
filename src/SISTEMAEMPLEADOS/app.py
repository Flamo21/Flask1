from flask import Flask
from flask import render_template,request,redirect
from flaskext.mysql import MySQL
from flask import send_from_directory #Poder enviar imagen de un directorio

from datetime import datetime
import os #Modulo para ingresar a los archivos del sistema, y editar la foto

app = Flask(__name__) #__name__ : Permite que se ejecute como un modulo independiente

mysql=MySQL() #Declaramos la conexión
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='Admin12345.'
app.config['MYSQL_DATABASE_DB']='sistema'

mysql.init_app(app) #Inicializamos la conexión

carpeta=os.path.join('uploads') #Referenciamos la carpeta
app.config['carpeta']=carpeta

#app.route: Función de Flask que sirve para declarar a que enlace queremos conectar


@app.route('/uploads/<nombreFoto>')#Llamamos a la carpeta donde esta las imagenes
def uploads(nombreFoto):
    return send_from_directory(app.config['carpeta'],nombreFoto)


@app.route('/')  #Sirve para declarar el nombre de la pagina que queremos mostrar o lo que queramos ejecutar
def index(): #Al declarar el codigo sql, cada vez que arranquemos la pagina se insertara la info dada

    sql="SELECT * FROM empleados;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destruir/<int:id>')
def destruir(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    
    cursor.execute("SELECT foto FROM empleados WHERE id =%s",id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['carpeta'],fila[0][0]))


    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
    
    conn.commit()
    return redirect('/')#Importamos redirect de Flask para redireccionar luego de la acción hecha



@app.route('/update/', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtEmail']
    _foto=request.files['txtFoto']
    id=request.form['txtID']
    sql="UPDATE empleados SET nombre=%s,correo=%s WHERE empleados.id=%s ;"
    datos=(_nombre,_correo,id)
    
    conn=mysql.connect()
    cursor=conn.cursor()
    
    cursor.execute(sql,datos)
    conn.commit()
    
    now=datetime.now()
    time=now.strftime("%Y%H%S")
    
    if _foto.filename != "":
        nuevonombreFoto=time+_foto.filename 
        _foto.save("uploads/"+nuevonombreFoto)
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila=cursor.fetchall()
        
        os.remove(os.path.join(app.config['carpeta'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevonombreFoto,id))
        conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s",(id))
    empleados=cursor.fetchall()
    conn.commit()
    
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/create')
def method_name():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST']) #Creamos un route, pero con el metodo POST para que pueda recibir la información de un HTML
def storage():
    _nombre=request.form['txtNombre']#Importar request de Flask para poder usarlo
    _correo=request.form['txtEmail']#Importar request de Flask para poder usarlo
    _foto=request.files['txtFoto']#Como es archivo cambiamos el form por file

    now=datetime.now()
    time=now.strftime("%Y%H%M%S")
    
    if _foto.filename != "":
        nuevonombreFoto=time+_foto.filename 
        _foto.save("uploads/"+nuevonombreFoto)
    
    sql="INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s,%s,%s);"
    
    datos=(_nombre,_correo,nuevonombreFoto)#Como la imagen es grande, solo necesitamos el nombre y ubicación
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)