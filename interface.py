import main
import cgi
from wsgiref.simple_server import make_server
import webbrowser
import access
from urllib.parse import parse_qs

port = 8080
website = "http://localhost:"+str(port)
begin = '''<html>
<head>
	<title>Search Page</title>
	<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>'''

end = '''</body>
<script>
var xhttp = new XMLHttpRequest();
var timeOut;
xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("suggestions").innerHTML = this.responseText;
    }
  };
function fill(sug){
var text = sug.innerHTML
el = document.getElementById('searchInput');
el.value = text;
getsuggestion();
}
function getsuggestion(){
clearTimeout(timeOut);
timeOut = setTimeout( function(){
el = document.getElementById('searchInput');
stype = document.getElementById('searchType').value;
ctype = document.getElementById('collectionType').value;
encoded = encodeURI(el.value)
xhttp.open("POST", "", true);
xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhttp.send("query="+encoded+"&collectionType="+ctype+"&searchType="+stype);
}, 1000);
document.getElementById("suggestions").innerHTML = 'Loading...'
}

function expand(el){
var text = el.innerHTML
el = document.getElementById('searchInput');
el.value = text;
document.getElementById('mainSearch').submit()
}

function toggleRelevance(el){
id = el.id;
query = document.getElementById('searchInput').value;
encoded = encodeURI(query)
var xhttp = new XMLHttpRequest();
xhttp.open("POST", "", true);
xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhttp.send("relevantquery="+encoded+"&id="+id);

if(el.className == 'unmark'){
el.className = 'mark'
el.innerHTML = 'Mark Relevant'
}else{
el.className = 'unmark'
el.innerHTML = 'Unmark Relevant'
}
}

function clr(){
clearTimeout(timeOut);
}
</script>
</html>'''


def search_bar(query='', type=None, coll=None, spell=False):
    expansion = None
    didYouMean = ''
    if spell:
        potential = main.Query(query, coll, type).checkSpelling()
        if potential != query:
            didYouMean = '''<p>Did You Mean:</p><p onclick="expand(this)" id='correction'>%s</p>''' % (potential)
    if query is not '':
        expansion = main.globalExpand(query)
    suggestion = '''<h2>Suggestions</h2><p onclick="expand(this)" id='expansion'>%s</p>''' % (expansion) if expansion else ''
    bar = '''<h1 id="title">Searchify</h1>
<form id="mainSearch" class="formInline" method="get" action="" onsubmit="clr()">
<div id='searchdiv'>
	<input autocomplete="off" id='searchInput' list="suggestions" oninput="getsuggestion()" class = "searchBar" type="text" name="query" value="%s" placeholder="Enter a Search Query">
	<div id="suggestions">
    </div>
	<input class = "searchButton" type="submit" value="Search">
</div>
<div class="selections">
<select id="searchType" class='selection' name="searchType">
    <option value="boolean">Boolean Model</option>
    <option value="vsm">Vector Space Model</option>
</select>
<select id="collectionType" class='selection' name="collectionType">
    <option value="uofo">UofO Corpus</option>
    <option value="reuters">Reuters</option>
    </select>
</div>
</form>
''' % query
    return bar+suggestion+didYouMean


def get_content_type(pathInfo):
    if pathInfo.endswith(".css"):
        return "text/css"
    else:
        return "text/html"


def read_static_content(filename):
    with open('.'+filename, 'r') as f:
        return f.read()


def app(environ, start_response):
    if get_content_type(environ['PATH_INFO']) == "text/css":
        response = read_static_content(environ['PATH_INFO'])
    else:
        response = ''
        if environ['REQUEST_METHOD'] == 'POST':
            response += post(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'GET':
            response = begin
            response += get(environ, start_response)
            response += end
    start_response(
        '200 OK', [('Content-Type', get_content_type(environ['PATH_INFO']))])
    return [response.encode("utf-8")]


def get(env, resp):
    if env['QUERY_STRING'] == '':
        return search_bar()
    else:
        formData = cgi.FieldStorage(fp=env['wsgi.input'],
                                    environ=env,
                                    keep_blank_values=True)
        if 'query' in formData:
            query = formData['query'].value
            type = formData['searchType'].value
            coll = formData['collectionType'].value
            return search_bar(query, type, coll, spell=True)+generate_results(query, type, coll)

        if 'title' in formData:
            title = formData['title'].value
            coll = formData['collectionType'].value
            return generateContent(title, coll)


def generateContent(title, coll):
    cont = access.getDocContent(title, coll)
    return "<h2>%s | %s</h2><div>%s</div>" % (cont[access.ID], cont[access.TITLE], cont[access.FULL])

def post(env, resp):
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = env['wsgi.input'].read(request_body_size)
    post = parse_qs(request_body)
    if b'query' in post:
        return generateSuggestions(post[b'query'][0].decode("utf-8"), post[b'collectionType'][0].decode("utf-8"), post[b'searchType'][0].decode("utf-8"))
    elif b'relevantquery' in post:
        query = post[b'relevantquery'][0].decode("utf-8")
        id = post[b'id'][0].decode("utf-8")
        main.toggleRelevance(query, id)
    return ''

def generateSuggestions(query, coll, type):
    sugs = main.complete(query, coll, type)
    suggestions = ''
    for data in sugs:
        suggestions += '<div class="aSuggest" onclick="fill(this)">'+query.strip()+' '+data+'</div>'
    return suggestions

def generate_results(query, type, coll):
    idList = main.query(query, coll, type)
    result = access.getAllDocs(idList, coll, type)
    resultclass = "aResult"
    resulttitle = resultclass+"_title"
    resultcontent = resultclass + "_content"
    resultdiv = resultclass + "_div"

    html = "<div class='%s'>" % resultclass
    relevantToggle = '''<div onclick='toggleRelevance(this)' id='%s' class='%s'>%s</div>'''

    for item in result:
        rel = main.isRelevant(query, item[access.ID])
        relevantButton = relevantToggle % (item[access.ID], 'unmark' if rel else 'mark', 'Unmark Relevant' if rel else 'Mark Relevant')
        link = '?title='+item[access.ID]+'&collectionType='+coll
        itemHtml = '''<a href='%s'><div class='%s' >
                   <h2 class='%s'> %s </h2>
                   <p class='%s'> %s </p>
                   </div></a>''' % (link, resultdiv, resulttitle,
                                   item[access.TITLE], resultcontent, item[access.EX])
        itemHtml = '<div class="resultContainer">'+itemHtml+relevantButton+'</div>'
        html += itemHtml
    return html + '</div>'


def start():
    webbrowser.open_new(website)
    try:
        httpd = make_server('', port, app)
        print('Serving on port', port, 'open', website)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
