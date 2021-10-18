from flask import Flask, render_template, request, Response
from werkzeug.utils import redirect, secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os
import model as md

app = Flask(__name__)

# image uploading 
app.secret_key = "UniFI-image"
app.config['UPLOAD_PATH'] = 'static/data/'       # UPLOAD_PATH = 'static/uploads/'
app.config['TEMP_UPLOAD'] = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
credentials = {'admin': 'UniFI'}    # admin panel credentials 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mldata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MLData(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(30), nullable=False)
    rollno = db.Column(db.String(30), nullable=False)
    dateofbirth = db.Column(db.String(12))
    email = db.Column(db.String(30), nullable=False)
    pno = db.Column(db.Integer, nullable=False)
    school = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    zip = db.Column(db.Integer, nullable=False)

    # def __repr__(self) -> str:
    #     return f"{self.sno} - {self.firstname}"

def dateTime():
    # playing with datetime
    date_time = str(datetime.utcnow())
    date_time = date_time.replace(':','')
    date_time = date_time.replace('-','')
    date_time = date_time.replace('.','')
    date_time = date_time.replace(' ','')
    date_time = date_time.strip()
    return date_time

# Start application
@app.route("/", methods=['GET', 'POST'])
def front():
    print('main-UniFI') 
    data = ""
    if request.method=='POST':
        img = request.files['Img']

        # playing with datetime
        date_time = dateTime()
        # changing file name 
        img.filename = date_time+".jpg"

        filename = secure_filename(img.filename)

        path = os.getcwd() + r'\static\uploads'
        if os.path.isdir(path) is False:
            os.mkdir(path)
        
        img.save(os.path.join(app.config['TEMP_UPLOAD'], filename))
        # print(os.path.join(app.config['TEMP_UPLOAD'], filename))
        
        print(filename)
        
        # calling ml model
        check, id = md.fun(filename)
        if check == True:
            sno = int(id.split('.')[0])
            # reterive data from sql
            data = MLData.query.filter_by(sno=sno).first()
            # print(data.firstname)

        # deleting the image 
        path = os.path.join(app.config['TEMP_UPLOAD'], filename)
        if os.path.isfile(path) == True:
            os.remove(path)

        #  using function regaring sql
        # alldata = MLData.query.with_entities(MLData.sno)
        # for x in alldata:
        #     print(x.sno)
        # path = 'static/data/'
        # print(os.listdir(os.path.abspath(path)))
        # ins = inspect(MLData)
        # print(ins.primary_key) 


        return render_template('index.html', data=data)
    return render_template('index.html', data=data)


login_check=0   #use for load login page inbuild in admin.html
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    print('admin-UniFI') 
    del_time = dateTime()       #for securing deletion
    update_time = dateTime()    #for securing to go derect in update
    global login_check
    if request.method=='POST':
        global login_check
        if request.form.get('submit'):
            print('login-UniFI')
            user = request.form['user']
            pwd = request.form['pwd']
            print(user)
            if user not in credentials:
                return render_template('admin.html', info="Invalid User", login_check=0)
            else:
                if credentials[user]!=pwd:
                    return render_template('admin.html', info="Invalid Password", login_check=0)
                else:
                    print('login')
                    login_check=1
                    # return render_template('admin.html', login_check=1)
        else:
            # login_check=1
            fullname = request.form['FullName']
            rollno = request.form['RollNo']
            dateofbirth = request.form['DateofBirth']
            email = request.form['Email']
            pno = request.form['PNo']
            school = request.form['school']
            address = request.form['Address']
            city = request.form['City']
            state = request.form['State']
            zip = request.form['Zip']
            mldata = MLData(fullname=fullname, rollno=rollno, dateofbirth=dateofbirth, email=email, pno=pno, school=school, address=address, city=city, state=state, zip=zip)
            db.session.add(mldata)
            db.session.commit()
            # Image
            img = request.files['Img']
            if img:
                path = os.getcwd() + r'\static\data'
                if os.path.isdir(path) is False:
                    os.mkdir(path)
                # print(img.filename)
                # file_extension = (img.filename).rsplit('.',1)[1].lower()
                img.filename = str(mldata.sno)+".jpg"
                # print(img, img.filename, type(file_extension))
                filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                # os.rename(img,mldata.sno)
                # print(mldata.sno)  # serial key of data
            login_check=1
            print('login_check', login_check)
    if login_check == 1:
        alldata = MLData.query.all() 
        login_check = 0
        return render_template('admin.html', alldata=alldata, login_check=1, del_time=del_time, update_time=update_time)
    return render_template('admin.html', login_check=0)
    


@app.route('/admin/delete/<string:del_time>/<int:sno>')
def delete(del_time, sno):
    print('del time', del_time)
    mldata = MLData.query.filter_by(sno=sno).first()
    filename = str(mldata.sno)+".jpg"
    path = os.path.join(app.config['UPLOAD_PATH'], filename)
    if os.path.isfile(path) == True:
        os.remove(path)
    db.session.delete(mldata)
    db.session.commit()
    global login_check
    login_check = 1 
    return redirect('/admin')

@app.route('/admin/update/<string:update_time>/<int:sno>', methods=['GET', 'POST'])
def update(update_time, sno):
    if request.method=='POST':
        fullname = request.form['FullName']
        rollno = request.form['RollNo']
        dateofbirth = request.form['DateofBirth']
        email = request.form['Email']
        pno = request.form['PNo']
        school = request.form['school']
        address = request.form['Address']
        city = request.form['City']
        state = request.form['State']
        zip = request.form['Zip']
        mldata = MLData.query.filter_by(sno=sno).first()
        # updating the data
        mldata.fullname = fullname
        mldata.rollno = rollno
        mldata.dateofbirth = dateofbirth
        mldata.email = email
        mldata.pno = pno
        mldata.school = school
        mldata.address = address
        mldata.city = city
        mldata.state = state
        mldata.zip = zip
        db.session.add(mldata)
        db.session.commit()
        # Image
        
        img = request.files['Img']
        print(img)
        if img:
            path = os.getcwd() + r'\static\data'
            if os.path.isdir(path) is False:
                os.mkdir(path)
            # print(img.filename)
            # file_extension = (img.filename).rsplit('.',1)[1].lower()
            img.filename = str(mldata.sno)+".jpg"
            # print(img, img.filename, type(file_extension))
            filename = secure_filename(img.filename)
            path = os.path.join(app.config['UPLOAD_PATH'], filename)
            if os.path.isfile(path) == True:
                os.remove(path)
            img.save(path)
            # os.rename(img,mldata.sno)
            # print(mldata.sno)  # serial key of data
        global login_check
        login_check=1
        print('update')
        return redirect('/admin')
    data = MLData.query.filter_by(sno=sno).first()
    return render_template('update.html', data=data, update_time=update_time)


@app.route("/about")
def about():
    print('about')
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)