# 팔로우 & 팔로잉 페이지에서 해당 유저의 팔로워와 팔로잉의 유저 목록을 출력하기 위한 쿼리의 기능들이 지정된 함수들이 있는 모듈

from .. import db


# 팔로워들의 목록을 출력하기 위한 쿼리를 지정한 함수
def follow_query(username, id, rnum):
    with db.cursor() as cur:
        # 팔로워들의 수를 가져오는 검색 쿼리
        cur.execute('select follow_count from users where username = %s', (username))
        user_count = cur.fetchone()

        # 팔로워들의 목록을 가져오는 검색쿼리
        cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollower_id\
                     from ( \
                       select f1.follower_id as userFollower_id, f1.timestamp, f2.followed_id as loginUserFollower_id\
                       from ( \
                         select followed_id, follower_id, timestamp \
                         from follows \
                         where followed_id = ( \
                           select id \
                           from users \
                           where username = %s \
                         ) \
                         and \
                         follower_id != ( \
                           select id \
                           from users \
                           where username = %s \
                         ) \
                       ) as f1 \
                       left outer join ( \
                         select followed_id, follower_id \
                         from follows \
                         where follower_id= %s and followed_id != %s\
                       ) as f2 \
                       on f1.follower_id = f2.followed_id \
                     ) as f \
                     inner join ( \
                       select id, username, profile_filename\
                       from users \
                     ) as u \
                     on f.userFollower_id = u.id \
                     order by f.timestamp desc \
                     limit %s, 10', (username, username, id, id, rnum))

        follow_datas = cur.fetchall()

    return follow_datas, user_count[0]


# 검색기능으로 팔로워들의 목록을 출력하기 위한 쿼리를 지정한 함수
def follow_search_query(username, id, search, limit=False, rnum=None):
    if limit:
        # 검색한 결과로 나오는 팔로워들의 목록을 limit절을 이용한 검색쿼리(GET)
        with db.cursor() as cur:
            cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollower_id\
                         from ( \
                           select f1.follower_id as userFollower_id, f1.timestamp, f2.followed_id as loginUserFollower_id \
                           from ( \
                             select followed_id, follower_id, timestamp \
                             from follows \
                             where followed_id = ( \
                               select id \
                               from users \
                               where username = %s \
                             ) \
                             and \
                             follower_id != ( \
                               select id \
                               from users \
                               where username != %s \
                             ) \
                           ) as f1 \
                           left outer join( \
                             select followed_id, follower_id \
                             from follows \
                             where follower_id = %s and followed_id != %s \
                           ) as f2 \
                           on f1.follower_id = f2.followed_id \
                         ) as f \
                         inner join ( \
                           select id, username, profile_filename \
                           from users \
                         ) as u \
                         on f.userFollower_id = u.id \
                         where u.username like %s \
                         order by f.timestamp desc \
                         limit 10', (username, username, id, id, "%"+search+"%"))

            follow_datas = cur.fetchall()
    else:
        # 검색한 결과로 나오는 팔로워들의 목록을 limit을 이용하지 않는 검색 쿼리(POST)
        with db.cursor() as cur:
            cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollower_id\
                         from ( \
                           select f1.follower_id as userFollower_id, f1.timestamp, f2.followed_id as loginUserFollower_id\
                           from ( \
                             select followed_id, follower_id, timestamp \
                             from follows \
                             where followed_id = ( \
                               select id \
                               from users \
                               where username = %s \
                             ) \
                             and \
                             follower_id != ( \
                               select id \
                               from users \
                               where username = %s \
                             ) \
                           ) as f1 \
                           left outer join ( \
                             select followed_id, follower_id \
                             from follows \
                             where follower_id= %s and followed_id != %s\
                           ) as f2 \
                           on f1.follower_id = f2.followed_id \
                         ) as f \
                         inner join ( \
                           select id, username, profile_filename\
                           from users \
                         ) as u \
                         on f.userFollower_id = u.id \
                         where u.username like %s\
                         order by f.timestamp desc', (username, username, id, id, "%"+search+"%"))

            follow_datas = cur.fetchall()


    return follow_datas


