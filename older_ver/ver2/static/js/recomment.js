var ck_num;
   
function write_recomment(num, groupnum){
     
 if(ck_num == null){
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
   var parent_element = 'li#comment_' + ck_num + ' ' + 'div.comment-body';
   var selector = 'recomment_' + ck_num;
   var remove_item = document.getElementById(selector);
   document.querySelector(parent_element).removeChild(remove_item);
   ck_num = null;
  }else{
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