from django.shortcuts import render
import requests
from django.core.cache import cache
from requests.exceptions import RequestException

API_KEY = '7c3cfa3f3f0f99ef146ff6c3fc75dddb'  # Substitua pela sua chave de API

# Função para obter o clima atual
def get_weather(city):
    # Tentando pegar o clima da cache para evitar consultas repetidas
    cache_key = f"weather_{city}"
    cached_weather = cache.get(cache_key)
    
    if cached_weather:
        return cached_weather

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=pt_br'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se a resposta não for 200
        data = response.json()

        # Verifica se a cidade é válida e se os dados são corretos
        if data['cod'] == 200:
            weather = {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind': data['wind']['speed'],
            }
            # Armazenando o resultado na cache por 15 minutos
            cache.set(cache_key, weather, timeout=60*15)
            return weather
        else:
            return {'error': 'Cidade não encontrada!'}
    
    except RequestException as e:
        # Erro na requisição (problemas de rede, servidor da API, etc.)
        return {'error': f"Erro na requisição: {str(e)}"}
    except Exception as e:
        # Erro genérico
        return {'error': f"Ocorreu um erro: {str(e)}"}

# Função para obter a previsão do tempo para os próximos dias
def get_forecast(city):
    # Tentando pegar a previsão da cache para evitar consultas repetidas
    cache_key = f"forecast_{city}"
    cached_forecast = cache.get(cache_key)
    
    if cached_forecast:
        return cached_forecast

    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=pt_br'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se a resposta não for 200
        data = response.json()

        if data['cod'] == '200':
            forecast = []
            for item in data['list']:
                forecast.append({
                    'date': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'],
                })
            # Armazenando a previsão na cache por 15 minutos
            cache.set(cache_key, forecast, timeout=60*15)
            return forecast
        else:
            return {'error': 'Não foi possível obter a previsão.'}
    except Exception as e:
        return {'error': f"Ocorreu um erro na previsão: {str(e)}"}

# Função principal para a view
def home(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        weather = get_weather(city)
        forecast = get_forecast(city)

        # Se houver erro, renderize com o erro
        if 'error' in weather:
            return render(request, 'clima/home.html', {'error': weather['error']})
        elif weather:
            return render(request, 'clima/home.html', {'weather': weather, 'forecast': forecast})
        else:
            return render(request, 'clima/home.html', {'error': 'Cidade não encontrada!'})
    
    return render(request, 'clima/home.html')