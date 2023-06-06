# import tensorflow
import flask
import urllib.request
from PIL import Image, ImageOps
import numpy as np
import ast
import mysql.connector
import random

# Use app with Flask Server
app = flask.Flask(__name__)


# Predefine first_class_names, first_model
'''
0 red
1 green
'''
first_class_names = None
first_model = None

# Predefine second_class_names, second_model
'''
0 yellow
1 blue
'''
second_class_names = None
second_model = None

# Predefine third_class_names, third_model
'''
0 red
1 green
2 yellow
3 blue
'''
third_class_names = None
third_model = None


quiz_cnt = 0
quiz_O = 0
quiz_X = 0


config = {
    'user': 'cray7',
    'password': 'dgu1234!',
    'host': '43.200.153.107',
    'port': '57223',
    'database': 'cray7db'
}
conn = mysql.connector.connect(**config)



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
    global type_dic
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

    # 사용자가 어떤 색각이상 타입인지 확인
    # 커서 시작
    cursor = conn.cursor()
    query = "SELECT * FROM user_type"
    cursor.execute(query)
    result = cursor.fetchall()

    type_answer = ''
    for r in result:
        if r[0] == user_id:
            type_answer = r[1]
            break

    # 커서 시작
    cursor = conn.cursor()
    insert_query = "INSERT INTO quiz (user_id, type1, image, answer) VALUES (%s, %s, %s, %s)"
    data = (user_id, type_answer, saved_image_url, color)
    cursor.execute(insert_query, data)
    conn.commit()

    # 커서와 연결 종료
    cursor.close()

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





# run second model
def load_second_model():
    global second_class_names, second_model

    second_class_names = open('second_labels.txt', 'r').readlines()
    second_model = tensorflow.keras.models.load_model('keras_second_model.h5', compile=False)
    
    
# second model api
@app.route("/api/second/predict", methods=["POST"])
def api_second_predict():
    global second_class_names, second_model

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
    prediction = second_model.predict(data)

    # 가장 확률이 높은 인덱스를 찾아주는 것
    index = np.argmax(prediction)

    # 가장 확률이 높은 색상을 (index)를 통해 class_name에 넣어주는 것
    class_name = second_class_names[index]
    confidence_score = round(prediction[0][index], 2)

    print(f'황색 : {round(prediction[0][0] * 100, 2)}')
    print(f'청색 : {round(prediction[0][1] * 100, 2)}')

    print("Class : ", class_name[2:], end='')
    print("Confidence Score : ", confidence_score)
    print()

    yellow_perc, blue_perc = \
    str(round(prediction[0][0] * 100, 2)), str(round(prediction[0][1] * 100, 2))

    if str(class_name[2:]).strip() == 'yellow':
        color = '황색'
    elif str(class_name[2:]).strip() == 'blue':
        color = "청색"

    # 커서 시작
    cursor = conn.cursor()

    insert_query = "INSERT INTO user1 (user_id, image, answer) VALUES (%s, %s, %s)"
    data = (user_id, saved_image_url, color)
    cursor.execute(insert_query, data)
    conn.commit()

    # 커서와 연결 종료
    cursor.close()

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
                        "description": "황색 : " + yellow_perc + '%\n' + "청색 : " + blue_perc + '%\n',
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

    # 커서 시작
    cursor = conn.cursor()

    insert_query = "INSERT INTO user1 (user_id, image, answer) VALUES (%s, %s, %s)"
    data = (user_id, saved_image_url, color)
    cursor.execute(insert_query, data)
    conn.commit()

    # 커서와 연결 종료
    cursor.close()

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
                        "description": "빨강색 : " + red_perc + '%\n' + "초록색 : " + green_perc + '%\n' + "황색 : " + yellow_perc + '%\n' + "청색 : " + blue_perc + '%\n',
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


