function register(){
		if (document.getElementById('passwordr').value != document.getElementById('repasswordr').value){
 	  		alert('两次密码不相同')
 	  		return
 	  	}
 	  	d = {}
 	  	d['username'] = document.getElementById("usernamer").value
 	  	d['password'] = $.md5(document.getElementById("passwordr").value)
 	  	d['name'] = document.getElementById("namer").value
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/register/'+jsondata,
 	  	function reg(data){
 	  		if (data == 'success'){
 	  			document.getElementById('LayerRegister').style.display = 'none'
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
 	  	d['password'] = $.md5(document.getElementById("passwordl").value)
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/login/'+jsondata,
 	  	function reg(data){
 	  		result = JSON.parse(data)
 	  		if (result['success'] == 0)
 	  			alert(result['message'])
 	  		else{
 	  			setCookie('userid', result['userid'], 1)
 	  			setCookie('username', result['username'], 1)
 	  			setCookie('truename', result['name'], 1)
 	  			setCookie('token', result['token'], 1)
 	  			loginstatus()
 	  			document.getElementById('LayerLogin').style.display = 'none'
 	  			document.getElementById('passwordl').value = ''
 	  		}
 	  	}
 	  	)
 	  }

 	  function logout(){
 	  	d = {}
 	  	d['username'] = getCookie('username')
 	  	d['token'] = getCookie('token')
 	  	delCookie('username')
 	  	delCookie('userid')
 	  	delCookie('truename')
 	  	delCookie('token')
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/logout/'+jsondata)
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

 	  function tomodify(){
 	  	showform('LayerModify')
 	  	document.getElementById('namem').value = getCookie('truename')
 	  }

 	  function modify(){
 	  	d = {}
 	  	d['username'] = getCookie('username')
 	  	d['name'] = document.getElementById('namem').value
 	  	d['token'] = getCookie('token')
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/modify/'+jsondata,
 	  		function modifyre(data){
 	  			result = JSON.parse(data)
 	  			document.getElementById('LayerModify').style.display = 'none'
 	  			if (result['success'] == 1)
 	  				setCookie('truename', document.getElementById('namem').value, 1)
 	  			alert(result['message'])
 	  		}
 	  	)
 	  }

 	  function modifypassword(){
 	  	if (document.getElementById('newpass').value != document.getElementById('renewpass').value){
 	  		alert('两次密码不相同')
 	  		return
 	  	}
 	  	d = {}
 	  	d['username'] = getCookie('username')
 	  	d['oldpass'] = $.md5(document.getElementById('oldpass').value)
 	  	d['newpass'] = $.md5(document.getElementById('newpass').value)
 	  	d['token'] = getCookie('token')
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/modifypassword/'+jsondata,
 	  		function modifyre(data){
 	  			result = JSON.parse(data)
 	  			if (result['success'] == 1){
 	  				document.getElementById('oldpass').value = ''
 	  				document.getElementById('newpass').value = ''
 	  				document.getElementById('renewpass').value = ''
 	  				document.getElementById('LayerModifypassword').style.display = 'none'
 	  			}
 	  			alert(result['message'])
 	  		}
 	  	)
 	  }