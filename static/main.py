import cv2
from flask import Flask, request, render_template
import settings
import utils
import numpy as np


app = Flask(__name__)
app.secret_key = "myapp"

doc_scan = utils.DocumentScan()

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image_name"]
        path = doc_scan.save_image(file)
        print(f'Image saved to {path}')

        pts, size = doc_scan.find_doc(path)
        # print(pts, size)

        if pts is None:
            message = "Document could not be found autmaticaly. Please manually select the document area."
            points = [
                {'x': 0, 'y': 0},
                {'x': 0, 'y': size[1]},
                {'x': size[0], 'y': 0},
                {'x': size[0], 'y': size[1]}
            ]
            return render_template("scanner.html", message=message, points=points, fileupload=True)
        else:
            points = []
            for pt in pts.tolist():
                points.append({'x': pt[0], 'y': pt[1]})
            message = "Document located. Edit the selected area or click 'Scan' to proceed."
            return render_template("scanner.html", message=message, points=points, fileupload=True)

    
    return render_template("scanner.html")

@app.route("/about")
def about():
    return render_template("about.html")

# API
@app.route("/crop", methods=["POST"])
def transform():
    try:
        pts = request.json["data"]
        array = np.array(pts)
        cropped_img = doc_scan.calibrate(array)
        cv2.imwrite("static/media/cropped_img.jpg", cropped_img)
        return "Success"
    except:
        return "Failed"

if __name__ == "__main__":
    app.run(debug=True)

   