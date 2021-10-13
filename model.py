
import app as ap
import cv2 as cv
import face_recognition

def fun(filename):
    img_loc = ap.os.getcwd() + r'\static\uploads'
    print(img_loc, type(img_loc))
    img_loc = ap.os.path.join(img_loc, filename)
    print(img_loc, type(img_loc))
    # img_loc = r'C:\Users\hanum\Desktop\Project\ML\static\data\1.jpg'
    img = cv.imread(img_loc)
    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_endcoding = face_recognition.face_encodings(rgb_img)[0]

    path = ap.os.getcwd() + '\static\data'
    print(path)
    alldata = ap.os.listdir(path) 
    print(alldata, type(alldata))
   
    for x in alldata:
        dir = ap.os.path.join(path, x)
        print(dir)        
        img2 = cv.imread(dir)
        rgb_img2 = cv.cvtColor(img2,cv.COLOR_BGR2RGB)
        img_endcoding2 = face_recognition.face_encodings(rgb_img2)[0]
        result = face_recognition.compare_faces([img_endcoding], img_endcoding2)
        if result[0] == True:
            print('Result:', result)   
            return True, x
        print('Result:', result, type(result), type(result[0]))
    return False, 'No'
        