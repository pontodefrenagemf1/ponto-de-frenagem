import time
import requests
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/mapa')
def mapa():
    with open('live-tracker.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

def background_f1_live_api():
    while True:
        try:
            # Endereço da API oficial de cronometragem da F1
            url = "https://livetiming.formula1.com/static/SessionInfo.json"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Aqui você processa os dados reais que vieram da API oficial
                # Como o formato muda dependendo se a sessão está ativa, vamos garantir a exibição:
                
                # Exemplo de renderização baseada na resposta real da API
                html_rows = f"""
                <div class="driver-row" style="border-left-color: #e10600;">
                    <span class="pos">1</span>
                    <div class="team-color-bar" style="background-color: #e10600;"></div>
                    <span class="sigla"><strong>Sessão Ativa: {data.get('Meeting', {}).get('Name', 'F1')}</strong></span>
                    <span class="gap">AO VIVO</span>
                </div>
                """
                socketio.emit('update_f1', {'html_rows': html_rows})
            
        except Exception as e:
            print("Aguardando feed oficial da sessão...", e)
            
        time.sleep(5)

if __name__ == '__main__':
    import threading
    threading.Thread(target=background_f1_live_api, daemon=True).start()
    
    print("\n[SERVIDOR ATUALIZADO] Abra no seu navegador: http://localhost:5000/mapa\n")
    socketio.run(app, debug=True, port=5000)