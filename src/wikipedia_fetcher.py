import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "SeriesAI/1.0"
}


def resolver_titulo_wikipedia(titulo):
    url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": titulo,
        "redirects": 1,
        "format": "json"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if pages:
        for _, pagina in pages.items():
            if pagina.get("missing"):
                continue
            titulo_resuelto = pagina.get("title")
            if titulo_resuelto:
                return titulo_resuelto
    params = {
        "action": "query",
        "list": "search",
        "srsearch": titulo,
        "srlimit": 1,
        "format": "json"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()
    resultados = data.get("query", {}).get("search", [])
    if resultados:
        return resultados[0].get("title") or titulo
    return titulo


def obtener_secciones(titulo):
    url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": titulo,
        "prop": "sections",
        "format": "json",
        "redirects": 1
    }
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()
    if "error" in data or "parse" not in data:
        raise ValueError(f"No se pudo obtener el articulo de Wikipedia para '{titulo}'.")
    return data["parse"].get("sections", [])


def obtener_contenido_seccion(titulo, indice):
    url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": titulo,
        "prop": "text",
        "section": indice,
        "format": "json",
        "redirects": 1
    }
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()
    if "error" in data or "parse" not in data:
        raise ValueError(f"No se pudo obtener la seccion {indice} de Wikipedia.")
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(separator=" ", strip=True)
    return texto


def obtener_articulo_completo(titulo):
    titulo_resuelto = resolver_titulo_wikipedia(titulo)
    secciones = obtener_secciones(titulo_resuelto)
    articulo = {}
    try:
        resumen = obtener_contenido_seccion(titulo_resuelto, 0)
        if resumen:
            articulo["Resumen"] = resumen
    except Exception:
        pass
    for seccion in secciones:
        nombre = seccion.get("line")
        indice = seccion.get("index")
        if not nombre or not indice:
            continue
        try:
            contenido = obtener_contenido_seccion(titulo_resuelto, indice)
            articulo[nombre] = contenido
        except Exception:
            pass
    return articulo