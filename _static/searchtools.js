if(!Scorer){var Scorer={objNameMatch:11,objPartialMatch:6,objPrio:{0:15,1:5,2:-5},objPrioDefault:0,title:15,partialTitle:7,term:5,partialTerm:2};}
if(!splitQuery){function splitQuery(query){return query.split(/\s+/);}}
var Search={_index:null,_queued_query:null,_pulse_status:-1,htmlToText:function(htmlString){var virtualDocument=document.implementation.createHTMLDocument('virtual');var htmlElement=$(htmlString,virtualDocument);htmlElement.find('.headerlink').remove();docContent=htmlElement.find('[role=main]')[0];if(docContent===undefined){console.warn("Content block not found. Sphinx search tries to obtain it "+
"via '[role=main]'. Could you check your theme or template.");return"";}
return docContent.textContent||docContent.innerText;},init:function(){var params=$.getQueryParameters();if(params.q){var query=params.q[0];$('input[name="q"]')[0].value=query;this.performSearch(query);}},loadIndex:function(url){$.ajax({type:"GET",url:url,data:null,dataType:"script",cache:true,complete:function(jqxhr,textstatus){if(textstatus!="success"){document.getElementById("searchindexloader").src=url;}}});},setIndex:function(index){var q;this._index=index;if((q=this._queued_query)!==null){this._queued_query=null;Search.query(q);}},hasIndex:function(){return this._index!==null;},deferQuery:function(query){this._queued_query=query;},stopPulse:function(){this._pulse_status=0;},startPulse:function(){if(this._pulse_status>=0)
return;function pulse(){var i;Search._pulse_status=(Search._pulse_status+1)%4;var dotString='';for(i=0;i<Search._pulse_status;i++)
dotString+='.';Search.dots.text(dotString);if(Search._pulse_status>-1)
window.setTimeout(pulse,500);}
pulse();},performSearch:function(query){this.out=$('#search-results');this.title=$('<h2>'+_('Searching')+'</h2>').appendTo(this.out);this.dots=$('<span></span>').appendTo(this.title);this.status=$('<p class="search-summary">&nbsp;</p>').appendTo(this.out);this.output=$('<ul class="search"/>').appendTo(this.out);$('#search-progress').text(_('Preparing search...'));this.startPulse();if(this.hasIndex())
this.query(query);else
this.deferQuery(query);},query:function(query){var i;var stemmer=new Stemmer();var searchterms=[];var excluded=[];var hlterms=[];var tmp=splitQuery(query);var objectterms=[];for(i=0;i<tmp.length;i++){if(tmp[i]!==""){objectterms.push(tmp[i].toLowerCase());}
if($u.indexOf(stopwords,tmp[i].toLowerCase())!=-1||tmp[i]===""){continue;}
var word=stemmer.stemWord(tmp[i].toLowerCase());if(word.length<3&&tmp[i].length>=3){word=tmp[i];}
var toAppend;if(word[0]=='-'){toAppend=excluded;word=word.substr(1);}
else{toAppend=searchterms;hlterms.push(tmp[i].toLowerCase());}
if(!$u.contains(toAppend,word))
toAppend.push(word);}
var highlightstring='?highlight='+$.urlencode(hlterms.join(" "));var terms=this._index.terms;var titleterms=this._index.titleterms;var results=[];$('#search-progress').empty();for(i=0;i<objectterms.length;i++){var others=[].concat(objectterms.slice(0,i),objectterms.slice(i+1,objectterms.length));results=results.concat(this.performObjectSearch(objectterms[i],others));}
results=results.concat(this.performTermsSearch(searchterms,excluded,terms,titleterms));if(Scorer.score){for(i=0;i<results.length;i++)
results[i][4]=Scorer.score(results[i]);}
results.sort(function(a,b){var left=a[4];var right=b[4];if(left>right){return 1;}else if(left<right){return-1;}else{left=a[1].toLowerCase();right=b[1].toLowerCase();return(left>right)?-1:((left<right)?1:0);}});var resultCount=results.length;function displayNextItem(){if(results.length){var item=results.pop();var listItem=$('<li></li>');var requestUrl="";var linkUrl="";if(DOCUMENTATION_OPTIONS.BUILDER==='dirhtml'){var dirname=item[0]+'/';if(dirname.match(/\/index\/$/)){dirname=dirname.substring(0,dirname.length-6);}else if(dirname=='index/'){dirname='';}
requestUrl=DOCUMENTATION_OPTIONS.URL_ROOT+dirname;linkUrl=requestUrl;}else{requestUrl=DOCUMENTATION_OPTIONS.URL_ROOT+item[0]+DOCUMENTATION_OPTIONS.FILE_SUFFIX;linkUrl=item[0]+DOCUMENTATION_OPTIONS.LINK_SUFFIX;}
listItem.append($('<a/>').attr('href',linkUrl+
highlightstring+item[2]).html(item[1]));if(item[3]){listItem.append($('<span> ('+item[3]+')</span>'));Search.output.append(listItem);setTimeout(function(){displayNextItem();},5);}else if(DOCUMENTATION_OPTIONS.HAS_SOURCE){$.ajax({url:requestUrl,dataType:"text",complete:function(jqxhr,textstatus){var data=jqxhr.responseText;if(data!==''&&data!==undefined){var summary=Search.makeSearchSummary(data,searchterms,hlterms);if(summary){listItem.append(summary);}}
Search.output.append(listItem);setTimeout(function(){displayNextItem();},5);}});}else{Search.output.append(listItem);setTimeout(function(){displayNextItem();},5);}}
else{Search.stopPulse();Search.title.text(_('Search Results'));if(!resultCount)
Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));else
Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s',resultCount));Search.status.fadeIn(500);}}
displayNextItem();},performObjectSearch:function(object,otherterms){var filenames=this._index.filenames;var docnames=this._index.docnames;var objects=this._index.objects;var objnames=this._index.objnames;var titles=this._index.titles;var i;var results=[];for(var prefix in objects){for(var name in objects[prefix]){var fullname=(prefix?prefix+'.':'')+name;var fullnameLower=fullname.toLowerCase()
if(fullnameLower.indexOf(object)>-1){var score=0;var parts=fullnameLower.split('.');if(fullnameLower==object||parts[parts.length-1]==object){score+=Scorer.objNameMatch;}else if(parts[parts.length-1].indexOf(object)>-1){score+=Scorer.objPartialMatch;}
var match=objects[prefix][name];var objname=objnames[match[1]][2];var title=titles[match[0]];if(otherterms.length>0){var haystack=(prefix+' '+name+' '+
objname+' '+title).toLowerCase();var allfound=true;for(i=0;i<otherterms.length;i++){if(haystack.indexOf(otherterms[i])==-1){allfound=false;break;}}
if(!allfound){continue;}}
var descr=objname+_(', in ')+title;var anchor=match[3];if(anchor==='')
anchor=fullname;else if(anchor=='-')
anchor=objnames[match[1]][1]+'-'+fullname;if(Scorer.objPrio.hasOwnProperty(match[2])){score+=Scorer.objPrio[match[2]];}else{score+=Scorer.objPrioDefault;}
results.push([docnames[match[0]],fullname,'#'+anchor,descr,score,filenames[match[0]]]);}}}
return results;},escapeRegExp:function(string){return string.replace(/[.*+\-?^${}()|[\]\\]/g,'\\$&');},performTermsSearch:function(searchterms,excluded,terms,titleterms){var docnames=this._index.docnames;var filenames=this._index.filenames;var titles=this._index.titles;var i,j,file;var fileMap={};var scoreMap={};var results=[];for(i=0;i<searchterms.length;i++){var word=searchterms[i];var files=[];var _o=[{files:terms[word],score:Scorer.term},{files:titleterms[word],score:Scorer.title}];if(word.length>2){var word_regex=this.escapeRegExp(word);for(var w in terms){if(w.match(word_regex)&&!terms[word]){_o.push({files:terms[w],score:Scorer.partialTerm})}}
for(var w in titleterms){if(w.match(word_regex)&&!titleterms[word]){_o.push({files:titleterms[w],score:Scorer.partialTitle})}}}
if($u.every(_o,function(o){return o.files===undefined;})){break;}
$u.each(_o,function(o){var _files=o.files;if(_files===undefined)
return
if(_files.length===undefined)
_files=[_files];files=files.concat(_files);for(j=0;j<_files.length;j++){file=_files[j];if(!(file in scoreMap))
scoreMap[file]={};scoreMap[file][word]=o.score;}});for(j=0;j<files.length;j++){file=files[j];if(file in fileMap&&fileMap[file].indexOf(word)===-1)
fileMap[file].push(word);else
fileMap[file]=[word];}}
for(file in fileMap){var valid=true;var filteredTermCount=searchterms.filter(function(term){return term.length>2}).length
if(fileMap[file].length!=searchterms.length&&fileMap[file].length!=filteredTermCount)continue;for(i=0;i<excluded.length;i++){if(terms[excluded[i]]==file||titleterms[excluded[i]]==file||$u.contains(terms[excluded[i]]||[],file)||$u.contains(titleterms[excluded[i]]||[],file)){valid=false;break;}}
if(valid){var score=$u.max($u.map(fileMap[file],function(w){return scoreMap[file][w]}));results.push([docnames[file],titles[file],'',null,score,filenames[file]]);}}
return results;},makeSearchSummary:function(htmlText,keywords,hlwords){var text=Search.htmlToText(htmlText);if(text==""){return null;}
var textLower=text.toLowerCase();var start=0;$.each(keywords,function(){var i=textLower.indexOf(this.toLowerCase());if(i>-1)
start=i;});start=Math.max(start-120,0);var excerpt=((start>0)?'...':'')+
$.trim(text.substr(start,240))+
((start+240-text.length)?'...':'');var rv=$('<p class="context"></p>').text(excerpt);$.each(hlwords,function(){rv=rv.highlightText(this,'highlighted');});return rv;}};$(document).ready(function(){Search.init();});
