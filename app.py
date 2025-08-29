import requests
from datetime import datetime, timedelta
from urllib.parse import quote
from flask import Flask, request, jsonify, render_template
import webbrowser
import threading
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")
REGION = 'europe'
PLATFORM = 'euw1'

def handle_http_error(resp):
    """Verbesserte Fehlerbehandlung für Riot API"""
    if resp.status_code == 403:
        raise Exception("API-Key abgelaufen oder ungültig. Bitte auf https://developer.riotgames.com/ neu generieren.")
    elif resp.status_code == 404:
        raise Exception("Spieler nicht gefunden. Bitte Riot ID überprüfen.")
    elif resp.status_code == 429:
        raise Exception("Rate Limit erreicht. Bitte warten.")
    elif resp.status_code == 401:
        raise Exception("Nicht autorisiert. API-Key ungültig.")
    elif not resp.ok:
        raise Exception(f"API Error {resp.status_code}: {resp.text}")

def get_puuid(game_name, tag_line):
    """Hole PUUID für Riot ID"""
    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    headers = {"X-Riot-Token": API_KEY}
    resp = requests.get(url, headers=headers)
    handle_http_error(resp)
    data = resp.json()
    return {
        'puuid': data['puuid'],
        'gameName': data['gameName'],
        'tagLine': data['tagLine']
    }

def get_summoner_info(puuid):
    """Hole Summoner Informationen"""
    url = f"https://{PLATFORM}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": API_KEY}
    resp = requests.get(url, headers=headers)
    handle_http_error(resp)
    return resp.json()

def get_last_matches(puuid, count=5):
    """Hole letzte Match IDs"""
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    headers = {"X-Riot-Token": API_KEY}
    resp = requests.get(url, headers=headers, params={'count': count})
    handle_http_error(resp)
    return resp.json()

def get_match_details(match_id):
    """Hole Match Details"""
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    resp = requests.get(url, headers=headers)
    handle_http_error(resp)
    return resp.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/last-matches")
def last_matches():
    game_name = request.args.get("gameName")
    tag_line = request.args.get("tagLine")
    
    print(f"DEBUG: Request for {game_name}#{tag_line}")
    
    if not game_name or not tag_line:
        return jsonify({"error": "Fehlende Parameter gameName oder tagLine"}), 400
    
    try:
        # Account Info abrufen (gibt puuid, gameName und tagLine zurück)
        account_info = get_puuid(game_name, tag_line)
        puuid = account_info['puuid']
        actual_game_name = account_info['gameName']
        
        # Summoner Info abrufen (gibt summoner details zurück)
        summoner_info = get_summoner_info(puuid)
        summoner_icon = f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{summoner_info['profileIconId']}.png"
        summoner_level = summoner_info["summonerLevel"]

        # Letzte Matches abrufen
        match_ids = get_last_matches(puuid, 5)
        if not match_ids:
            return jsonify({
                "summoner": {
                    "name": actual_game_name,
                    "level": summoner_level,
                    "icon": summoner_icon
                }, 
                "matches": [], 
                "message": "Keine Matches gefunden"
            })
        
        # Match Details sammeln
        matches = []
        latest_time_ago = None
        
        for match_id in match_ids:
            try:
                match = get_match_details(match_id)
                info = match["info"]
                game_start = datetime.utcfromtimestamp(info["gameStartTimestamp"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                duration = str(timedelta(seconds=info["gameDuration"]))
                
                # Finde den Spieler in Participants
                participant = next((p for p in info["participants"] if p["puuid"] == puuid), None)
                champion = participant["championName"] if participant else "Unbekannt"
                champion_id = participant["championId"] if participant else 0
                queue_id = info["queueId"]
                
                # Champion Icon URL erstellen
                champion_icon = f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/{champion.replace(' ', '')}.png"
                
                matches.append({
                    "match_id": match_id,
                    "game_start": game_start,
                    "duration": duration,
                    "champion": champion,
                    "champion_icon": champion_icon,
                    "queue_id": queue_id
                })
                
            except Exception as e:
                print(f"Fehler bei Match {match_id}: {e}")
                matches.append({
                    "match_id": match_id,
                    "game_start": "Fehler",
                    "duration": "Fehler",
                    "champion": "Fehler beim Laden",
                    "champion_icon": "",
                    "queue_id": 0
                })

        # Berechne die Zeit seit dem letzten Spiel
        if matches:
            now = datetime.utcnow()
            first_game_start_str = matches[0]["game_start"]
            first_game_start_dt = datetime.strptime(first_game_start_str, "%Y-%m-%d %H:%M:%S")
            time_since = now - first_game_start_dt
            
            days = time_since.days
            hours = time_since.seconds // 3600
            minutes = (time_since.seconds % 3600) // 60
            
            # Formatierung der Zeitangabe
            time_parts = []
            if days > 0:
                time_parts.append(f"{days} Tag{'e' if days > 1 else ''}")
            if hours > 0:
                time_parts.append(f"{hours} Stunde{'n' if hours > 1 else ''}")
            if minutes > 0:
                time_parts.append(f"{minutes} Minute{'n' if minutes > 1 else ''}")
            
            if time_parts:
                latest_time_ago = f"{' '.join(time_parts)} her"
            else:
                latest_time_ago = "weniger als eine Minute her"

        return jsonify({
            "summoner": {
                "name": actual_game_name,
                "level": summoner_level,
                "icon": summoner_icon
            },
            "matches": matches,
            "latest_time_ago": latest_time_ago
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

def open_browser():
    """Öffne Browser nach kurzer Verzögerung"""
    time.sleep(1.5)
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Prüfe API-Key
    if not API_KEY or not API_KEY.startswith("RGAPI-"):
        print("❌ WARNUNG: API-Key fehlt oder ist ungültig.")
        print("Bitte generiere einen neuen Key auf https://developer.riotgames.com/")
    
    # Nur für lokale Entwicklung den Browser öffnen
    import os
    if not os.environ.get('RENDER'):  # Render.com setzt diese Umgebungsvariable
        threading.Thread(target=open_browser, daemon=True).start()
        print("🚀 Server starting on http://127.0.0.1:5000")
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    else:
        # Für Production auf Render.com
        app.run(debug=False, host='0.0.0.0', port=5000)