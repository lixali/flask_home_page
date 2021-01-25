import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash, send_from_directory
from database import list_users, verify, delete_user_from_db, add_user
from database import read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id
from database import image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db
from werkzeug.utils import secure_filename
import subprocess
import sys


app = Flask(__name__)
app.config.from_object('config')



@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413




@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")

@app.route("/intro/")
def FUN_intro():
    return render_template("public_intro.html")

FLAG = ""
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = '/Users/mac/Downloads/'
#UPLOAD_FOLDER = '/home/ubuntu/image_ID_protection/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
target = os.path.join(APP_ROOT, 'static/', 'usr_upload/')
#app.config['UPLOAD_FOLDER'] = target
if not os.path.isdir(target):
    os.mkdir(target)
else:
    print("Couldn't create upload directory or up directory already exsit: {}".format(target))




@app.route('/uploads/<filename>')
def send_image(filename):
    #return send_from_directory(UPLOAD_FOLDER, filename)
    return send_from_directory("images", filename)


@app.route('/show/<filename>')
def uploaded_file(filename):
    #filename = 'http://0.0.0.0:5000/uploads/' + filename
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    return render_template('image.html', filename=filename)


#@app.route('/upload_image/<filename>')
@app.route('/upload_image/', methods = ['GET', 'POST'])
#@app.route('/upload_image/', methods = ['GET'])
#@app.route('/upload_image/', methods = ['POST'])


###def FUN_upload_file(filename):
###    #filename = 'http://0.0.0.0:5000/upload_image/' + filename
###    filename = 'http://127.0.0.1:5000/uploads/' + filename    
###    return render_template('image.html', filename=filename)
###    #return render_template("image.html")

def FUN_upload_file():
    global FLAG
    FLAG += "1"
    file = request.files['file']
    image_name = file.filename
    print("FILE is", file)
    print("IMAGE NAME IS", image_name)
    print("APP_ROOT is ", APP_ROOT)
    destination = "/".join([target, image_name])
    file.save(destination)
    #subprocess.call('/Users/mac/Downloads/hello.sh')
    #subprocess.check_call(["/home/ubuntu/hello.sh", image_name])
    with open('test.log', 'wb') as f:  # replace 'w' with 'wb' for Python 3
        memory = subprocess.Popen(["./query.sh", image_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(memory.stdout.readline, b''):
            sys.stdout.buffer.write(line)    # for binary data, it needs to be buffer.write
            f.write(line)
            #if b'S3' in line:
                #f.write(line) 
    #subprocess.check_call(["find", "./", "-iname", "read_test.py"])    
    subprocess.check_call(["echo", image_name])    
    #memory2 = subprocess.Popen(["./read_test.py", "test.log"], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.check_call(["pwd"])    
    #subprocess.check_call(["/home/ubuntu/flask-example-master/read_test.py", "test.log"])    
    #subprocess.check_call(["python3", "read_test.py", "test.log"])    

    #memory2 = subprocess.Popen(['grep JPEG', f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
#out,error = memory.communicate()


    #subprocess.check_call(["ls", "-1"])
    #filename = 'http://0.0.0.0:5000/uploads/' + image_name     
    #filename = 'http://127.0.0.1:5000/uploads/' + image_name     
    #filename = 'http://54.80.242.35:5000/uploads/' + image_name
    filename = os.path.join('usr_upload', image_name)
    return render_template('image.html', filename=filename)
    #return render_template("image.html")

@app.route('/search_image/', methods = ['GET', 'POST'])
def FUN_search_file():
    #subprocess.check_call(["aws", "s3", "cp", "s3://puretest1000/ILSVRC2012_val_00001571.JPEG", "./"])
    with open('image_returned.txt', 'r+') as f:
        for line in f:
            if "JPEG" in line and FLAG == "1":
                image_name = line
                #filename = 'http://127.0.0.1:5000/uploads/' + image_name
            else:
                image_name = None
                #filename = None
    return render_template('result.html', filename=image_name)








@app.route("/login", methods = ["POST"])
def FUN_login():
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
    
    return(redirect(url_for("FUN_root")))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))

@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exsit in database. We also need to ensure the id is valid.
        if request.form.get('id').upper() in list_users():
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            add_user(request.form.get('id'), request.form.get('pw'))
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)





if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80)
#    app.run(port=80)
    #app.run(port=80,debug=True)
