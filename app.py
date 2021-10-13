from flask import Flask, render_template, request, Response
from werkzeug.utils import redirect, secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os
import model as md

app = Flask(__name__)

# image uploading 
app.secret_key = "vishal-image"
app.config['UPLOAD_PATH'] = 'static/data/'       # UPLOAD_PATH = 'static/uploads/'
app.config['TEMP_UPLOAD'] = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
credentials = {'admin': 'vishal'}    # admin panel credentials 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mldata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MLData(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    pno = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    zip = db.Column(db.Integer, nullable=False)

    # def __repr__(self) -> str:
    #     return f"{self.sno} - {self.firstname}"


# Start application
@app.route("/", methods=['GET', 'POST'])
def front():
    print('main-vishal') 
    data = ""
    if request.method=='POST':
        img = request.files['Img']

        # playing with datetime
        date_time = str(datetime.utcnow())
        date_time = date_time.replace(':','')
        date_time = date_time.replace('-','')
        date_time = date_time.replace('.','')
        date_time = date_time.replace(' ','')
        date_time = date_time.strip()
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
        id = md.fun(filename)
        sno = int(id.split('.')[0])

        # reterive data from sql
        data = MLData.query.filter_by(sno=sno).first()
        # print(data.firstname)
        # print(data.lastname)
        # print(data.state)
        # print(data.city)

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
    




@app.route('/login', methods=['GET', 'POST'])
def login():
    print('login-vishal')
    if request.method=='POST':
        user = request.form['user']
        pwd = request.form['pwd']
        print(user)
        if user not in credentials:
            return render_template('login.html', info="Invalid User")
        else:
            if credentials[user]!=pwd:
                return render_template('login.html', info="Invalid Password")
            else:
                return redirect('/admin')
    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    print('admin-vishal')
    if request.method=='POST':
        firstname = request.form['FirstName']
        lastname = request.form['LastName']
        email = request.form['Email']
        pno = request.form['PNo']
        address = request.form['Address']
        city = request.form['City']
        state = request.form['State']
        zip = request.form['Zip']
        mldata = MLData(firstname=firstname, lastname=lastname, email=email, pno=pno, address=address, city=city, state=state, zip=zip)
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
    alldata = MLData.query.all()
    return render_template('admin.html', alldata=alldata)


@app.route('/delete/<int:sno>')
def delete(sno):
    mldata = MLData.query.filter_by(sno=sno).first()
    filename = str(mldata.sno)+".jpg"
    path = os.path.join(app.config['UPLOAD_PATH'], filename)
    if os.path.isfile(path) == True:
        os.remove(path)
    db.session.delete(mldata)
    db.session.commit()
    return redirect('/admin')

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        firstname = request.form['FirstName']
        lastname = request.form['LastName']
        email = request.form['Email']
        pno = request.form['PNo']
        address = request.form['Address']
        city = request.form['City']
        state = request.form['State']
        zip = request.form['Zip']
        mldata = MLData.query.filter_by(sno=sno).first()
        # updating the data
        mldata.firstname = firstname
        mldata.lastname = lastname
        mldata.email = email
        mldata.pno = pno
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
        return redirect('/admin')
    data = MLData.query.filter_by(sno=sno).first()
    return render_template('update.html', data=data)


@app.route("/about")
def about():
    print('about')
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)