from flask import render_template, Flask, request
from flask_mysqldb import MySQL
from flask_cors import CORS
import base64
import os
from datetime import datetime
import qrcode

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'hakatonKrasnodar.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'hakatonKrasnodar'
app.config['MYSQL_PASSWORD'] = 'n01082002'
app.config['MYSQL_DB'] = 'hakatonKrasnodar$hacaton_3'
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_list_users", methods=["GET"])
def listok():
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT id,photo,fio FROM users; ''')
    arr = cursor.fetchall()
    cursor.close()
    answer = {}
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    for i in arr:
        with open((os.path.join(THIS_FOLDER,i[1])), "rb") as image_file:
            data = str(base64.b64encode(image_file.read()))
            data = data[2:len(data)-1]
        at = [i[2],data]
        answer[i[0]] = at
    return answer


@app.route("/gen_qr",methods=["GET"])
def gen_qr():
    now = int(datetime.timestamp(datetime.now())//10)%100000000
    message = str(now)
    st = ""
    arr = ["c","k","p","o","y","q","j","x","s","l"]
    for i in message:
        buf = int(i)
        st+=arr[buf]
    img = qrcode.make(st)
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    img.save(os.path.join(THIS_FOLDER,"some_file.png"))
    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO qr VALUES (%s,%s)''',(0,st))
    mysql.connection.commit();
    cursor.close()
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    with open((os.path.join(THIS_FOLDER,"some_file.png")), "rb") as image_file:
        data = str(base64.b64encode(image_file.read()))
    data = data[2:len(data)-1]
    return {"qr":data}

