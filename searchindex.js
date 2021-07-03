Search.setIndex({docnames:["api","api-application","api-child","api-config","api-control","api-daemon","api-exceptions","api-logs","api-protocols","api-smtp","api-streams","api-supervisor","api-utils","api-worker","changelog","command-auth","command-expn","command-vrfy","communicating-with-blackhole","configuration","dynamic-responses","dynamic-switches","index","overview","todo"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api.rst","api-application.rst","api-child.rst","api-config.rst","api-control.rst","api-daemon.rst","api-exceptions.rst","api-logs.rst","api-protocols.rst","api-smtp.rst","api-streams.rst","api-supervisor.rst","api-utils.rst","api-worker.rst","changelog.rst","command-auth.rst","command-expn.rst","command-vrfy.rst","communicating-with-blackhole.rst","configuration.rst","dynamic-responses.rst","dynamic-switches.rst","index.rst","overview.rst","todo.rst"],objects:{"blackhole.application":{blackhole_config:[1,1,1,""],run:[1,1,1,""]},"blackhole.child":{Child:[2,2,1,""]},"blackhole.child.Child":{clients:[2,3,1,""],heartbeat:[2,4,1,""],servers:[2,3,1,""],start:[2,4,1,""],stop:[2,4,1,""]},"blackhole.config":{Config:[3,2,1,""],_compare_uid_and_gid:[3,1,1,""],config_test:[3,1,1,""],parse_cmd_args:[3,1,1,""],warn_options:[3,1,1,""]},"blackhole.config.Config":{args:[3,3,1,""],config_file:[3,3,1,""],create_flags:[3,4,1,""],delay:[3,5,1,""],dynamic_switch:[3,5,1,""],flags_from_listener:[3,4,1,""],group:[3,5,1,""],listen:[3,5,1,""],load:[3,4,1,""],max_message_size:[3,5,1,""],mode:[3,5,1,""],pidfile:[3,5,1,""],test:[3,4,1,""],test_delay:[3,4,1,""],test_dynamic_switch:[3,4,1,""],test_group:[3,4,1,""],test_ipv6_support:[3,4,1,""],test_max_message_size:[3,4,1,""],test_mode:[3,4,1,""],test_no_listeners:[3,4,1,""],test_pidfile:[3,4,1,""],test_port:[3,4,1,""],test_same_listeners:[3,4,1,""],test_timeout:[3,4,1,""],test_tls_dhparams:[3,4,1,""],test_tls_ipv6_support:[3,4,1,""],test_tls_port:[3,4,1,""],test_tls_settings:[3,4,1,""],test_user:[3,4,1,""],test_workers:[3,4,1,""],timeout:[3,5,1,""],tls_cert:[3,5,1,""],tls_dhparams:[3,5,1,""],tls_key:[3,5,1,""],tls_listen:[3,5,1,""],user:[3,5,1,""],validate_option:[3,4,1,""],workers:[3,5,1,""]},"blackhole.control":{_context:[4,1,1,""],_socket:[4,1,1,""],pid_permissions:[4,1,1,""],server:[4,1,1,""],setgid:[4,1,1,""],setuid:[4,1,1,""]},"blackhole.daemon":{Daemon:[5,2,1,""]},"blackhole.daemon.Daemon":{daemonize:[5,4,1,""],fork:[5,4,1,""],pid:[5,5,1,""]},"blackhole.exceptions":{BlackholeRuntimeException:[6,6,1,""],ConfigException:[6,6,1,""],DaemonException:[6,6,1,""]},"blackhole.exceptions.BlackholeRuntimeException":{with_traceback:[6,4,1,""]},"blackhole.exceptions.ConfigException":{with_traceback:[6,4,1,""]},"blackhole.exceptions.DaemonException":{with_traceback:[6,4,1,""]},"blackhole.logs":{configure_logs:[7,1,1,""]},"blackhole.protocols":{PING:[8,7,1,""],PONG:[8,7,1,""]},"blackhole.smtp":{Smtp:[9,2,1,""]},"blackhole.smtp.Smtp":{auth_CRAM_MD5:[9,4,1,""],auth_LOGIN:[9,4,1,""],auth_PLAIN:[9,4,1,""],auth_UNKNOWN:[9,4,1,""],close:[9,4,1,""],connection_lost:[9,4,1,""],connection_made:[9,4,1,""],data_received:[9,4,1,""],delay:[9,5,1,""],do_DATA:[9,4,1,""],do_EHLO:[9,4,1,""],do_ETRN:[9,4,1,""],do_EXPN:[9,4,1,""],do_HELO:[9,4,1,""],do_HELP:[9,4,1,""],do_MAIL:[9,4,1,""],do_NOOP:[9,4,1,""],do_NOT_IMPLEMENTED:[9,4,1,""],do_QUIT:[9,4,1,""],do_RCPT:[9,4,1,""],do_RSET:[9,4,1,""],do_STARTTLS:[9,4,1,""],do_UNKNOWN:[9,4,1,""],do_VRFY:[9,4,1,""],eof_received:[9,4,1,""],flags_from_transport:[9,4,1,""],get_auth_members:[9,4,1,""],get_help_members:[9,4,1,""],greet:[9,4,1,""],help_AUTH:[9,4,1,""],help_DATA:[9,4,1,""],help_EHLO:[9,4,1,""],help_ETRN:[9,4,1,""],help_EXPN:[9,4,1,""],help_HELO:[9,4,1,""],help_MAIL:[9,4,1,""],help_NOOP:[9,4,1,""],help_QUIT:[9,4,1,""],help_RCPT:[9,4,1,""],help_RSET:[9,4,1,""],help_UNKNOWN:[9,4,1,""],help_VRFY:[9,4,1,""],lookup_auth_handler:[9,4,1,""],lookup_handler:[9,4,1,""],lookup_help_handler:[9,4,1,""],lookup_verb_handler:[9,4,1,""],mode:[9,5,1,""],pause_writing:[9,4,1,""],process_header:[9,4,1,""],push:[9,4,1,""],response_from_mode:[9,4,1,""],resume_writing:[9,4,1,""],timeout:[9,4,1,""],wait:[9,4,1,""]},"blackhole.streams":{StreamProtocol:[10,2,1,""]},"blackhole.streams.StreamProtocol":{connection_lost:[10,4,1,""],connection_made:[10,4,1,""],data_received:[10,4,1,""],eof_received:[10,4,1,""],is_connected:[10,4,1,""],pause_writing:[10,4,1,""],resume_writing:[10,4,1,""]},"blackhole.supervisor":{Supervisor:[11,2,1,""]},"blackhole.supervisor.Supervisor":{close_socks:[11,4,1,""],create_socket:[11,4,1,""],generate_servers:[11,4,1,""],run:[11,4,1,""],start_workers:[11,4,1,""],stop:[11,4,1,""],stop_workers:[11,4,1,""]},"blackhole.utils":{Formatter:[12,2,1,""],Singleton:[12,2,1,""],blackhole_config_help:[12,7,1,""],formatting:[12,7,1,""],get_version:[12,1,1,""],mailname:[12,1,1,""],message_id:[12,1,1,""]},"blackhole.worker":{Worker:[13,2,1,""]},"blackhole.worker.Worker":{chat:[13,4,1,""],connect:[13,4,1,""],heartbeat:[13,4,1,""],kill_child:[13,4,1,""],restart_child:[13,4,1,""],setup_child:[13,4,1,""],start:[13,4,1,""],stop:[13,4,1,""]},blackhole:{application:[1,0,0,"-"],child:[2,0,0,"-"],config:[3,0,0,"-"],control:[4,0,0,"-"],daemon:[5,0,0,"-"],exceptions:[6,0,0,"-"],logs:[7,0,0,"-"],protocols:[8,0,0,"-"],smtp:[9,0,0,"-"],streams:[10,0,0,"-"],supervisor:[11,0,0,"-"],utils:[12,0,0,"-"],worker:[13,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","attribute","Python attribute"],"4":["py","method","Python method"],"5":["py","property","Python property"],"6":["py","exception","Python exception"],"7":["py","data","Python data"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:attribute","4":"py:method","5":"py:property","6":"py:exception","7":"py:data"},terms:{"0":[3,4,9,15,17,18,19,23,24],"0x13":14,"0x14":14,"0x23":14,"0x24":14,"0x27":14,"0x28":14,"0x2b":14,"0x2c":14,"0x2f":14,"0x30":14,"0xc0":14,"0xcc":14,"1":[3,9,17,18,19,23],"10":[3,19,21,23,24],"1024":19,"1024000":19,"1025":3,"11":23,"12":23,"127":[3,19],"128":14,"13":[4,19,23],"14":[23,24],"15":[13,23],"16":23,"180":[3,19],"2":[4,9,15,17,18,19,23,24],"2013":23,"2021":23,"221":18,"235":[9,15],"23749":[14,19],"25":[3,14,18,19],"250":[9,14,16,17,18],"252":[9,17],"256":14,"2822":12,"3":[2,13,22,23],"30":[13,19,21],"334":[9,15],"354":18,"4":[19,23,24],"421":[9,19],"450":18,"451":18,"452":18,"458":18,"465":[18,19],"5":[3,9,15,17,19,22,23],"500":19,"501":14,"512":[3,14,19],"512000":[3,14,19],"521":18,"535":[9,15],"550":[9,16,17,18],"551":18,"552":18,"553":18,"571":18,"587":[3,14,19],"6":[19,23],"60":[3,9,19,21],"7":[9,15,17,23],"7bit":18,"8":[9,15,18,19,23],"82000":18,"8bitmim":18,"9":23,"\u00df\u00e6\u00f8\u00fe":18,"byte":[2,3,9,13,14,19],"case":4,"catch":14,"class":[2,3,5,9,10,11,12,13],"default":[3,4,9,12,14,15,17,19,21,24],"do":[14,19,22],"final":[2,9,14],"function":[1,2,3,4,5,9,11,12,13,14],"import":[9,10,12,18],"int":[3,4,5,9,13],"long":9,"new":[2,9,13,14,19,23],"null":22,"return":[3,4,5,6,9,12,14,16,17,19,20,24],"switch":[3,9,14,19,22,24],"true":[3,9,19],"try":23,"var":19,"while":[14,19,21,22,23],A:[2,3,4,6,9,12,13,14,21,23],AND:23,AS:23,And:9,BE:23,BUT:23,By:[15,17],FOR:23,For:[18,20,21],IN:23,IS:23,If:[2,3,4,5,9,13,14,23],In:14,It:[14,19,22],NO:23,NOT:[23,24],No:14,Not:[9,16,19],OF:23,OR:23,On:19,Or:17,THE:23,TO:[9,18,23],The:[3,4,5,9,11,12,13,14,16,19,21,23],Then:19,There:[14,23],These:[2,9,10,13,14],To:[18,19,21,23],WITH:23,Will:[9,14,17],With:[4,5,11,22],__traceback__:6,__version__:12,_compare_uid_and_gid:3,_context:4,_socket:4,abil:14,abort:18,about:[21,23],abov:[3,14,23],absolut:19,accept:[3,19,21,22,23],access:3,act:[14,19],action:[18,22,23],actual:[3,14,19,22],ad:[4,14,19,21,23,24],adapt:[9,10],add:[23,24],addit:[10,23],addr:[3,4],address:[3,4,18,19],advis:19,ae:14,aead:14,aes128:14,aes256:14,aesgcm:14,af_inet6:4,af_inet:[3,4],affect:[14,21],after:[4,9,18,24],against:[9,23],agent:22,alex:[9,16],all:[2,3,9,11,14,19,20,21,22,23,24],alloc:18,allow:[3,9,14,18,19,20,21,24],almost:14,alongsid:14,also:[2,3,4,9,13,14,16,18,19,23],alwai:[3,19],amo:[9,16],amount:[19,22],an:[3,4,5,9,11,12,13,14,20,21,22,23],ani:[21,23,24],anoth:21,api:[2,13,22,23],app:[9,10],appli:14,applic:[0,22],apt:19,ar:[2,3,4,9,10,13,14,16,19,21,22,23,24],arg:[2,3,5,7,11,14],argpars:[3,7],argument:[3,9,20,22,23],aris:23,ask:[15,16],assertionerror:12,assign:[9,19],associ:23,async:[2,9,13,14,22],asynchron:14,asyncio:[1,2,9,13,14,19,22,23],attach:11,attack:14,attempt:[9,14,17],au:14,auth:[9,14,18,20,22,24],auth_cram_md5:9,auth_login:9,auth_mechan:9,auth_plain:9,auth_unknown:9,authent:[9,15],author:23,authoris:[9,16],automat:[14,23],aux:19,avail:[2,9,13,14,19,22,24],await:[14,22],awar:19,b:[2,8,13,19,23],back:12,background:19,bancroft:[9,16],base:[9,14,24],becaus:[3,19,21],been:[5,14,19],befor:[4,9,13,14,19,21,22],begin:3,behaviour:[20,23],being:[2,14,19],below:[9,10,19,20],better:14,between:[2,10,13,14,21,24],biggest:14,bin:19,bind:[4,24],blackhol:[0,14,16,19,21,23,24],blackhole_config:[1,12,14,19],blackhole_config_help:12,blackholeruntimeexcept:[4,6],blindli:21,block:[14,18],bold:12,bool:[3,4],bounc:[3,19,21,22],bound:[4,13],branch:23,branch_nam:23,bring:14,buffer:[9,10],bug:[14,19,23],bugfix:14,build:[14,24],built:[14,16,19,22],builtin:19,bump:14,burton:[9,16],c:[14,19,23],call:[3,4,9,10,11,14,16,23],call_soon:[9,10],callabl:9,callback:[9,10],can:[3,9,13,16,17,18,19,20,21,22,23,24],cancel:2,cannot:[3,4,5,12],caus:[3,14,16,23],cdhe:14,cert:[3,19],certain:3,certif:[3,4,19],chacha20:14,chang:[4,14,18,23],changelog:22,channel:[2,13],charact:18,charg:23,chat:13,check:[3,9,14],checkout:23,child:[0,8,11,13,14,22],children:[11,14],chmod:19,choos:3,ci:14,cipher:[14,19],claim:23,cleanli:1,client:[2,9,10,14,19,20,21],close:[2,9,11,14],close_sock:11,code:[1,3,4,5,9,11,14,19,22],com:[21,24],combin:[14,16,22,24],come:[13,19],command:[3,4,9,14,16,20,22,24],comment:[3,14,23],commun:[2,8,9,13,14,22,23],compar:3,compil:14,complet:[9,19],compliant:[12,24],condit:[9,10,23],conduct:23,conf:[3,19],config:[0,1,14,22,24],config_fil:3,config_test:[3,14,24],configexcept:[3,6],configtest:14,configur:[1,3,4,6,7,9,14,21,22],configure_log:7,confirm:3,connect:[2,3,9,10,13,14,18,19,23],connection_lost:[9,10],connection_mad:[9,10],consol:[1,3],contain:[3,4,9,19],content:[3,12,18],context:[4,11,14,24],contract:23,contribut:[14,22],contributor:23,control:[0,2,11,14,22],convent:23,convers:[9,10],copi:[19,23],copyright:23,core:3,correct:3,could:[14,19],counter:14,cpu:[14,19],cr:18,cram:[9,14,18,20,22],crash:14,creat:[1,3,4,11,13,14,23],create_flag:3,create_socket:11,creation:24,crt:19,current:[3,5,13,19,23],cython:19,d:[14,22],daemon:[0,4,6,14,22],daemonexcept:[5,6],daemonis:5,damag:23,data:[9,10,13,14,15,19,22,24],data_receiv:[9,10],databas:3,daunt:23,deal:23,debian:[14,19],debug:[14,19],dedic:23,def:[14,22],defin:[2,3,13,19,20,24],definit:3,deiman:14,delai:[3,9,14,22,24],delet:5,deliv:22,deliveri:[9,17],denial:3,depend:19,descriptor:13,design:22,detail:[9,10],determin:12,dev:[19,22],develop:[14,23],dhparam:[3,4,19],dict:[3,4],dictionari:4,did:23,differ:[3,14],diffi:[3,4,14,19],direct:[3,14],directli:19,directori:19,disabl:[3,14,19],disconnect:14,disconnect_error:10,displai:[14,19],distribut:23,dkim:24,do_data:9,do_ehlo:9,do_etrn:9,do_expn:9,do_helo:9,do_help:9,do_mail:9,do_noop:9,do_not_impl:9,do_quit:9,do_rcpt:9,do_rset:9,do_starttl:9,do_unknown:9,do_verb:9,do_vrfi:9,doc:[14,23],docstr:23,document:[2,13,14,22],doe:[5,9,12,14,18,19],domain:[9,12,14,17,18],domainkei:24,don:[4,19],done:[18,23],doubl:3,down_read:13,down_writ:2,download:23,drain:[9,10],drop:19,dsn:18,dynam:[3,9,14,19,22,24],dynamic_switch:[3,22],e:[3,9,19,23,24],each:[2,3,11,14,23],easili:19,ecdh:[14,19],ecdsa:14,effect:[9,10],ehlo:[9,12,14,22,24],either:[9,10,22],els:[11,14],email:[9,14,18,19,21,22],enabl:[3,9,14,19],enc:14,encod:18,end:[9,10,18],enforc:14,enhancedstatuscod:18,ensur:[9,10],environ:14,eof:10,eof_receiv:[9,10],ephemer:[3,4,14,19],equal:[9,10],equival:[9,19],error:[1,4,14,16,18],etc:[12,19,24],etrn:[9,14,22],even:[9,10,19],event:[11,19,23],event_loop:14,eventloop:[9,10],eventu:[9,10],everyth:14,ex_noperm:[1,4],ex_ok:[1,3,5,11],ex_usag:[1,3,4],exampl:21,exc:[9,10],exceed:18,except:[0,9,14,22],execut:19,exist:[3,5,9,12,19],exit:[1,2,3,4,14,19],expect:[9,10,14],expens:[14,19],explicitli:[16,17],expn:[9,14,18,20,22,24],express:23,extend:24,extra:19,extract:12,fail:[9,13,14,16,17,20,24],failsaf:14,failur:9,falcon:[9,16],fall:12,fals:[3,4,9,11,19],familaris:23,famili:[3,4],fast:19,featur:22,feel:[14,23],figur:22,file:[3,4,9,12,13,14,19,23,24],filestem:5,filesystem:5,find:[21,23],fit:23,fix:[14,23],flag:[3,9,14,19],flags_from_listen:3,flags_from_transport:9,flake8:24,fly:[9,14,20],folder:19,follow:[14,16,19,23],fork:[5,13,23],format:[1,12,14,19],formatt:12,found:[9,19],free:[14,23],friendli:19,from:[3,4,5,7,9,12,13,14,18,19,21,23,24],fulli:[12,14],furnish:23,further:14,futur:23,gcm:14,gener:[9,11],generate_serv:11,get:[3,9,14,19,22],get_auth_memb:9,get_help_memb:9,get_vers:12,getfqdn:12,getgrgid:3,getmemb:3,getpass:3,getus:3,gg:[2,3,4,9,13],gid:13,git:23,github:[23,24],give:[14,19],given:[14,21],global:14,go:[9,10,13],goe:[9,10],goodby:18,gr_name:3,grant:23,greet:9,greylist:24,group:[3,4,14,22],grp:3,guid:23,h:19,ha:[14,19,21,23],hackawai:23,had:14,handl:[2,3,5,9,13,19,22],handler:9,have:[3,9,10,14,19,23],header:[9,14,19,21],heartbeat:[2,13],hellman:[3,4,14,19],helo:[9,12,14,22,24],help:[1,9,14,19,22,24],help_auth:9,help_data:9,help_ehlo:9,help_etrn:9,help_expn:9,help_helo:9,help_mail:9,help_noop:9,help_quit:9,help_rcpt:9,help_rset:9,help_unknown:9,help_verb:9,help_vrfi:9,helper:10,here:19,herebi:23,high:[9,10,14],higher:3,holden:[9,16],holder:23,home:19,honeypot:22,hood:19,host:3,how:[3,9,14,19,20,21,22,23],html:[2,3,4,9,13,14],http:[2,3,4,9,13,14,19,24],huge:14,i:[3,9,14,19,23,24],iana:19,id:[9,12,18,19,24],idx:[2,13],ignor:[3,14],imap4:14,imap:24,impact:14,implement:[9,14,19,24],impli:23,improv:[14,19,23,24],includ:[4,9,12,14,19,20,23],incom:[3,19],incorrectli:4,increas:[9,10],inect:24,inform:[13,14,19,23],init:[14,22],inject:24,inspect:3,instal:22,instanc:[2,4,12,20],instead:[21,23],instruct:13,insuffici:18,integ:3,interfac:24,intern:[2,9,11,14],introduc:[14,19],introspect:3,invalid:[3,9,14,16],inwhich:4,io:[9,16,18],ipv4:[3,14,19],ipv6:[3,14,19],is_connect:10,isort:24,issu:14,itself:[9,13],jim:[9,16],job:14,just:[3,21],kamal:[9,16],kawahara:[9,16],kb:[3,14,19],keep:[9,10],kei:[3,4,9,16,19],kernel:14,kill:[2,13],kill_child:13,kind:23,known:19,kovac:[9,16],kristin:[9,16],kura:[2,3,4,9,13,19,23,24],kwarg:[2,3,5,10,11],kx:14,l:19,lag:19,larg:14,last:3,latest:23,lauren:[9,16],least:[3,23],less:[4,14,19],let:14,letmein:[9,15],level:24,lf:18,liabil:23,liabl:23,librari:[14,19],libuv1:19,libuv:19,licens:22,liesmith:[9,16],like:[12,14,22,23],limit:23,line:[3,4,9,14,22],linux:19,list1:9,list2:9,list3:9,list:[2,3,9,14,19,20,22,23,24],listen:[3,4,11,14,22],ll:[13,23],load:[3,4,14],load_dh_param:[4,24],loadabl:24,local:18,log:[0,3,22,24],login:[9,14,18,20,22],longer:[14,19],look:[9,14],lookup_auth_handl:9,lookup_handl:9,lookup_help_handl:9,lookup_verb_handl:9,loop:[1,9,10,11,13,19],lose:4,lost:[9,10],lot:[14,23],low:[9,10,16],lower:[3,9,10],ls:[4,14,19],m:14,mac:14,machin:[18,23],made:10,magic:3,mai:19,mail:[9,14,16,19,22,24],mailbox:18,mailnam:12,mailname_fil:12,maintain:2,make:[14,19,21,23,24],makefil:23,man:1,manag:[2,9,11,13],mani:[3,14,19],manual:23,map:11,mark:[2,9,10],master:19,max:[3,9,14,24],max_messag:3,max_message_s:[3,22],maximum:[3,9,14,19],md5:[9,14,18,20,22],me:14,mean:19,meant:14,mecham:9,mechan:[9,14,24],merchant:23,merg:23,messag:[2,3,8,9,12,13,14,18,19,21,22],message_id:12,method:[3,9,14,24],min:24,mind:22,minimum:19,misspel:14,mit:23,mitig:[14,19],mode:[3,9,14,22,24],modern:14,modif:14,modifi:[4,20,23],modul:[3,7,14,24],monitor:11,more:[3,9,10,14,19,21,24],most:[9,10,24],mostli:14,move:[14,24],mozilla:14,msg:[9,18],mta:22,much:[14,23],multipl:[3,18,19],must:[3,4,9,10],mv:19,n:24,nagata:[9,16],name:[3,12,16,18,19,23],namespac:[3,7],naomi:[9,16],need:[9,10,14,19,23],neither:9,nine:14,non:14,none:[3,4,5,9,10,13,19,22],noninfring:23,noop:[9,22],note:[9,10],noth:11,notic:23,now:[14,23],number:[3,14,19],object:[3,4,5,9,13],obtain:23,occur:[1,4],off:[5,9,13],offici:14,offlin:14,ok:[9,17,18],old:14,omit:4,onc:[9,10,19,23],one:3,onli:[3,9,10,14,19],onward:19,op_cipher_server_prefer:[4,14],op_no_compress:[4,14],op_no_sslv2:4,op_no_sslv3:4,op_single_dh_us:[4,14,19],op_single_ecdh_us:[4,14,19],open:[11,12],oper:3,option:[3,4,9,14,15,18,22],order:24,org:[14,19],origin:19,ortega:[9,16],os:[1,3,4,5,11],other:[9,14,21,23],otherwis:23,out:[3,14,21,23,24],output:[12,19],over:[9,10,13,19],overhaul:14,overhead:[14,19],overrid:19,overridden:9,overriden:24,overview:22,owner:19,ownership:4,packag:19,page:[14,23],pair:[9,10],parallelis:23,paramet:[3,4,7,9,12,13,14,19,22],pars:[3,7,14,19],parse_cmd_arg:3,part:[3,9,16,20,23],parti:14,particular:[14,23,24],pass:[9,14,15,16,17,19,20,24],password:3,past:23,path:[3,12,19],paus:[9,10,23],pause_writ:[9,10],pde0nje5mza1otywms4ymdq5ljeymz:15,pde0nje5mza1otywms4ymdq5ljeymzi4nte2:9,pem:19,pep257:23,pep8:23,per:[3,14,19],perform:[19,22,23],period:3,permiss:[1,3,4,23],permit:23,person:23,pid:[3,4,5,14,19],pid_permiss:4,pidfil:[3,14,22,24],piec:23,ping:[2,8,13],pip:[19,23],pipe:[13,22],pipelin:[18,24],place:[14,19],plain:[9,14,18,20,22],plan:22,pleas:23,poly1305:14,pong:[2,8,13],pop3:14,pop:24,port:[3,4,14,19],portion:23,possibl:[4,19,23],potenti:14,prefer:12,pretti:[14,23],primari:19,print:1,privat:19,privileg:[4,14,19],probabl:22,problem:3,proc:5,procedur:14,process:[2,3,5,8,9,11,13,14,18,19,21,22],process_head:9,processor:3,program:[1,19],progress:24,project:[19,23],properli:[14,24],properti:[3,5,9],protocol:[0,2,9,10,13,14,22],provid:[1,2,3,4,5,9,10,11,12,13,19,23],ps:19,publish:23,pull:22,purpos:23,push:9,put:14,py:23,pypi:[14,22],pypy3:14,pytest:24,python3:19,python:[14,19,22,23],q:19,qualifi:12,quellcrist:[9,16],queu:18,queue:18,quiet:14,quit:[9,22,23],quot:3,r:24,rais:[1,3,4,5,11,12],random:[3,18,19],randomli:[22,24],rang:[3,19,22,24],rather:14,rc:22,rcpt:[9,22,24],re:[4,9,14,18,23],reach:[9,10,19],read:[5,9,12,13,14,23],readabl:3,reader:13,realli:[19,23],reboot:19,receiv:[9,10,13,22],recognis:19,reduc:[14,19],refactor:14,refus:14,reileen:[9,16],reintroduc:14,relat:14,releas:23,reli:23,relianc:14,remov:[2,13,14],replac:19,repons:9,report:23,repositori:23,request:[9,13,18,20,22],requir:[11,13,14,19,20,22],reset:14,resolv:14,respect:[11,13,19],respond:[3,9,16,17,20,21],respons:[3,4,9,11,13,14,17,19,21,22,24],response_from_mod:9,restart:[13,14],restart_child:13,restrict:[9,23],resum:[9,10],resume_writ:[9,10],retain:14,retriev:5,review:[14,19],rfc:12,right:23,risk:[14,19],rn:9,root:[14,19],rsa:14,rset:[9,22],rule:14,run:[1,11,14,19,22],runtim:6,runtimeerror:10,s:[2,5,9,10,11,13,14,19,22,23],same:[3,18,19],saniti:3,scale:14,schema:[2,13],scope:3,script:22,second:[3,9,13,19,21,24],section:[14,21,23],secur:[3,4,14,19],see:[9,10,14],self:[3,6,14],sell:23,send:[9,14,18,19,21],sender:24,sendmail:18,sent:19,separ:[3,14,24],server:[1,2,3,4,9,14,18,19,23,24],server_side_tl:14,servic:[3,19,21],set:[3,6,13,14,19,22],setgid:4,setproctitl:[14,22],setuid:4,setup:23,setup_child:13,sever:16,sha256:14,sha384:14,shadow:[9,16],shall:23,should:[11,14,22,23],show:19,shutdown:[13,14],signal:[11,19],silent:14,similar:23,simpl:[19,23],simpli:14,simul:19,singl:[3,13,19],singleton:12,size:[3,9,10,14,19],sleep:[13,23],slightli:14,small:14,smtp:[0,14,18,19,22,24],smtp_ssl:18,smtplib:18,smtputf8:18,so:[3,13,14,19,23],so_reuseport:14,sock:[2,13],socket:[3,4,11,12,14,24],softwar:23,some:[3,9,14,16,18,20,22],sort:22,sourc:[1,2,3,4,5,6,7,9,10,11,12,13,22],space:[3,9],spawn:[2,3,11,13,14,19],special:24,specif:[14,19,22],specifi:[3,9,14,18,19,20],spefici:14,spf:24,split:9,squash:14,ssl:[3,4,14,18,19],sslcontext:4,start:[1,2,11,13,18,19,22,24],start_work:11,starttl:[9,14,22,23],statement:[14,22],statu:14,still:14,stop:[2,4,11,13],stop_work:11,storag:18,store:3,str:[3,4,9,12],stream:[0,22],streamprotocol:10,streamread:[10,13],streamwrit:13,strictli:[9,10],string:12,strip:[3,24],strong:14,structur:3,style:[1,23],subject:[18,21,23],sublicens:23,submiss:[14,19,24],submit:22,subsequ:[9,10],substanti:23,succe:20,success:[5,9,15],sudo:19,suit:[14,23],suitabl:12,supervisor:[0,2,3,13,14,19,22],suppi:23,support:[3,14,19,22,23,24],suppress:[14,19],sure:[19,23],syntax:[14,15,16,17,18,19],system:[3,14,18,24],systemexit:[1,3,4,5,11,14],t:[4,19],tag:14,take:[14,23],taken:[14,18],takeshi:[9,16],tandum:3,tarbal:23,target:[14,23],task:23,tb:6,tell:[16,17,20,21,22],tendenc:14,term:22,termin:[11,12,13,19],tese:14,test:[3,9,14,16,18,19,21,24],test_:3,test_delai:3,test_dynamic_switch:3,test_group:3,test_ipv6_support:3,test_max_message_s:3,test_mod:3,test_no_listen:3,test_pidfil:3,test_port:3,test_same_listen:3,test_timeout:3,test_tls_dhparam:3,test_tls_ipv6_support:3,test_tls_port:3,test_tls_set:3,test_us:3,test_work:3,than:[3,9,10,14],thei:[3,4,9,11,13,14,19,20,21],them:[3,16,24],thi:[2,3,9,10,13,14,18,19,21,23],thing:[9,10,22,24],think:[22,23],third:14,those:[19,22],three:[16,21],through:[9,10,23],tie:9,time:[9,19,22],timeout:[3,9,22],tini:14,tl:[3,4,11,14,18,19,24],tld:[9,14,17,18],tls_cert:[3,22],tls_dhparam:[3,14,22],tls_kei:[3,22],tls_listen:[3,14,22],tlsv1:14,tmp:[3,19],todo:[14,22,23],togeth:19,too:9,top:[14,22],tort:23,total:14,tox:[14,23],track:19,tracker:14,transfer:22,transport:[9,10],travi:[14,23],tree:24,trigger:[9,14,20],tset:18,tsl:14,two:[14,22],txt:19,type:[3,4,5,9,12],typo:14,ubuntu:[14,19],uid:13,unabl:18,unavail:[14,18],under:[19,23],underlin:12,understand:23,unix:3,unknown:[9,17],unless:[4,15,19],unlik:24,unpack:23,unsuccess:5,until:[9,10,14,19,23],up:[9,19],up_read:2,up_writ:13,upcom:22,updat:[13,14,19],us:[2,3,4,8,9,12,13,14,16,18,22,23],use_tl:[4,11],usecas:14,user:[3,4,9,14,17,18,24],utf:18,util:[0,14,22],utilis:[2,22],uvloop:[14,22],v:19,valid:[3,9,19],validate_opt:3,valu:[2,3,9,13,19],varieti:23,variou:19,ve:23,verb:[9,14,16,19,20,22,24],veri:23,verifi:3,version:[12,14,19,23],via:[2,11,19,22,23],vidaura:[9,16],view:23,violat:14,virginia:[9,16],virtualenv:19,vrfy:[9,18,20,22],vxnlcm5hbwu6:[9,15],wa:[12,14],wai:[14,16,19,23],wait:[9,13,14,19],want:14,warn:[3,14,19],warn_opt:3,warranti:23,water:[9,10],we:[3,13,18],wealth:23,wednesdai:[9,16],well:[3,19],were:[9,10,14],what:[19,20,21,23],whatev:14,when:[1,3,4,5,9,10,12,14,19,23],whether:[3,4,23],which:[3,4,14,23],whom:23,wiki:14,wish:23,with_traceback:6,within:3,without:[9,10,12,14,18,19,20,21,22,23],work:[14,19,23],worker:[0,2,3,8,11,14,22],would:[9,10,14,19],wrap:19,wrapper:[4,9],write:[9,10,13,19,22],write_eof:9,writer:13,written:[3,14,23],www:19,x01:[2,8,13],x02:[2,8,13],x509:19,x:[9,19,21],yield:[9,10],you:[3,4,14,15,16,17,18,20,21,22,23],your:[18,23],your_distro:19,yourself:[14,23],zero:[9,10]},titles:["API","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.application</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.child</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.config</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.control</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.daemon</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.exceptions</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.logs</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.protocols</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.smtp</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.streams</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.supervisor</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.utils</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">blackhole.worker</span></code>","Changelog","AUTH","EXPN","VRFY","Communicating with Blackhole","Configuration","Dynamic responses","Dynamic Switches","Blackhole  ","Overview","TODO"],titleterms:{"0":14,"1":14,"10":14,"11":14,"12":14,"13":14,"14":14,"15":14,"16":14,"2":14,"3":14,"4":14,"5":14,"6":14,"7":14,"8":14,"9":14,"do":23,"switch":21,With:18,accept:18,all:16,amount:21,an:16,api:0,applic:1,argument:16,auth:15,befor:23,blackhol:[1,2,3,4,5,6,7,8,9,10,11,12,13,18,22],bodi:18,bounc:18,branch:22,build:[22,23],changelog:[14,23],child:2,code:[18,23],combin:21,command:[18,19],commun:18,config:3,configur:19,contribut:23,control:4,coverag:22,cram:15,current:14,d:19,daemon:5,data:18,delai:[19,21],document:23,dynam:[20,21],dynamic_switch:19,ehlo:18,etrn:18,except:6,expn:16,fail:15,featur:[14,19,23,24],futur:24,get:23,group:19,guid:22,helo:18,help:18,init:19,instal:[19,23],licens:23,line:19,list1:16,list2:16,list3:16,list:16,listen:19,log:7,login:15,mail:18,master:22,max_message_s:19,md5:15,mode:[19,21],noop:18,option:19,overview:23,paramet:18,past:14,pidfil:19,plain:15,plan:[14,23],possibl:24,probabl:19,protocol:8,pull:23,pypi:23,python:18,quit:18,rang:21,rc:19,rcpt:18,releas:14,request:23,requir:23,respons:[18,20],rset:18,run:23,script:19,set:21,setproctitl:19,should:19,size:18,smtp:9,some:23,sourc:23,start:23,starttl:19,statu:22,stream:10,submit:23,succe:15,supervisor:11,support:18,test:[22,23],thing:23,time:21,timeout:19,tls_cert:19,tls_dhparam:19,tls_kei:19,tls_listen:19,todo:24,upcom:[14,23],us:[19,21],user:[19,22],util:12,uvloop:19,verb:18,vrfy:17,without:16,worker:[13,19],write:23,you:19}})