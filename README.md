# flask_blog

### 해당 페이지의 db 모델은 아래의 이미지 이다.(수정 2019/08/10)

<img width="624" alt="flasky" src="https://user-images.githubusercontent.com/48170295/62810346-9b534880-bb38-11e9-9163-88a5d29e7ddb.PNG">



### 이미지에 존재하는 테이블의 타입은 다음과 같이 설명한다.(수정 2019/07/17)

<table>
  <tr>
    <td><b>table_name : users</b></td>
  </tr>
  <tr>
    <td><b>column_name</b></td>
    <td><b>type</b></td>
  </tr>
  <tr>
   <td>id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>email</td>
   <td>varchar(64)</td>
  </tr>
  <tr>
   <td>username</td>
   <td>varchar(64)</td>
  </tr>
  <tr>
   <td>password_hash</td>
   <td>varchar(225)</td>
  </tr>
  <tr>
   <td>location</td>
   <td>text</td>
  </tr>
  <tr>
   <td>about_me</td>
   <td>text</td>
  </tr>
  <tr>
   <td>member_since</td>
   <td>datetime</td>
  </tr>
  <tr>
   <td>profile_filename</td>
   <td>varchar(200)</td>
  </tr>
  <tr>
   <td>post_count</td>
   <td>int</td>
  </tr>
  <tr>
   <td>follow_count</td>
   <td>int</td>
  </tr>
  <tr>
   <td>following_count</td>
   <td>int</td>
  </tr>
</table>

<table>
  <tr>
    <td><b>table_name : posts & deletepost</b></td>
  </tr>
  <tr>
    <td><b>column_name</b></td>
    <td><b>type</b></td>
  </tr>
  <tr>
   <td>id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>author_id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>name</td>
   <td>varchar(200)</td>
  </tr>
  <tr>
   <td>timestamp</td>
   <td>datetime</td>
  </tr>
  <tr>
   <td>comment_count</td>
   <td>int</td>
  </tr>
</table>

<table>
  <tr>
    <td><b>table_name : comments & deletecomments</b></td>
  </tr>
  <tr>
    <td><b>column_name</b></td>
    <td><b>type</b></td>
  </tr>
  <tr>
   <td>id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>author_id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>post_id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>body</td>
   <td>text</td>
  </tr>
  <tr>
   <td>timestamp</td>
   <td>datetime</td>
  </tr>
  <tr>
   <td>groupnum</td>
   <td>int</td>
  </tr>
  <tr>
   <td>parent</td>
   <td>int</td>
  </tr>
</table>

<table>
  <tr>
    <td><b>table_name : follows</b></td>
  </tr>
  <tr>
    <td><b>column_name</b></td>
    <td><b>type</b></td>
  </tr>
  <tr>
   <td>follower_id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>followed_id</td>
   <td>int</td>
  </tr>
  <tr>
   <td>timestamp</td>
   <td>datetime</td>
  </tr
</table>



### Table을 Flask Shell로 생성하기
>> flask_app = flasky.py
>> flask shell

```
>>> db.create_all()
```
