drop table if exists comments;
drop table if exists delcomments;
drop table if exists deletepost;
drop table if exists posts;
drop table if exists follows;
drop table if exists users; -- 왜레키 제약으로 users 테이블은 맨 마지막으로 삭제를 해야한다.

create table users( -- 사용자 정보를 저장하는 테이블
  id int auto_increment,
  email varchar(64),
  username varchar(64),
  password_hash varchar(225),
  location text,
  about_me text,
  member_since datetime default now(),
  profile_filename varchar(200),
  post_count int default 0,
  follow_count int default 0,
  following_count int default 0,
  primary key(id)
);

create table posts( -- 게시글의 정보를 저장하는 테이블
   id int auto_increment,
   author_id int,
   name varchar(200),
   timestamp datetime default now(),
   comment_count int default 0,
   primary key(id),
   foreign key(author_id)
   references users(id) on update cascade on delete cascade
);

create table comments( -- 댓글의 정보를 저장하는 테이블
  id int auto_increment,
  author_id int,
  post_id int,
  body text,
  timestamp datetime default now(),
  groupnum int default 0,
  parent int default 0,
  primary key(id),
  foreign key(author_id)
  references users(id) on update cascade on delete set null,
  foreign key(post_id)
  references posts(id) on update cascade on delete cascade
);

create table follows( -- 팔로워 & 팔로잉에 대한 정보를 저장한 테이블
  follower_id int,
  followed_id int,
  timestamp datetime default now(),
  foreign key(follower_id)
  references users(id) on update cascade on delete cascade,
  foreign key(followed_id)
  references users(id) on update cascade on delete cascade
);

create table deletecomments like comments; -- 댓글 삭제시 저장하는 테이블

create table deletepost like posts; -- 게시글 삭제시 저장하는 테이블