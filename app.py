import tensorflow
import flask
import urllib.request
from PIL import Image, ImageOps
import numpy as np
import ast

# Use app with Flask Server
app = flask.Flask(__name__)


# Predefine first_class_names, first_model
'''
0 red
1 green
'''
first_class_names = None
first_model = None

# Predefine third_class_names, third_model
'''
0 red
1 green
2 yellow
3 blue
'''
third_class_names = None
third_model = None



# Main home page
@app.route('/')
def main():
    return """<h1>안녕</h1>"""




# run first model
def load_first_model():
    global first_class_names, first_model

    first_class_names = open('first_labels.txt', 'r').readlines()
    first_model = tensorflow.keras.models.load_model('keras_first_model.h5', compile=False)
    
# first model api
@app.route("/api/first/predict", methods=["POST"])
def api_first_predict():
    global first_class_names, first_model

    # UserRequest 중 발화를 req에 parsing.
    req = flask.request.get_json()
    req = req['userRequest']['utterance']
    print(f'사용자의 발화가 들어왔을 때를 나타냄 : {req}')

    body = flask.request.get_json()

    image_with_information = body['action']['params']['secureimage']
    print(f"req['action']['params']['secureimage'] : {image_with_information}")
    print()

    user_id = body['userRequest']['user']['id']
    print(f"user_id : {user_id}")
    print()

    # 문자열로 바꿔주는 코드 (json 형식이라 필히 해야함)
    image_urls = ast.literal_eval(image_with_information)
    new_url = image_urls['secureUrls']

    saved_image_url = new_url[5:-1]
    print(f"저장된 최종 이미지 url : {saved_image_url}")
    print()

    np.set_printoptions(suppress=True)
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # 'img'안에 saved_image_url을 넣어줌
    urllib.request.urlretrieve(saved_image_url, 'img')

    image = Image.open('img').convert('RGB')
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    # 모델을 돌리는 곳 이게 좀 오래걸림
    prediction = first_model.predict(data)

    # 가장 확률이 높은 인덱스를 찾아주는 것
    index = np.argmax(prediction)

    # 가장 확률이 높은 색상을 (index)를 통해 class_name에 넣어주는 것
    class_name = first_class_names[index]
    confidence_score = round(prediction[0][index], 2)

    print(f'빨간색 : {round(prediction[0][0] * 100, 2)}')
    print(f'초록색 : {round(prediction[0][1] * 100, 2)}')

    print("Class : ", class_name[2:], end='')
    print("Confidence Score : ", confidence_score)
    print()

    red_perc, green_perc = \
    str(round(prediction[0][0] * 100, 2)), str(round(prediction[0][1] * 100, 2))

    if str(class_name[2:]).strip() == 'red':
        color = '빨간색'
    elif str(class_name[2:]).strip() == 'green':
        color = "초록색"

    msg = color
    print(msg)

# Basic Card Format
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": "판별 색깔 : " + msg,
                        "description": "빨강색 : " + red_perc + '%\n' + "초록색 : " + green_perc + '%\n',
                        "thumbnail": {
                            "imageUrl": saved_image_url
                        },
                        "buttons": [
                            {
                                "action":  "webLink",
                                "label": "전송한 사진 다시 보기",
                                "webLinkUrl": saved_image_url
                            }
                        ]
                    }
                }
            ]
        }
    }
    print(res)
    return flask.jsonify(res)





# run third model
def load_third_model():
    global third_class_names, third_model

    third_class_names = open('third_labels.txt', 'r').readlines()
    third_model = tensorflow.keras.models.load_model('keras_third_model.h5', compile=False)


# third model api
@app.route("/api/third/predict", methods=["POST"])
def api_third_predict():
    global third_class_names, third_model

    # UserRequest 중 발화를 req에 parsing.
    req = flask.request.get_json()
    req = req['userRequest']['utterance']
    print(f'사용자의 발화가 들어왔을 때를 나타냄 : {req}')

    body = flask.request.get_json()

    image_with_information = body['action']['params']['secureimage']
    print(f"req['action']['params']['secureimage'] : {image_with_information}")
    print()

    user_id = body['userRequest']['user']['id']
    print(f"user_id : {user_id}")
    print()

    # 문자열로 바꿔주는 코드 (json 형식이라 필히 해야함)
    image_urls = ast.literal_eval(image_with_information)
    new_url = image_urls['secureUrls']

    saved_image_url = new_url[5:-1]
    print(f"저장된 최종 이미지 url : {saved_image_url}")
    print()

    np.set_printoptions(suppress=True)
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # 'img'안에 saved_image_url을 넣어줌
    urllib.request.urlretrieve(saved_image_url, 'img')

    image = Image.open('img').convert('RGB')
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    # 모델을 돌리는 곳 이게 좀 오래걸림
    prediction = third_model.predict(data)

    # 가장 확률이 높은 인덱스를 찾아주는 것
    index = np.argmax(prediction)

    # 가장 확률이 높은 색상을 (index)를 통해 class_name에 넣어주는 것
    class_name = third_class_names[index]
    confidence_score = round(prediction[0][index], 2)

    print(f'빨간색 : {round(prediction[0][0] * 100, 2)}')
    print(f'초록색 : {round(prediction[0][1] * 100, 2)}')
    print(f'황색 : {round(prediction[0][2] * 100, 2)}')
    print(f'청색 : {round(prediction[0][3] * 100, 2)}')

    print("Class : ", class_name[2:], end='')
    print("Confidence Score : ", confidence_score)
    print()

    red_perc, green_perc, yellow_perc, blue_perc = \
    str(round(prediction[0][0] * 100, 2)), str(round(prediction[0][1] * 100, 2)),\
        str(round(prediction[0][2] * 100, 2)), str(round(prediction[0][3] * 100, 2))

    if str(class_name[2:]).strip() == 'blue':
        color = '청색'
    elif str(class_name[2:]).strip() == 'red':
        color = '빨간색'
    elif str(class_name[2:]).strip() == 'green':
        color = "초록색"
    else:
        color = "황색"

    msg = color
    print(msg)

# Basic Card Format
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": "판별 색깔 : " + msg,
                        "description": "빨강색 : " + red_perc + '%\n' + "초록색 : " + green_perc + '%\n' + "청색 : " + blue_perc + '%\n' + "황색 : " + yellow_perc + '%\n',
                        "thumbnail": {
                            "imageUrl": saved_image_url
                        },
                        "buttons": [
                            {
                                "action":  "webLink",
                                "label": "전송한 사진 다시 보기",
                                "webLinkUrl": saved_image_url
                            }
                        ]
                    }
                }
            ]
        }
    }
    print(res)
    return flask.jsonify(res)


if __name__ == "__main__":
    load_first_model()
    load_third_model()
    app.run(host='0.0.0.0', debug=True)
