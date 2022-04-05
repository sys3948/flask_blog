$(function(){
 // 글자 굵게하기, 이탤릭체 표기, 양쪽 좌우 중앙 정렬, 밑줄 금지줄 긋기, 문단번호 글머리꼴 달기 버튼 이벤트
 $('div.editor-controls button').on('click', function(){
  var value = this.value;
  document.execCommand(value);
 });
 
 // 글자 크기 조절 이벤트
 $('#font-size').on('change', function(){
  var SizeValue = this.value;
  document.execCommand('fontSize', false, SizeValue);
 });
 
 // 글자 스타일 변형 이벤트
 $('#font-family').on('change', function(){
  var FontFamily = this.value;
  document.execCommand('fontName', false, String(FontFamily));
 });
 
 // 글자 색, 글자 배경색 변경 이벤트
 $('div.editor-controls input').on('change', function(){
  var colorValue = this.value;
  var kind = this.title;
  if(kind == 'font-color'){
   console.log('color value: ' + colorValue);
   document.execCommand('foreColor', false, String(colorValue));
  }else{
   console.log('color value: ' + colorValue);
   document.execCommand('backColor', false, String(colorValue));
  }
 });
 
 // 에디터에 글을 입력하면 textarea에 그 html 문서 값을 value에 넣는 이벤트 함수
 $('#editor').on('keyup', function(){
  var bodyHtml = this.innerHTML;
  console.log("지금 입력한 값: " + bodyHtml);
  $('#flask-pagedown-body').val(bodyHtml);
  console.log(document.getElementById('flask-pagedown-body').value);
 });
})