@app.route("/verify_qr", methods=["GET"])
def verify_qr():
    a = request.args["qr"]
    cursor = mysql.connection.cursor()
    qr = a
    print(a)
    cursor.execute('''SELECT id FROM qr WHERE qr = %s''',[a])
    id = cursor.fetchall()
    cursor.close()
    arr = ["c","k","p","o","y","q","j","x","s","l"]
    a = ""
    for i in qr:
        num = 0
        for j in arr:
            if j == i:
                a+=str(num)
            num+=1
    now = int(datetime.timestamp(datetime.now())//10)%100000000
    print(id)
    print(now - int(a))
    if (now - int(a) < 43200) & (len(id) > 0):
        cursor = mysql.connection.cursor()
        cursor.execute('''DELETE FROM qr WHERE qr = %s''',[qr])
        mysql.connection.commit();
        cursor.close()
        print("Ok")
        return {"status":"OK"}
    else:
        return {"status":"Not Ok"}


@app.route("/get_users", methods=['GET'])
def users():
    answer = {}
    typ = int(request.args["type"])
    if(typ == 1) | (typ == 0):
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT id,fio,photo,phone FROM users WHERE type = %s ; ''', str(typ))
        arr = cursor.fetchall()
        cursor.close()
        j = 0
        for i in arr:
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            with open((os.path.join(THIS_FOLDER,i[2])), "rb") as image_file:
                data = str(base64.b64encode(image_file.read()))
                data = data[2:len(data)-1]
            sub_answer = {"id":i[0],"fio":i[1],"photo":data,"phone":i[3]}
            answer[j] = sub_answer
            j+=1
    elif typ == 2:
        print("type 2")
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT id,fio,photo,phone,kid FROM users WHERE type = %s ; ''', str(typ))
        arr = cursor.fetchall()
        cursor.close()
        j = 0
        print(arr)
        for i in arr:
            kids = ""
            if i[4] is None:
                kids = "-"
            else:
                for f in i[4].split(" "):
                    cursor = mysql.connection.cursor()
                    cursor.execute(''' SELECT fio FROM users WHERE id = %s;''',[str(f)])
                    arm = cursor.fetchall()
                    cursor.close()
                    # if len(kids) > 0:
                    kids += arm[0][0] + ' , '
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            with open((os.path.join(THIS_FOLDER,i[2])), "rb") as image_file:
                data = str(base64.b64encode(image_file.read()))
                data = data[2:len(data)-1]
            sub_answer = {"id":i[0],"fio":i[1],"photo":data,"phone":i[3], "kids":kids}
            answer[j] = sub_answer
            j+=1
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT id,fio,photo,phone,groupa FROM users WHERE type = %s ; ''', str(typ))
        arr = cursor.fetchall()
        cursor.close()
        j = 0
        for i in arr:
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            with open((os.path.join(THIS_FOLDER,i[2])), "rb") as image_file:
                data = str(base64.b64encode(image_file.read()))
                data = data[2:len(data)-1]
            sub_answer = {"id":i[0],"fio":i[1],"photo":data,"phone":i[3], "groupa":i[4]}
            answer[j] = sub_answer
            j+=1
    return answer

@app.route("/search_user", methods=["GET"])
def search():
    part = request.args["part"]
    cursor = mysql.connection.cursor()
    cursor.execute(" SELECT id,fio,photo,phone,kid FROM users WHERE fio LIKE '%"+part+"%' ;")
    arr = cursor.fetchall()
    cursor.close()
    j = 0
    answ = {}
    kids = ""
    for i in arr:
        kids = ""
        if i[4] is None:
            kids = "-"
        else:
            for f in i[4].split(" "):
                cursor = mysql.connection.cursor()
                cursor.execute(''' SELECT fio FROM users WHERE id = %s;''',[str(f)])
                arr = cursor.fetchall()
                cursor.close()
                if len(kids) > 0:
                    kids += arr[0][0] + ' , '
        data = None
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        with open((os.path.join(THIS_FOLDER,i[2])), "rb") as image_file:
            data = str(base64.b64encode(image_file.read()))
            data = data[2:len(data)-1]
        sub_answ = {"id":i[0],"fio":i[1],"photo":data,"phone":i[3], "kids":kids}
        answ[j] = sub_answ
        j+=1
    return answ

@app.route("/add_user", methods=['POST'])
def user():
    id = 0
    fio = None
    groupa = None
    photo = None
    inst = None
    phone = None
    kid = None
    typ = int(request.args["type"])
    img_data = str(request.args["pic"].split(",")[1]).replace(" ", "+")
    cursor = mysql.connection.cursor();
    cursor.execute(''' SELECT MAX(id) FROM users; ''')
    ind = int(cursor.fetchall()[0][0])
    cursor.close()
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    ind = ind+1
    fh = open((os.path.join(THIS_FOLDER,"img/"+str(ind)+".png")), "wb")
    fh.write(base64.b64decode(img_data))
    fh.close()
    photo = "img/"+str(ind)+".png"
    if typ == 0 | typ == 1:
        fio = request.args["fio"]
        inst = request.args["inst"]
        phone = request.args["phone"]
    elif typ == 2:
        fio = request.args["fio"]
        inst = request.args["inst"]
        phone = request.args["phone"]
        kid = request.args["kid"]
    else:
        fio = request.args["fio"]
        groupa = request.args["group"]
        inst = request.args["inst"]
        phone = request.args["phone"]
    stat = {"status":"ok"}
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',(id,fio,groupa,photo,typ,inst,phone,kid))
    mysql.connection.commit()
    cursor.close()
    return stat

@app.route("/send_to_verification_users", methods=["POST"])
def send_to_verif():
    id = 0
    fio = None
    groupa = None
    photo = None
    inst = None
    phone = None
    kid = None
    img_data = str(request.args["pic"].split(",")[1]).replace(" ", "+")
    cursor = mysql.connection.cursor();
    cursor.execute(''' SELECT MAX(id) FROM verification; ''')
    ind = int(cursor.fetchall()[0][0])
    cursor.close()
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    ind = ind+1
    fh = open((os.path.join(THIS_FOLDER,"img/"+str(ind)+".png")), "wb")
    fh.write(base64.b64decode(img_data))
    fh.close()
    photo = "img/"+str(ind)+".png"
    typ = int(request.args["type"])
    fio = request.args["fio"]
    inst = request.args["inst"]
    phone = request.args["phone"]
    kid = request.args["kid"]
    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO verification VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(id,fio,groupa,photo,typ,inst,phone,kid,0))
    mysql.connection.commit()
    cursor.close()
    return {"status":"ok"}

@app.route("/verificate_user", methods=["GET"])
def verifcate_get():
    answer = {}
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT id,fio,photo,phone,kid FROM verification WHERE status = %s ; ''', str(0))
    arr = cursor.fetchall()
    cursor.close()
    j = 0
    for i in arr:
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        with open((os.path.join(THIS_FOLDER,i[2])), "rb") as image_file:
            data = str(base64.b64encode(image_file.read()))
            data = data[2:len(data)-1]
        sub_answer = {"id":i[0],"fio":i[1],"photo":data,"phone":i[3], "kids":i[4]}
        answer[j] = sub_answer
        j+=1
    return answer

@app.route("/verificate_user", methods=["POST"])
def post_verif():
    params = request.args["ver"]
    id = request.args["id"]
    cursor = mysql.connection.cursor()
    print(params)
    if params == str(1):
        cursor.execute('''SELECT * FROM verification WHERE id = %s ;''', id)
        arr = cursor.fetchall()[0]
        cursor.execute(''' INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', (0,arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7]))
        mysql.connection.commit()
    cursor.execute('''UPDATE verification SET status = %s WHERE id = %s ;''', (params,id))
    mysql.connection.commit()
    cursor.close()
    return {"status":"ok"}
