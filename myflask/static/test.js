var msg = new Vue({
    el: '#msg',
    data: {
        message: 'How many do you want buy?',
        count: 0
    },
    methods:{
      add:function(){
        msg.count+=1
        if(msg.count>5)
        {
            document.getElementById("msg").innerHTML="<h1>Gone Bro!!</h1>";
            document.getElementById("msg").style.backgroundColor = "red";
        }
    },
    sub:function(){
      msg.count-=1
      if(msg.count<0)
      {
          document.getElementById("msg").innerHTML="<h1>Gone Bro!!</h1>";
          document.getElementById("msg").style.backgroundColor = "red";
      }
    }
    },
    delimiters: ['[[', ']]']
});