# Quiz
@app.route("/quiz", methods=["POST"])
def quiz():
    global quiz_cnt, quiz_O, quiz_X
    # UserRequest 중 발화를 req에 parsing.
    req = flask.request.get_json()
    user_id = req['userRequest']['user']['id']
    print(f'사용자 아이디 : {user_id}')

    speak = req['userRequest']['utterance']
    print(f'사용자의 발화가 들어왔을 때를 나타냄 : {speak}')

    if '정답' in speak:
        quiz_cnt += 1
        quiz_O += 1

    elif '오답' in speak:
        quiz_cnt += 1
        quiz_X += 1

    # quiz문제를 다 푼 경우
    if quiz_cnt == 3:
        quiz_cnt = 0
        correct = quiz_O
        quiz_O = 0
        wrong = quiz_X
        quiz_X = 0

        # Basic Card Format
        res = {
          "version": "2.0",
          "template": {
            "outputs": [
              {
                "basicCard": {
                  "title": f"사용자님은 3문제 중 {correct}개 맞추셨습니다",
                  "description": f"사용자님의 틀린 {wrong}개의 사진의 가중치가 올라가서 다음번에 다시 출제됩니다.",
                  "thumbnail": {
                    "imageUrl": 'https://blog.amazingtalker.com/wp-content/uploads/2022/09/Congrats-1024x683.jpg'
                  }
                }
              }
            ]
          }
        }

        # 커서 시작
        cursor = conn.cursor()
        insert_query = "INSERT INTO quiz_history (user_id, correct, wrong) VALUES (%s, %s, %s)"
        data = (user_id, correct, wrong)
        cursor.execute(insert_query, data)
        conn.commit()

        # 커서와 연결 종료
        cursor.close()

        return flask.jsonify(res)






    # 사용자가 어떤 색각이상 유형인지 파악
    # 커서 시작
    cursor = conn.cursor()
    query = "SELECT * FROM user_type"
    cursor.execute(query)

    result = cursor.fetchall()

    color_type = ''
    for r in result:
        if r[0] == user_id:
            color_type = r[1]

    # 사용자의 색각이상 유형이 정의되지않았다면
    if color_type == '':
        print("사용자의 색각이상이 정의되지 않은 경우")
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"사용자의 색각 이상 유형이 정의되지 않았습니다. 색각이상 TEST에서 색각이상유형을 등록해주세요!"
                        }
                    }
                ]
            }
        }
        # 커서와 연결 종료
        cursor.close()
        return res

    print(f'사용자의 색각이상은 {color_type}입니다')


    if color_type == '적록색맹':
        final_ans = ''
        query1 = "SELECT * FROM red"
        cursor.execute(query1)

        result1 = cursor.fetchall()

        query2 = "SELECT * FROM green"
        cursor.execute(query2)

        result2 = cursor.fetchall()

        # 빨간색 고를지 초록색 고를지
        color_num = random.randint(1, 3)

        # 빨간색으로 퀴즈 내기
        if color_num == 1:
            img_link = ''
            cnt = 0
            for r in result1:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result1[img_idx][1]
            final_ans = '빨간색'

        # 초록색으로 퀴즈 내기
        else:
            img_link = ''
            cnt = 0
            for r in result2:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result2[img_idx][1]
            final_ans = '초록색'

        # 커서와 연결 종료
        cursor.close()

        if final_ans == '빨간색':
            # Basic Card Format (빨간색인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "basicCard": {
                      "title": "위 사진의 색깔을 맞춰보세요!",
                      "description": "빨강색 / 초록색",
                      "thumbnail": {
                        "imageUrl": img_link
                      },
                      "buttons": [
                        {
                          "action": "message",
                          "label": "빨간색",
                          "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                        },
                        {
                          "action": "message",
                          "label": "초록색",
                          "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                        }
                      ]
                    }
                  }
                ]
              }
            }
        else:
            # Basic Card Format (초록색인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "basicCard": {
                      "title": "위 사진의 색깔을 맞춰보세요!",
                      "description": "빨강색 / 초록색",
                      "thumbnail": {
                        "imageUrl": img_link
                      },
                      "buttons": [
                        {
                          "action": "message",
                          "label": "빨간색",
                          "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                        },
                        {
                          "action": "message",
                          "label": "초록색",
                          "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                        }
                      ]
                    }
                  }
                ]
              }
            }
        return flask.jsonify(res)


    elif color_type == '황청색맹':
        final_ans = ''
        query1 = "SELECT * FROM brown"
        cursor.execute(query1)

        result1 = cursor.fetchall()

        query2 = "SELECT * FROM blue"
        cursor.execute(query2)

        result2 = cursor.fetchall()

        # 황색 고를지, 청색 고를지
        color_num = random.randint(1, 3)

        # 황색으로 퀴즈 내기
        if color_num == 1:
            img_link = ''
            cnt = 0
            for r in result1:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result1[img_idx][1]
            final_ans = '황색'

        # 청색으로 퀴즈 내기
        else:
            img_link = ''
            cnt = 0
            for r in result2:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result2[img_idx][1]
            final_ans = '청색'

        # 커서와 연결 종료
        cursor.close()

        if final_ans == '황색':
            # Basic Card Format (황색인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "basicCard": {
                      "title": "위 사진의 색깔을 맞춰보세요!",
                      "description": "황색 / 청색",
                      "thumbnail": {
                        "imageUrl": img_link
                      },
                      "buttons": [
                        {
                          "action": "message",
                          "label": "황색",
                          "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                        },
                        {
                          "action": "message",
                          "label": "청색",
                          "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                        }
                      ]
                    }
                  }
                ]
              }
            }
        else:
            # Basic Card Format (청색인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "basicCard": {
                      "title": "위 사진의 색깔을 맞춰보세요!",
                      "description": "황색 / 청색",
                      "thumbnail": {
                        "imageUrl": img_link
                      },
                      "buttons": [
                        {
                          "action": "message",
                          "label": "황색",
                          "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                        },
                        {
                          "action": "message",
                          "label": "청색",
                          "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                        }
                      ]
                    }
                  }
                ]
              }
            }
        return flask.jsonify(res)


    # 전색맹인 경우
    else:
        final_ans = ''
        query1 = "SELECT * FROM red"
        cursor.execute(query1)

        result1 = cursor.fetchall()

        query2 = "SELECT * FROM green"
        cursor.execute(query2)

        result2 = cursor.fetchall()

        query3 = "SELECT * FROM brown"
        cursor.execute(query3)
        result3 = cursor.fetchall()

        query4 = "SELECT * FROM blue"
        cursor.execute(query4)
        result4 = cursor.fetchall()

        
        # 빨, 초, 황, 청 뭘 고를지 고민
        color_num = random.randint(1, 5)

        # 빨간색으로 퀴즈 내기
        if color_num == 1:
            img_link = ''
            cnt = 0
            for r in result1:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result1[img_idx][1]
            final_ans = '빨간색'

        # 초록색으로 퀴즈 내기
        elif color_num == 2:
            img_link = ''
            cnt = 0
            for r in result1:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result1[img_idx][1]
            final_ans = '초록색'

        # 황색으로 퀴즈 내기
        if color_num == 3:
            img_link = ''
            cnt = 0
            for r in result1:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result1[img_idx][1]
            final_ans = '황색'

        # 청색으로 퀴즈 내기
        else:
            img_link = ''
            cnt = 0
            for r in result2:
                cnt += 1
            img_idx = random.randint(1, cnt)
            img_link = result2[img_idx][1]
            final_ans = '청색'

        # 커서와 연결 종료
        cursor.close()

        # 답이 빨간색인 경우
        if final_ans == '빨간색':
            # Basic Card Format (빨간인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "carousel": {
                      "type": "basicCard",
                      "items": [
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "빨강색 / 초록색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "빨간색",
                              "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "초록색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        },
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "황색 / 청색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "황색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "청색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        }
                      ]
                    }
                  }
                ]
              }
            }

        # 답이 초록색인 경우
        if final_ans == '초록색':
            # Basic Card Format (빨간인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "carousel": {
                      "type": "basicCard",
                      "items": [
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "빨강색 / 초록색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "빨간색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "초록색",
                              "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                            }
                          ]
                        },
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "황색 / 청색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "황색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "청색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        }
                      ]
                    }
                  }
                ]
              }
            }

        # 답이 황색인 경우
        if final_ans == '황색':
            # Basic Card Format (빨간인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "carousel": {
                      "type": "basicCard",
                      "items": [
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "빨강색 / 초록색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "빨간색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "초록색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        },
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "황색 / 청색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "황색",
                              "messageText": f"답은 {final_ans}입니다. 정답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "청색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        }
                      ]
                    }
                  }
                ]
              }
            }

        # 답이 청색인 경우
        else:
            # Basic Card Format (빨간인 경우)
            res = {
              "version": "2.0",
              "template": {
                "outputs": [
                  {
                    "carousel": {
                      "type": "basicCard",
                      "items": [
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "빨강색 / 초록색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "빨간색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "초록색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            }
                          ]
                        },
                        {
                          "title": "위 사진의 색깔을 맞춰보세요!",
                          "description": "황색 / 청색",
                          "thumbnail": {
                            "imageUrl": img_link
                          },
                          "buttons": [
                            {
                              "action": "message",
                              "label": "황색",
                              "messageText": f"답은 {final_ans}입니다. 오답입니다!"
                            },
                            {
                              "action": "message",
                              "label": "청색",
                              "messageText": f"답은 {final_ans}입니다. 청색입니다!"
                            }
                          ]
                        }
                      ]
                    }
                  }
                ]
              }
            }
        return flask.jsonify(res)


