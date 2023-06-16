1) Android_Color_Dection_App 폴더
-> 색을 판별하는 AI 모델을 활용한 안드로이드(JAVA) 앱

2) chromedriver_win32 폴더
-> 이미지를 Crawling하는데 필요한 ChromeDriver32


3) Color_Detection_Models 폴더
 3_1) keras_first_model.h5 : 빨간색, 초록색을 판별해주는 keras 적록색 모델
 3_2) keras_second_model.h5 : 황색, 청색을 판별해주는 keras 황청색 모델
 3_3) keras_third_model.h5 : 빨간색, 초록색, 황색, 청색을 판별해주는 keras 전색 모델

4) Color_Detection_Names 폴더
 3_1) first_labels.txt : keras_first_model.h5의 각 인덱스별 색깔 이름
 3_2) second_labels.txt : keras_second_model.h5의 각 인덱스별 색깔 이름
 3_3) third_labels.txt : keras_third_model.h5의 각 인덱스별 색깔 이름

5) static 폴더
-> Web에서 이미지를 사용하기 위한 static 폴더
-> static 폴더 내에 이미지 저장

6) templates 폴더
-> Flask 서버에서 render_template() 함수를 사용하기 위해 모든 html 파일을 templates 폴더에 담아서 저장
-> 웹에서의 모든 기능들을 수행하는 html파일이 존재한다.

7) venv 폴더
-> 필요한 모듈을 따로 설치하여 배포하기 쉽게 하기 위해 파이썬 가상환경인 venv 내에서 모든 코드를 구현
-
8) .gitignore 파일
-> github에 push할 때 push하지 않을 코드들을 지정하는 파일

9) app.py 파일
-> 파이썬 Flask를 기반으로 구현한 모든 백엔드 코드
-> 웹과 카카오톡 챗봇의 서버 역할을 하며 mysql 데이터베이스와 연결했다.

10) Imgs_Crawling.py
-> Google의 대표 브라우저인 Chrome을 웹 브라우저로 ChromeDriver와 파이썬 Selenium을 이용해 빨간색, 초록색, 황색, 청색의 이미지를 수집하는 코드이다.

11) Imgs_Quiz_Insert.py
-> 사용자가 푸는 퀴즈 데이터베이스에 호스팅된 이미지를 Insert하는 코드이다.