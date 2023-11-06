import random
import tensorflow as tf
from keras.preprocessing import image
import librosa
import librosa.display
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import gcf
import os
import numpy as np
from urllib.parse import quote

from PIL import Image, ImageFile
from tensorflow.keras.utils import img_to_array
try:
    from PIL import Image
except ImportError:
    import Image
matplotlib.use('Agg')
import requests
import bs4

model_load = tf.keras.models.load_model('model.h5', compile=False)

# Flask utils
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

def create_spectrogram(file):
    """ loads audio file and creates spectrogram """
    signal, sr = librosa.load(file, duration=10)
    fig = gcf()
    DPI = fig.get_dpi()
    fig = plt.figure()
    fig.set_size_inches(6, 6)

    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    S = librosa.feature.melspectrogram(
        y=signal,
        sr=sr,
        n_fft=1024,
        hop_length=1024,
        n_mels=128,
        htk=True,
        fmin=1400,
        fmax=sr / 2
    )
    librosa.display.specshow(
        librosa.power_to_db(S ** 2, ref=np.max),
        fmin=1400,
        y_axis='linear'
    )
    fig.savefig("trail.png")
    img = image.load_img('trail.png', grayscale=False, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    return x, fig


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


birdClassLong = ['Dendrocopos major', 'Coccothraustescoccothraustes', 'Delichon urbicum', 'Apus apus', 'Turdus pilaris', 'Passer montanus', 'Garrulus glandarius', 'Podiceps gallardoi', 'Antilophia bokermanni']
birdQ = ['Dendrocopos+major', 'Coccothraustescoccothraustes', 'Delichon+urbicum', 'Apus+apus', 'Turdus+pilaris', 'Passer+montanus', 'Garrulus+glandarius', 'Podiceps+gallardoi', 'Antilophia+bokermanni']
season = ['Spring', 'End of March and mid-August', 'Migrate to South America for the winter', 'Late April to early May', 'Northern birds moving south during the winter', 'Nonmigratory in North America, but may wander outside resident range during the nonbreeding season',
          'Begins in April', 'April(autumn)', 'Commence in August, peak in September/October']
category = ['Resident', 'Resident and migratory', 'Migratory', 'Resident', 'Migratory', 'Resident and migratory', 'Resident ', 'Full migrant', 'Resident']
birdCommon = ['Great spotted woodpecker', 'Hawfinch', 'House Martin', 'Common swift', 'Fieldfares', 'Eurasian tree sparrow', 'Eurasian jay', 'Hooded grebe', 'Araripe manakin']
birdClassShort = ['0Dendr', '1Cocco', '2Delic', '3Apusa', '4Turdu', '5Passe', '6Garru', '7Podic', '8Antil']


def get_conservation(name):
    url = 'https://google.com/search?q=' + quote(name) + "+conservation+status&hl=en"
    print(url)
    request_result = requests.get(url)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")

    try:
        div = soup.find('div', attrs={"class": "BNeawe iBp4i AP7Wnd"})
        status = div.select('div.BNeawe.iBp4i.AP7Wnd')[0].get_text()
        print("CS:", status)
        return status
    except AttributeError:
        print("Error occurred while scraping conservation status.")
        return "N/A"


def get_image(name):
    url = 'https://google.com/search?q=' + quote(name) + "+conservation+status&tbm=isch"
    print(url)
    request_result = requests.get(url)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    images = soup.findAll('img')
    ind = random.randint(1, len(images))
    print("Image:", images[ind].get('src'))
    return images[ind].get('src')


@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            f = request.files['file']
            basepath = os.path.dirname(__file__)
            file_path = os.path.join(
                basepath, 'uploads', secure_filename(f.filename))
            f.save(file_path)

            print("File----", file_path)
            image, fig = create_spectrogram(file_path)
            print("Shape--", image.shape)
            preds = model_load.predict(image)
            print("Res", preds[0])
            a = preds
            ind = np.argmax(a)
            print("index-", ind)
            status = get_conservation(birdQ[ind])
            img_link = get_image(birdQ[ind])

            res = {
                'status': 'success',
                'Cstatus': status,
                'image': str(img_link),
                'bird': birdClassLong[ind],
                'birdCommon': birdCommon[ind],
                'birdCat': category[ind],
                'birdSeason': season[ind]
            }
            print(res)
            return jsonify(res)

        except Exception as e:
            res = {
                'status': 'error',
                'message': 'An error occurred',
                'error': str(e)
            }
            return jsonify(res)


    return jsonify({'status': '', 'message': 'Invalid request method'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
