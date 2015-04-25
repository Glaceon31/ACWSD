var senselist = []
var predictlist = []

function submit(){
   		text = document.getElementById('inputtextarea').value
 	  	$.post('/wsd/'+text,
 	  	function(data){
 	  		senselist = []
 	  		predictlist = []
 	  		sentence = JSON.parse(data)
 	  		document.getElementById("sense").innerHTML = ''
 	  		document.getElementById('result').innerHTML = ''
 	  		for (i in sentence){
 	  			senselist.push('')
 	  			predictlist.push('')
 	  			if (sentence[i].sense == ''){
 	  				document.getElementById('result').innerHTML += '<nospan id="word'+String(i)+'">'+sentence[i].word+'</nospan>'
 	  			}
 	  			else{
 	  				reg0 = new RegExp('\n', 'g')
 	  				reg1 = new RegExp('\t', 'g')
 	  				senselist[i] = sentence[i].sense//.replace(reg0, '').replace(reg1, '')
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
 	  			sense = sensetag[j].attributes.vernacular.nodeValue
 	  			var sensehtml = ''
 	  			if (lock == 1)
 	  				sensehtml += '<'+pos+'> '+sense+'<input id="radio'+String(tagsensenum)+'" value="'+sense+'" name="sense" type="radio"/><br>'
 	  			else
 	  				sensehtml += '<'+pos+'> '+sense+'<br>'
 	  			if (predictlist[sensenum] == sense)
 	  				sensehtml = '<nospan style="color:red">'+sensehtml+'</nospan>'
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
 	  			submit()
 	  			current = tmpcurrent
 	  			document.getElementById("sense").innerHTML = ''
 	  			changesense(current)
 	  			if (result['message'] == '标注成功'){
 	  				tmp = parseInt(getCookie('tagnum'))
 	  				setCookie('tagnum', String(tmp+1), 1)
 	  			}
 	  			alert(result['message'])
 	  			
 	  		}
 	  		else{
 	  			alert(result['message'])
 	  		}
 	  	}
 	  	)
 	  	return
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