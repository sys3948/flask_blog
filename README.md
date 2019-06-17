# flask_blog

해당 페이지의 db 모델은 아래의 이미지 이다.

<img width="578" alt="db_modle_in_flasky" src="https://user-images.githubusercontent.com/48170295/59585495-94512080-911b-11e9-9172-97f2683fd67c.PNG">

이미지에 존재하는 테이블의 타입은 다음과 같이 설명한다.

<table>
  <tr>
    <td></td>
    <td><b>table_name : users</b></td>
  </tr>
  <tr>
    <td>column_name</td>
    <td>type</td>
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
</table>
