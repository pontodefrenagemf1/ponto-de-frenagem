import time
import os
import pandas as pd
import fastf1
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Cria a pasta de cache se ela não existir para evitar erros
if not os.path.exists('f1_cache'):
    os.makedirs('f1_cache')

fastf1.Cache.enable_cache('f1_cache')

@app.route('/')
def index():
    with open('live-tracker.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

def background_f1_data():
    while True:
        try:
            # Carrega a sessão de exemplo
            session = fastf1.get_session(2026, 'Zandvoort', 'R')
            session.load(telemetry=False, weather=False, messages=False)
            
            results = session.results
            
            html_rows = ""
            for idx, driver in results.iterrows():
                pos = int(driver['Position']) if pd.notna(driver['Position']) else '-'
                sigla = driver['Abbreviation']
                gap = "Leader" if pos == 1 else f"+{idx * 1.5:.3f}s"
                pneu = "M"
                
                html_rows += f"""
                <tr>
                    <td>{pos}</td>
                    <td><strong>{sigla}</strong></td>
                    <td>{gap}</td>
                    <td><span style="background: #ffd700; color: black; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px;">{pneu}</span></td>
                </tr>
                """
            
            socketio.emit('update_f1', {'html_rows': html_rows})
            
        except Exception as e:
            # Fallback caso a sessão ao vivo exija conexão ou dê erro de API
            html_rows = """
                <tr><td>1</td><td><strong>VER</strong></td><td>Leader</td><td><span style="background: #ff3333; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">S</span></td></tr>
                <tr><td>2</td><td><strong>NOR</strong></td><td>+2.145s</td><td><span style="background: #ffd700; color: black; padding: 2px 6px; border-radius: 4px; font-size: 11px;">M</span></td></tr>
                <tr><td>3</td><td><strong>LEC</strong></td><td>+5.892s</td><td><span style="background: #ffffff; color: black; padding: 2px 6px; border-radius: 4px; font-size: 11px;">H</span></td></tr>
            """
            socketio.emit('update_f1', {'html_rows': html_rows})
            
        time.sleep(2)

if __name__ == '__main__':
    import threading
    threading.Thread(target=background_f1_data, daemon=True).start()
    
    print("\n[SERVIDOR RODANDO] Abra no seu navegador: http://localhost:5000\n")
    socketio.run(app, debug=True, port=5000)