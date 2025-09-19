from django.shortcuts import render
import requests

def buscar_anime(request):
    query = request.GET.get('q', '')
    contexto = {
        'query': query,
        'resultados': [],
        'erro': None,
    }

    if query:
        api_url = 'https://api.jikan.moe/v4/anime'
        params = {'q': query}

        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
            
            # ADICIONE ESTE PRINT PARA VER A RESPOSTA COMPLETA
            print(f"Dados da API: {dados_api}")
            
            contexto['resultados'] = dados_api.get('data', [])

        except requests.exceptions.RequestException as e:
            contexto['erro'] = f"Ocorreu um erro ao buscar na API: {e}"
            print(contexto['erro'])

    return render(request, 'animes/pagina_de_busca.html', contexto)