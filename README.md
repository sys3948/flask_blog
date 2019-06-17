# flask_blog

해당 페이지의 db 모델은 아래의 이미지 이다.

<img width="578" alt="db_modle_in_flasky" src="https://user-images.githubusercontent.com/48170295/59585495-94512080-911b-11e9-9172-97f2683fd67c.PNG">

이미지에 존재하는 테이블의 타입은 다음과 같이 설명한다.


|table_name|users|
|:--------:|:--------:|
|column_name|type|
|:--------:|:--------:|
|id|int|
|email|varchar(64)|
|username|varchar(64)|
|password_hash|varchar(225)|
|location|text|
|about_me|text|
|member_since|datetime|
|profile_filename|varchar(200)|
