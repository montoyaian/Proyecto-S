def unir_lista(items, separador=", "):
    if not items:
        return ""
    return separador.join([str(item) for item in items if item])


def construir_documento_serie(datos):
    if not datos:
        return None
    tmdb = datos.get("tmdb", {})
    personajes = datos.get("personajes", [])
    wikipedia = datos.get("wikipedia", {})
    titulo = tmdb.get("titulo") or tmdb.get("titulo_original") or ""
    descripcion = tmdb.get("descripcion") or ""
    generos = unir_lista(tmdb.get("generos", []))
    temporadas = tmdb.get("numero_temporadas")
    episodios = tmdb.get("numero_episodios")
    lista_personajes = unir_lista(personajes)
    secciones = []
    for nombre, contenido in wikipedia.items():
        if contenido:
            secciones.append(f"== {nombre} ==\n{contenido}")
    secciones_texto = "\n\n".join(secciones)
    texto = (
        f"Titulo: {titulo}\n\n"
        f"Descripcion:\n{descripcion}\n\n"
        f"Generos:\n{generos}\n\n"
        f"Personajes:\n{lista_personajes}\n\n"
        f"Temporadas:\n{temporadas}\n\n"
        f"Episodios:\n{episodios}\n\n"
        f"Secciones Wikipedia:\n{secciones_texto}"
    )
    return {
        "id": str(tmdb.get("id")),
        "texto": texto
    }