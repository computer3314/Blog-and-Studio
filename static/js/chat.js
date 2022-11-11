      const myVar = document.getElementById("myVar").value;
      // 得到房間的名字
      const roomName = JSON.parse(document.getElementById('room-name').textContent);

      // 根據roomName拼接websocket請求地址，建立長連接
      //  請求url地址為/ws/chat/<room_name>/
      const wss_protocol = (window.location.protocol == 'https:') ? 'wss://': 'ws://';
      const chatSocket = new WebSocket(
           wss_protocol + window.location.host + '/ws/chat/'  + roomName + '/'
           );
      // 建立websocket連結時觸發這個funciton 歡迎進來的人
      chatSocket.onopen = function(e) {
          //  document.querySelector('#chat-log').value += ('[公告]歡迎進入' + roomName + '討論群。歡迎斗內案讚!\n')
              $(".messages").append('<li class="message clearfix"> <div class="received"><p>'+'[公告]歡迎進入' + roomName + '討論群。歡迎斗內案讚!\n' +'</p><p class="date">'+ formatDate(new Date()) +'</p> </div></li>');
              scrollTo()
            }

      // 從後台接收到資料時觸發此方法
      //  接收到後台資料時解析，並把他加祿聊天紀錄chatlog
       chatSocket.onmessage = function(e) {
              const data = JSON.parse(e.data);
              if(data.type=="chat_message"){
                if(myVar=="True"){
                  $(".messages").append('<li class="message clearfix" id="'+data.id+'"> <div class="received"><input type="checkbox"  id="ch'+data.id+'" value="'+data.id+'"><p  class="message">'+ data.nickname  +':'+ data.message  +'</p><p class="date">'+ data.time +'</p> </div></li>');
                }
                else{
                  $(".messages").append('<li class="message clearfix" id="'+data.id+'"> <div class="received"><p  class="message">'+ data.nickname  +':'+ data.message  +'</p><p class="date">'+ data.time +'</p> </div></li>');
                }
                scrollTo();
              }
              else if(data.type=="delete_message"){
                var array  = data.messages.replace(/'/g, '"');
                array = JSON.parse(array);
                for (var value of array) {
                    $("#"+value+" .message").html("該留言已被管理員刪除");
                    $("#"+value+" .message").addClass("delmessage");
                    $("#ch"+value).prop('disabled', true);
                  }
              }
             
       };
      
       // websocket連結中斷觸發方法
       chatSocket.onclose = function(e) {
           console.error('Chat socket closed unexpectedly');
       };
       
       //document.querySelector('#chat-message-input').focus();
       document.querySelector('#chat-message-input').onkeyup = function(e) {
           if (e.keyCode === 13) {  // enter, return
               document.querySelector('#chat-message-submit').click();
           }
       };
       //每當典籍發送按鈕  都通過websocket的send方法向後台發送消息
       document.querySelector('#chat-message-submit').onclick = function(e) {
            // 得到姓名
          var nickname = document.getElementById('nick_name').value;
          if(nickname==""){
              var nickname = prompt('請輸入你的暱稱');
              if(nickname==null){
                  document.getElementById('nick_name').value=""
              }
              else{
             
                  document.getElementById('nick_name').value=nickname
              }
          }
          else{
              const messageInputDom = document.querySelector('#chat-message-input');
              var message = messageInputDom.value;
              message = message.toString().replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/'/g, "&#39;").replace(/"/g, "&#34;");//阻擋script攻擊字元
              //先把資料轉乘jsｏｎ　在送後端
              chatSocket.send(JSON.stringify({
                  'type':'chat_message',
                  'nickname':nickname,
                  'message': message,
              }));
              messageInputDom.value = '';
          }
       };
       function scrollTo(){
              $('.message-wrapper').animate({
                  scrollTop: $('.message-wrapper').get(0).scrollHeight
              },50)
          }
          function padTo2Digits(num) {
return num.toString().padStart(2, '0');
}

function formatDate(date) {
return (
  [
    date.getFullYear(),
    padTo2Digits(date.getMonth() + 1),
    padTo2Digits(date.getDate()),
  ].join('-') +
  ' ' +
  [
    padTo2Digits(date.getHours()),
    padTo2Digits(date.getMinutes()),
    padTo2Digits(date.getSeconds()),
  ].join(':')
);
}