# 사용자가 어떤 색각이상자인지 저장
@app.route("/problem", methods=["POST"])
def problem():
    # UserRequest 중 발화를 req에 parsing.
    req = flask.request.get_json()
    user_id = req['userRequest']['user']['id']
    print(f'사용자의 아이디 {user_id}')

    contents = req['userRequest']['utterance']
    print(f'사용자의 발화가 들어왔을 때를 나타냄 : {contents}')

    if contents == '아니요, 잘 돼요':
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"사용자님은 정상입니다!"
                        }
                    }
                ]
            }
        }
        return res

    type_ans = ''
    if '(T)' == contents[-3:]:
        type_ans = '황청색맹'
    elif '(A)' == contents[-3:]:
        type_ans = '전색맹'
    elif '(P)' or '(D)' == contents[-3:]:
        type_ans = '적록색맹'
    print(f'판별된 색맹 : {type_ans}')

    # 사용자의 색각이상 타입이 정해졌는지 확인하기
    # 커서 시작
    cursor = conn.cursor()
    query = "SELECT * FROM user_type"
    cursor.execute(query)

    result = cursor.fetchall()

    is_exist = False

    for r in result:
        if r[0] == user_id:
            is_exist = True
            break

    if not is_exist:
        insert_query = "INSERT INTO user_type (user_id, type) VALUES (%s, %s)"
        data = (user_id, type_ans)
        cursor.execute(insert_query, data)
        conn.commit()

    else:
        insert_query = "UPDATE user_type SET type=%s where user_id = %s"
        data = (type_ans, user_id)
        cursor.execute(insert_query, data)
        conn.commit()

    # 커서와 연결 종료
    cursor.close()

    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"사용자의 색각이상 유형을 등록했습니다." + "\n" + "색각 이상 Quiz를 이용해보세요!"
                    }
                }
            ]
        }
    }
    return res


if __name__ == "__main__":
    # load_first_model()
    # load_second_model()
    # load_third_model()
    app.run(host='0.0.0.0', debug=True)
