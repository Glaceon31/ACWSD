var senselist = []
var predictlist = []
var taglist = []

function submit(text){
   		d = {}
   		d['sentence'] = text
   		d['username'] = getCookie('username')
   		jsondata = JSON.stringify(d)
 	  	$.post('/wsd/'+jsondata,
 	  	function(data){
 	  		senselist = []
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
 	  	xml = parser.parseFromString(senselist[sensenum],'text/xml')
 	  	root = xml.getElementsByTagName('character')
 	  	ch = root[0].attributes.value.nodeValue
 	  	prontag = root[0].getElementsByTagName('pron')
 	  	var i = 0
 	  	tagsensenum = 0
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

 	  	if (lock == 1)
 	  		document.getElementById("sense").innerHTML += '<input type="button" id="tagcorpus" value="提交标注" onclick="updatecorpus()"/>'
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
 	  	
 	  }

function randomsentence(){
	$.post('/random',
	function randre(data){
		document.getElementById('inputtextarea').value = data
	}
	)
}

function randomsentencecond(cond){
	$.post('/randomcond/'+cond,
	function randcondre(data){
		document.getElementById('inputtextarea').value = data
	}
	)
}

function baidu(){
	sentence = document.getElementById('inputtextarea').value
	window.open('http://www.baidu.com/s?wd='+sentence, '_blank')
}