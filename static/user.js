function register(){
 	  	d = {}
 	  	d['username'] = document.getElementById("usernamer").value
 	  	d['password'] = document.getElementById("passwordr").value
 	  	d['name'] = document.getElementById("namer").value
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/register/'+jsondata,
 	  	function reg(data){
 	  		if (data == 'success'){
 	  			alert(data)
 	  		}
 	  		else{
 	  			alert(data)
 	  		}
 	  	}
 	  	)
 	  }
 	  
 	  function login(){
 	  	d = {}
 	  	d['username'] = document.getElementById("usernamel").value
 	  	d['password'] = document.getElementById("passwordl").value
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/login/'+jsondata,
 	  	function reg(data){
 	  		result = JSON.parse(data)
 	  		if (result['success'] == 0)
 	  			alert(result['message'])
 	  		else{
 	  			setCookie('userid', result['userid'], 1)
 	  			setCookie('username', result['username'], 1)
 	  			loginstatus()
 	  			document.getElementById('LayerLogin').style.display = 'none'
 	  			document.getElementById('passwordl').value = ''
 	  		}
 	  	}
 	  	)
 	  }

 	  function logout(){
 	  	delCookie('username')
 	  	delCookie('userid')
 	  	loginstatus()
 	  }

 	  function loginstatus(){
 	  	username = getCookie('username')
 	  	if (username != ''){
 	  		document.getElementById('username').innerHTML = username
 	  		document.getElementById('logged').style.display = ''
 	  		document.getElementById('unlogged').style.display = 'none'
 	  	}
 	  	else{
 	  		document.getElementById('logged').style.display = 'none'
 	  		document.getElementById('unlogged').style.display = ''
 	  	}
 	  }