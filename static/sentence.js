var senselist = []
var usersenselist = []
var predictlist = []
var taglist = []
var sentence = []

function submit(text){
   		d = {}
   		d['sentence'] = text
   		d['username'] = getCookie('username')
   		jsondata = JSON.stringify(d)
 	  	$.post('/wsd/'+jsondata,
 	  	function(data){
 	  		senselist = []
 	  		usersenselist = []
 	  		predictlist = []
 	  		taglist = []
 	  		sentence = JSON.parse(data)
 	  		document.getElementById("sense").innerHTML = ''
 	  		document.getElementById('result').innerHTML = ''
 	  		for (i in sentence){
 	  			senselist.push('')
 	  			predictlist.push('')
 	  			taglist.push('')
 	  			if (sentence[i].sense == ''){
 	  				document.getElementById('result').innerHTML += '<nospan id="word'+String(i)+'">'+sentence[i].word+'</nospan>'
 	  			}
 	  			else{
 	  				reg0 = new RegExp('\n', 'g')
 	  				reg1 = new RegExp('\t', 'g')
 	  				senselist[i] = sentence[i].sense//.replace(reg0, '').replace(reg1, '')
 	  				if (sentence[i].tagged == 1){
 	  					document.getElementById('result').innerHTML += '<nospan style="color:blue" id="word'+String(i)+'" onmouseover="if (lock == 0) changesense('+String(i)+')" onclick=lockorunlock('+String(i)+')>'+sentence[i].word+'</nospan>'
 	  					taglist[i] = sentence[i].usertag
 	  				}
 	  				else
 	  					document.getElementById('result').innerHTML += '<nospan id="word'+String(i)+'" onmouseover="if (lock == 0) changesense('+String(i)+')" onclick=lockorunlock('+String(i)+')>'+sentence[i].word+'</nospan>'
 	  				if (sentence[i].predictsense != ''){
 	  					predictlist[i] = sentence[i].predictsense
 	  				}
 	  			}
 	  			
 	  		}
 	  		lock = 0
 	  		current = -1
 	  	}
 	  	)
 	  }
 	  
 	  function changesense(sensenum){
 	  //	if (lock == 1)
 	  //		return
 	  	if (current != -1){
 	  		if (taglist[current] != '')
 	  			document.getElementById('word'+String(current)).style.color = 'blue'
 	  		else
 	  			document.getElementById('word'+String(current)).style.color = ''
 	  	}
 	  	document.getElementById('word'+String(sensenum)).style.color = 'red'
 	  	document.getElementById("sense").innerHTML = ''
 	  	current = sensenum
 	  	parser = new DOMParser()
 	  	sensedata = senselist[sensenum]
 	  	xml = parser.parseFromString(sensedata['dictsense'],'text/xml')
 	  	root = xml.getElementsByTagName('character')
 	  	ch = root[0].attributes.value.nodeValue
 	  	prontag = root[0].getElementsByTagName('pron')
 	  	var i = 0
 	  	tagsensenum = 0
 	  	if (lock == 1)
 	  		document.getElementById("sense").innerHTML += '<input type="button" id="tagcorpus" value="提交标注" onclick="updatecorpus()"/><br>'
 	  	for (;i<prontag.length; i++){
 	  		pron = prontag[i].attributes.value.nodeValue
 	  		document.getElementById("sense").innerHTML += pron+'<br>'
 	  		sensetag = prontag[i].getElementsByTagName('sense')
 	  		var j = 0
 	  		for (;j<sensetag.length;j++){
 	  			try{
 	  				pos = sensetag[j].attributes.tag.nodeValue
 	  			}catch(e){
 	  				pos = '无'
 	  			}
 	  			examtag = sensetag[j].getElementsByTagName('exam')
 	  			sense = sensetag[j].attributes.vernacular.nodeValue
 	  			var sensehtml = ''
 	  			if (lock == 1){
 	  				if (sense == taglist[sensenum])
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio" checked/>';
 	  				else
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio"/>';
 	  			}
 	  			sensehtml += String(tagsensenum+1)+'. '
 	  			sensehtml += '<'+pos+'> '+sense
 	  			if (predictlist[sensenum] == sense)
 	  				sensehtml = '<nospan style="color:red">'+sensehtml+'</nospan>'
 	  			if (examtag.length > 0){
 	  				sensehtml += '。'+examtag[0].attributes.article.nodeValue+': “'
 	  				for (k in examtag[0].attributes.ref.nodeValue){
 	  					addword = examtag[0].attributes.ref.nodeValue[k]
 	  					if (addword == ch)
 	  						sensehtml += '<nospan style="color:red">'+addword+'</nospan>'
 	  					else
 	  						sensehtml += addword
 	  				}
 	  				sensehtml += '”'
 	  			}
 	  			sensehtml += '<br>'
 	  			document.getElementById("sense").innerHTML += sensehtml
 	  			tagsensenum += 1
 	  		}
 	  	}
 	  	i = 0
 	  	usersense = sensedata['usersense']
 	  	if (usersense.length > 0){
 	  		document.getElementById("sense").innerHTML += '用户添加义项<br>'
 	  		for (; i<usersense.length; i++){
 	  			sensehtml = ''
 	  			sense = usersense[i]['sense']
 	  			if (lock == 1){
 	  				if (sense == taglist[sensenum])
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio" checked/>';
 	  				else
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio"/>';
 	  			}
 	  			sensehtml += String(tagsensenum+1)+'. '
 	  			sensehtml += '<'+usersense[i]['pos']+'> '+usersense[i]['sense']
 	  			if (predictlist[sensenum] == sense)
 	  				sensehtml = '<nospan style="color:red">'+sensehtml+'</nospan>'
 	  			if (usersense[i]['example'].length > 0){
 	  				sensehtml += '。“'
 	  				for (k in usersense[i]['example']){
 	  					addword = usersense[i]['example'][k]
 	  					if (addword == ch)
 	  						sensehtml += '<nospan style="color:red">'+addword+'</nospan>'
 	  					else
 	  						sensehtml += addword
 	  				}
 	  				sensehtml += '”'
 	  			}
 	  			sensehtml += '<br>'
 	  			document.getElementById("sense").innerHTML += sensehtml
 	  			tagsensenum += 1
 	  		}
 	  		
 	  	}
 	  	phrasetag = root[0].getElementsByTagName('phrase')
 	  	i = 0
 	  	for (; i < phrasetag.length; i++){
 	  		document.getElementById("sense").innerHTML += '【'+phrasetag[i].attributes.value.nodeValue+'】<br>'
 	  		sensetag = phrasetag[i].getElementsByTagName('sense')
 	  		j = 0
 	  		for (;j < sensetag.length; j++){
 	  			sense = sensetag[j].attributes.value.nodeValue
 	  			sensehtml = ''
 	  			if (lock == 1){
 	  				if (sense == taglist[sensenum])
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio" checked/>';
 	  				else
 	  					sensehtml += '<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio"/>';
 	  			}
 	  			sensehtml += String(tagsensenum+1)+'. '
 	  			sensehtml += sense
 	  			if (predictlist[sensenum] == sense)
 	  				sensehtml = '<nospan style="color:red">'+sensehtml+'</nospan>'
 	  			sensehtml += '<br>'
 	  			document.getElementById("sense").innerHTML += sensehtml
 	  			tagsensenum += 1
 	  		}
 	  	}
 	  	if (lock == 1){
 	  		sensehtml = '添加新的义项<br>词性<select id="newpos">'
 	  		sensehtml += posoption('名')
 	  		sensehtml += posoption('动')
 	  		sensehtml += posoption('代')
 	  		sensehtml += posoption('副')
 	  		sensehtml += posoption('介')
 	  		sensehtml += posoption('助')
 	  		sensehtml += posoption('形')
 	  		sensehtml += posoption('连')
 	  		sensehtml += posoption('无')
 	  		sensehtml += posoption('数')
 	  		sensehtml += posoption('量')
 	  		sensehtml += posoption('名使动')
 	  		sensehtml += '</select><br>发音<input type="text" id="newpron" size=3></input><br>'
 	  		sensehtml += '释义<input type="text" id="newsense"></input><br>'
 	  		sensehtml += '例句<input type="text" id="newexample"></input>'
 	  		sensehtml += '<br><input type="button" onclick="addsense()" value="添加义项"/><br>'
 	  		document.getElementById("sense").innerHTML += sensehtml
 	  	}
 	  }

 	  function posoption(pos){
 	  	return '<option value="'+pos+'">'+pos+'</option>'
 	  }

 	  function updatecorpus(){
 	  	tagword = document.getElementById('word'+String(current)).innerHTML
 	  	tagsense = ''
 	  	var j = 0
 	  	for (;j < tagsensenum; j++){
 	  		if (document.getElementById('radio'+String(j)).checked){
 	  			tagsense = document.getElementById('radio'+String(j)).value
 	  			break
 	  		}
 	  	}
 	  	tagsentence = ''
 	  	for (i in senselist)
 	  		tagsentence += document.getElementById('word'+String(i)).innerHTML
 	  	tagdata = {}
 	  	tagdata['token'] = getCookie('token')
 	  	tagdata['word'] = current
 	  	tagdata['sentence'] = tagsentence
 	  	tagdata['sense'] = tagsense
 	  	tagdata['tagger'] = getCookie('username')
 	  	jsondata = JSON.stringify(tagdata)
 	  	$.post('/update/'+jsondata,
 	  	function(data){
 	  		result = JSON.parse(data)
 	  		if (result['success'] == 1){
 	  			lock = 0
 	  			var tmpcurrent = current
 	  			submit(tagsentence)
 	  			current = tmpcurrent
 	  			document.getElementById("sense").innerHTML = ''
 	  			changesense(current)
 	  			if (result['message'] == '标注成功'){
 	  				tmp = parseInt(getCookie('tagnum'))
 	  				setCookie('tagnum', String(tmp+1), 1)
 	  			}
 	  			//alert(result['message'])
 	  			
 	  		}
 	  		else{
 	  			alert(result['message'])
 	  		}
 	  	}
 	  	)
 	  	return
 	  }

 	  function addsense(){
 	  	d = {}
 	  	d['pron'] = document.getElementById('newpron').value
 	  	d['example'] = document.getElementById('newexample').value
 	  	d['word'] = sentence[current].word
 	  	d['username'] = getCookie('username')
 	  	d['token'] = getCookie('token')
 	  	d['pos'] = document.getElementById('newpos').value
 	  	d['sense']  = document.getElementById('newsense').value
 	  	if (d['sense'] == ''){
 	  		alert('义项不能为空')
 	  		return
 	  	}
 	  	jsondata = JSON.stringify(d)
 	  	$.post('/addsense/'+jsondata,
 	  		function addsensere(data){
 	  			result = JSON.parse(data)
 	  			tagsentence = ''
 	  			for (i in senselist)
 	  				tagsentence += document.getElementById('word'+String(i)).innerHTML
 	  			submit(tagsentence)
 	  			alert(result['message'])
 	  		}
 	  	)
 	  }

 	  function deletesense(){

 	  }

function randomsentence(){
	mid = document.getElementById('midschool').checked
	high = document.getElementById('highschool').checked
	if (mid && high){
		alert('请不要复选')
		return
	}
	if (!mid && !high){
		$.post('/random',
		function randre(data){
			document.getElementById('inputtextarea').value = data
		}
		)
	}
	else{
		if (mid) cond = 'midschool'
		if (high) cond = 'highschool'
		$.post('/randomcond/'+cond,
		function randcondre(data){
			document.getElementById('inputtextarea').value = data
		}
		)
	}
}

function randomsentencesub(){
	mid = document.getElementById('midschool').checked
	high = document.getElementById('highschool').checked
	if (mid && high){
		alert('请不要复选')
		return
	}
	if (!mid && !high){
		$.post('/randomsub',
		function randcondre(data){
			document.getElementById('inputtextarea').value = data
		}
		)
	}
	else{
		if (mid) cond = 'midschool'
		if (high) cond = 'highschool'
		$.post('/randomsubcond/'+cond,
		function randcondre(data){
			document.getElementById('inputtextarea').value = data
		}
		)
	}
}

function baidu(){
	sentence = document.getElementById('inputtextarea').value
	window.open('http://www.baidu.com/s?wd='+sentence, '_blank')
}