KEY_OFFSETS = {
    "ESC":7,
    "F1":13,"F2":16,"F3":19,"F4":22,"F5":28,"F6":31,"F7":34,"F8":37,
    "F9":40,"F10":43,"F11":46,"F12":49,"PRT":52,"SCR":55,"PAUSE":58,

    "~":83,"1":86,"2":89,"3":92,"4":95,"5":98,"6":101,"7":104,
    "8":107,"9":110,"0":113,"-":116,"=":119,"BACKSPACE":135,
    "INS":138,"HOME":141,"PGUP":144,

    "TAB":159,"Q":162,"W":165,"E":168,"R":171,"T":174,"Y":177,
    "U":180,"I":183,"O":186,"P":199,"[":202,"]":205,"\\":211,
    "DEL":214,"END":217,"PGDN":220,

    "CAPS":235,"A":241,"S":244,"D":247,"F":250,"G":263,"H":266,
    "J":269,"K":272,"L":275,";":278,"'":281,"ENTER":287,

    "LSHIFT":311,"Z":327,"X":330,"C":333,"V":336,"B":339,"N":342,
    "M":345,",":348,".":351,"/":354,"RSHIFT":363,"UP":369,

    "LCTRL":397,"WIN":400,"LALT":403,"SPACE":415,"RALT":427,"FN":430,
    "PRINT":433,"RCTRL":436,"LEFT":442,"DOWN":455,"RIGHT":458,

    "NUMLOCK":147,"NUM_DIV":150,"NUM_MUL":153,"NUM_MINUS":156,
    "NUM7":223,"NUM8":226,"NUM9":229,"NUM_PLUS":232,
    "NUM4":299,"NUM5":302,"NUM6":305,
    "NUM1":375,"NUM2":378,"NUM3":391,"NUM_ENTER":394,
    "NUM0":461,"NUM_DOT":467,
}

KEY_GEOMETRY = {}
def _add(n,x,y,w=1,h=1):
    KEY_GEOMETRY[n]=(float(x),float(y),float(w),float(h))

_add("ESC",0,0)
for i,n in enumerate(["F1","F2","F3","F4"]): _add(n,2+i,0)
for i,n in enumerate(["F5","F6","F7","F8"]): _add(n,6.5+i,0)
for i,n in enumerate(["F9","F10","F11","F12"]): _add(n,11+i,0)
for i,n in enumerate(["PRT","SCR","PAUSE"]): _add(n,15.5+i,0)

x=0
for n in ["~","1","2","3","4","5","6","7","8","9","0","-","="]:
    _add(n,x,1.35); x+=1
_add("BACKSPACE",x,1.35,2)
for i,n in enumerate(["INS","HOME","PGUP"]): _add(n,15.5+i,1.35)
for i,n in enumerate(["NUMLOCK","NUM_DIV","NUM_MUL","NUM_MINUS"]): _add(n,19+i,1.35)

_add("TAB",0,2.35,1.5); x=1.5
for n in ["Q","W","E","R","T","Y","U","I","O","P","[","]"]:
    _add(n,x,2.35); x+=1
_add("\\",x,2.35,1.5)
for i,n in enumerate(["DEL","END","PGDN"]): _add(n,15.5+i,2.35)
for i,n in enumerate(["NUM7","NUM8","NUM9"]): _add(n,19+i,2.35)
_add("NUM_PLUS",22,2.35,1,2)

_add("CAPS",0,3.35,1.75); x=1.75
for n in ["A","S","D","F","G","H","J","K","L",";","'"]:
    _add(n,x,3.35); x+=1
_add("ENTER",x,3.35,2.25)
for i,n in enumerate(["NUM4","NUM5","NUM6"]): _add(n,19+i,3.35)

_add("LSHIFT",0,4.35,2.25); x=2.25
for n in ["Z","X","C","V","B","N","M",",",".","/"]:
    _add(n,x,4.35); x+=1
_add("RSHIFT",x,4.35,2.75)
_add("UP",16.5,4.35)
for i,n in enumerate(["NUM1","NUM2","NUM3"]): _add(n,19+i,4.35)
_add("NUM_ENTER",22,4.35,1,2)

_add("LCTRL",0,5.35,1.25)
_add("WIN",1.25,5.35,1.25)
_add("LALT",2.5,5.35,1.25)
_add("SPACE",3.75,5.35,6.25)
_add("RALT",10,5.35,1.25)
_add("FN",11.25,5.35,1.25)
_add("PRINT",12.5,5.35,1.25)
_add("RCTRL",13.75,5.35,1.25)
_add("LEFT",15.5,5.35)
_add("DOWN",16.5,5.35)
_add("RIGHT",17.5,5.35)
_add("NUM0",19,5.35,2)
_add("NUM_DOT",21,5.35)

MAX_X=max(x+w for x,y,w,h in KEY_GEOMETRY.values())
MAX_Y=max(y+h for x,y,w,h in KEY_GEOMETRY.values())

def center(name):
    x,y,w,h=KEY_GEOMETRY[name]
    return x+w/2,y+h/2

def normalized_center(name):
    x,y=center(name)
    return x/MAX_X,y/MAX_Y

NORMALIZED_CENTERS={
    k: normalized_center(k)
    for k in KEY_OFFSETS
    if k in KEY_GEOMETRY
}

GROUPS = {
    "WASD": {"W","A","S","D"},
    "Arrows": {"UP","DOWN","LEFT","RIGHT"},
    "Numpad": {k for k in KEY_OFFSETS if k.startswith("NUM")},
    "F-row": {"ESC"} | {f"F{i}" for i in range(1,13)},
}
