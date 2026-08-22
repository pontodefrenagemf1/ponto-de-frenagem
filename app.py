import time
import fastf1
import pandas as pd
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Ativa o cache do FastF1 para não estourar o limite de requisições da API
fastf1.Cache.enable_cache('f1_cache') 

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/mapa')
def mapa():
    with open('live-tracker.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

def background_f1_real_data():
    session = None
    last_fetch = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Atualiza os dados da sessão oficial a cada 60 segundos para evitar Rate Limit
            if session is None or (current_time - last_fetch) > 60:
                print("Buscando dados oficiais da sessão F1...")
                # Carrega o treino ou corrida atual (ex: GP da Holanda - Corrida)
                session = fastf1.get_session(2026, 'Dutch Grand Prix', 'R')
                session.load(telemetry=False, weather=False)
                last_fetch = current_time

            # Pega os resultados atuais da sessão
            results = session.results
            
            html_rows = ""
            if not results.empty:
                for idx, row in results.iterrows():
                    pos = int(row['Position']) if pd.notna(row['Position']) else idx + 1
                    sigla = row['Abbreviation']
                    
                    # Trata o tempo / gap
                    time_status = row['Time']
                    if pd.notna(time_status):
                        gap = str(time_status).split('days')[-1].strip() # Formata o tempo
                    else:
                        gap = row['Status']

                    # Define cores baseadas na equipe oficial
                    team_colors = {
                        "Red Bull Racing": "#3671C6", "Ferrari": "#E8002D", 
                        "Mercedes": "#27F4D2", "McLaren": "#FF8700", 
                        "Aston Martin": "#229971", "Williams": "#64C4FF",
                        "Alpine": "#0093CC", "Haas F1 Team": "#B6BABD",
                        "RB": "#6692FF", "Audi": "#E10600", "Cadillac": "#FFFFFF"
                    }
                    cor = team_colors.get(row['TeamName'], "#888888")

                    html_rows += f"""
                    <div class="driver-row" style="border-left-color: {cor};">
                        <span class="pos">{pos}</span>
                        <div class="team-color-bar" style="background-color: {cor};"></div>
                        <span class="sigla"><strong>{sigla}</strong></span>
                        <span class="gap">{gap}</span>
                    </div>
                    """
            else:
                html_rows = "<div style='color: white; text-align:center;'>Aguardando dados da sessão oficial...</div>"

            socketio.emit('update_f1', {'html_rows': html_rows})
            
        except Exception as e:
            print("Aviso ao buscar dados ao vivo:", e)
            
        # Espera 10 segundos antes de reenviar para a tela (mantém o navegador leve)
        time.sleep(10)

if __name__ == '__main__':
    import threading
    threading.Thread(target=background_f1_real_data, daemon=True).start()
    
    print("\n[SERVIDOR RODANDO] Abra no seu navegador: http://localhost:5000/mapa\n")
    socketio.run(app, debug=True, port=5000)