# 팔로잉의 목록을 출력하기 위한 쿼리를 지정한 함수 
def following_query(username, id, rnum):
    with db.cursor() as cur:
        cur.execute('select following_count from users where username = %s', (username))
        user_count = cur.fetchone()

        cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollowed_id \
                     from ( \
                       select f1.followed_id as userFollowed_id, f1.timestamp as timestamp, f2.followed_id as loginUserFollowed_id \
                       from ( \
                         select followed_id, timestamp \
                         from follows \
                         where follower_id = ( \
                           select id \
                           from users \
                           where username = %s \
                         ) \
                         and \
                         followed_id != ( \
                           select id \
                           from users \
                           where username = %s \
                         ) \
                       ) as f1 \
                       left outer join ( \
                         select followed_id \
                         from follows \
                         where follower_id = %s and followed_id != %s\
                       ) as f2 \
                       on f1.followed_id = f2.followed_id \
                     ) as f \
                     inner join (\
                       select id, username, profile_filename \
                       from users \
                     ) as u \
                     on f.userFollowed_id = u.id \
                     order by f.timestamp desc \
                     limit %s, 10', (username, username, id, id, rnum))

        follow_datas = cur.fetchall()

    return follow_datas, user_count[0]


# 검색기능으로 팔로잉들을 출력하기 위한 쿼리를 지정한 함수 
def following_search_query(username, id, search, limit=False, rnum=None):
    if limit:
        with db.cursor() as cur:
            # 검색한 결과로 나오는 팔로잉들의 목록을 limit를 이용한 검색 쿼리(GET)
            cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollowed_id \
                         from ( \
                           select f1.followed_id as userFollowed_id, f1.timestamp as timestamp, f2.followed_id as loginUserFollowed_id \
                           from ( \
                             select followed_id, timestamp \
                             from follows \
                             where follower_id = ( \
                               select id \
                               from users \
                               where username = %s \
                             ) \
                             and \
                             followed_id != ( \
                               select id \
                               from users \
                               where username = %s \
                             ) \
                           ) as f1 \
                           left outer join ( \
                             select followed_id \
                             from follows \
                             where follower_id = %s and followed_id != %s\
                           ) as f2 \
                           on f1.followed_id = f2.followed_id \
                         ) as f \
                         inner join (\
                           select id, username, profile_filename \
                           from users \
                         ) as u \
                         on f.userFollowed_id = u.id \
                         where u.username like %s \
                         limit %s, 10', (username, username, id, id, "%"+search+"%", rnum))

            follow_datas = cur.fetchall()

    else:
        with db.cursor() as cur:
            # 검색한 결과로 나오는 팔로잉들의 목록을 limit를 이용하지 않는 검색 쿼리(POST)
            cur.execute('select u.username, u.profile_filename, f.timestamp, f.loginUserFollowed_id \
                          from ( \
                            select f1.followed_id as userFollowed_id, f1.timestamp as timestamp, f2.followed_id as loginUserFollowed_id \
                            from ( \
                              select followed_id, timestamp \
                              from follows \
                              where follower_id = ( \
                                select id \
                                from users \
                                where username = %s \
                              ) \
                              and \
                              followed_id != ( \
                                select id \
                                from users \
                                where username = %s \
                              ) \
                            ) as f1 \
                            left outer join ( \
                              select followed_id \
                              from follows \
                              where follower_id = %s and followed_id != %s\
                            ) as f2 \
                            on f1.followed_id = f2.followed_id \
                          ) as f \
                          inner join (\
                            select id, username, profile_filename \
                            from users \
                          ) as u \
                          on f.userFollowed_id = u.id \
                          where u.username like %s \
                          order by f.timestamp desc', (username, username, id, id, "%"+search+"%"))

            follow_datas = cur.fetchall()

    return follow_datas

