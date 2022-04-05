function modal(name, iconUrl){
 // img src 값 삽입하기.
 document.getElementById('icon').src = iconUrl;
 // 모달 content 삽입하기.
 document.getElementById('modalContent').innerHTML = '<p>생각이 바뀌면 '+name+'님을 팔로우 할 수 있습니다.</p>';
 // 언팔로우 url 삽입하기.
 document.getElementById('unfollowLink').href = "/unfollow/" + name;
}