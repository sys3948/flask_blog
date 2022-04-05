var ck_num; // 답 댓글 작성 폼을 활성화 또는 비활성화 하기 위한 변수.
var edit_ck_num; // 댓글 수정 폼을 활성화 또는 비활성화 하기 위한 변수.
var beforEditId; // 댓글 수정시 수정취소로 이전 댓글의 id value를 저장하기 위한 변수
var divText; // 댓글 수정시 수정취소로 이전 댓글 텍스트를 저장하기 위한 변수


// 답 댓글 작성 함수
function write_recomment(num, groupnum){
     
 if(ck_num == null){
  // 처음 답글 작성하기를 클릭할 경우 답글 작성 폼 활성화
  ck_num = num;
  var comment_id = 'li#comment_' + num;
  var select_value = comment_id + ' ' + 'div.comment-body';

  var form_elements = "<div id='recomment_" +num + "'" + ">" +
   "<form action method='post' class='form' role='form'>" +
    "<input type='hidden' name='comment-classfiy' value='recomment'>" +
    "<div class='form-group required'>" +
     "<label class='font-weight-bolder' for='body'>Enter Your Re Comment</label>" +
      "<div class='flask-pagedown'>" +
       "<textarea class='form-control flask-pagedown-input' id='flask-pagedown-body' name='body' required>" +
       "</textarea>" +
       "<input type='hidden' name='parent_id' value='" + num + "'>" +
       "<input type='hidden' name='group_id' value='" + groupnum + "'>" +
      "</div>" +
     "</div>" +
     "<input class='btn btn-outline-secondary text-secondary font-weight-bolder' id='submit' name='submit' type='submit' value='Submit'>" +
    "</form>" +
   "</div>";

  document.querySelector(select_value).innerHTML += form_elements;
 }else{
  if(ck_num == num){
   // 동일한 답글 쓰기를 클릭할 경우(같은 곳에 짝수번 클릭시) 답글 작성 폼 비활성화 
   var parent_element = 'li#comment_' + ck_num + ' ' + 'div.comment-body';
   var selector = 'recomment_' + ck_num;
   var remove_item = document.getElementById(selector);
   document.querySelector(parent_element).removeChild(remove_item);
   ck_num = null;
  }else{
   // 답글 작성 폼이 활성화 될 경우 다른 댓글의 답글을 작성하기 위해 새로운 답글 작성 버튼 클릭시
   // 기존 활성화된 답글 폼을 비활성화 하고 새로 클릭한 답글 작성한 위치에 답글 작성 폼 활성화
   var parent_element = 'li#comment_' + ck_num + ' ' + 'div.comment-body';
   var selector = 'recomment_' + ck_num;
   var remove_item = document.getElementById(selector);
   document.querySelector(parent_element).removeChild(remove_item);
   ck_num = num;
   
   var comment_id = 'li#comment_' + num;
   var select_value = comment_id + ' ' + 'div.comment-body';

   var form_elements = "<div id='recomment_" +num + "'" + ">" +
    "<form action method='post' class='form' role='form'>" +
     "<input type='hidden' name='comment-classfiy' value='recomment'>" +
     "<div class='form-group required'>" +
      "<label class='font-weight-bolder' for='body'>Enter Your Re Comment</label>" +
      "<div class='flask-pagedown'>" +
       "<textarea class='form-control flask-pagedown-input' id='flask-pagedown-body' name='body' required>" +
       "</textarea>" +
       "<input type='hidden' name='parent_id' value='" + num + "'>" +
       "<input type='hidden' name='group_id' value='" + groupnum + "'>" +
      "</div>" +
     "</div>" +
     "<input class='btn btn-outline-secondary text-secondary font-weight-bolder' id='submit' name='submit' type='submit' value='Submit'>" +
    "</form>" +
   "</div>";
       
   document.querySelector(select_value).innerHTML += form_elements;
  }
 }
}


// 댓글 수정 함수
function edit_comment(num){
 var editId = 'commentBody-' + num;
 var textareaText = document.getElementById(editId).innerHTML; // 수정버튼 클릭시 textarea의 value로 들어가는 변수
 
 if(edit_ck_num == null){
  // 처음 수정을 클릭할 경우 수정 폼 활성화.
  edit_ck_num = num;
  beforEditId = editId;
  divText = textareaText;
  
  var edit_form_element = '<div class="comment-form" id="editComment-"' + num + '>' +
   '<form action method="post" class="form" role="form">' +
    '<input type="hidden" name="comment-classfiy" value="eidt">' +
    '<div class="form-group required">' +
     '<label class="font-weight-bolder" for="body">Enter Your Edit Comment</label>' +
     '<textarea class="form-control" id="body" name="body" required>'+textareaText+'</textarea>' +
      "<input type='hidden' name='editComment_id' value='" + num + "'>" +
    '</div>' +
    '<input class="btn btn-outline-secondary text-secondary" id="submit" name="submit" type="submit" value="Submit">' +
   '</form>' +
  '</div>' ;
  
  document.getElementById(editId).innerHTML = edit_form_element;
 }else{
  if(edit_ck_num == num){
   // 수정을 취소했을 시 수정 폼 비활성화 후 댓글 원상복귀
   document.getElementById(editId).innerHTML = divText;
   divText = null;
   edit_ck_num = null;
  }else{
   // 다른 댓글을 수정할 시 전에 활성화 된 수정 폼 비활성화 후 전의 댓글 복구 후
   // 현재 수정하기 위한 댓글에 수정 폼 활성화
   document.getElementById(beforEditId).innerHTML = divText;
   
   var edit_form_element = '<div class="comment-form" id="editComment-"' + num + '>' +
   '<form action method="post" class="form" role="form">' +
    '<input type="hidden" name="comment-classfiy" value="eidt">' +
    '<div class="form-group required">' +
     '<label class="font-weight-bolder" for="body">Enter Your Edit Comment</label>' +
     '<textarea class="form-control" id="body" name="body" required>'+textareaText+'</textarea>' +
      "<input type='hidden' name='editComment_id' value='" + num + "'>" +
    '</div>' +
    '<input class="btn btn-outline-secondary text-secondary" id="submit" name="submit" type="submit" value="Submit">' +
   '</form>' +
  '</div>' ;
   
  edit_ck_num = num;
  beforEditId = editId;
  divText = textareaText;
  
  document.getElementById(editId).innerHTML = edit_form_element;
  }
 }
}