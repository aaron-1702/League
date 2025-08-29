# League Match Tracker

Eine Flask-Webanwendung, die die letzten Spiele eines League of Legends-Spielers anzeigt, basierend auf der Riot Games API.

![League Match Tracker](https://img.shields.io/badge/League-Match%20Tracker-blue?style=for-the-badge&logo=leagueoflegends)

## Funktionen

- Suche nach Spielern über Riot ID (Name#Tag)
- Anzeige der letzten 5 Spiele
- Zeit seit dem letzten Spiel in Tagen, Stunden und Minuten
- Responsives Design mit Tailwind CSS
- Automatische Browser-Öffnung beim Start
- Dark/Light Mode Toggle

## Voraussetzungen

- Python 3.7 oder höher
- Riot Games Developer Account mit API-Key

## Installation

1. Repository klonen:
```bash
git clone https://github.com/aaron-1702/League.git
cd League
```
2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```
3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```
4. Umgebung konfigurieren
```text
RIOT_API_KEY=dein_api_key_hier
```

## Riot API-Key erhalten

1. Gehe zu Riot Developer Portal
2. Erstelle ein Konto oder melde dich an
3. Generiere einen neuen API-Key
4. Kopiere den Key in deine .env Datei
Hinweis: Der API-Key ist nur 24 Stunden gültig und muss regelmäßig erneuert werden.

## Verwendung

1. Starte die Anwendung:
```bash
python app.py
```
2. Der Browser öffnet automatisch http://127.0.0.1:5000
3. Gib eine Riot ID im Format "Name#Tag" ein (z.B. "Doublelift#EUW")
4. Klicke auf "Check" um die letzten Spiele anzuzeigen

## Projektstruktur

```text
League/
├── app.py                 # Hauptanwendung (Flask Server)
├── index.html            # Frontend Template
├── .env                  # Umgebungsvariablen (nicht im Repository)
├── requirements.txt      # Python Abhängigkeiten
└── README.md            # Diese Datei
```
