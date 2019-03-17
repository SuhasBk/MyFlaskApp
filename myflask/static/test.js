var msg = new Vue({
    el: '#msg',
    data: {
        message: 'Hello Vue!'
    },
    methods:{
      click:function(){
        alert('clicked!!!')
      }
    },
    delimiters: ['[[', ']]']
});
