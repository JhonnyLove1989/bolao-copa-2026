import requests
import json
import os
from datetime import datetime

# 🔐 usa variável de ambiente (melhor prática)
API_KEY = os.getenv("API_KEY")

url = "https://api.football-data.org/v4/competitions/WC/matches"

headers = {
    "X-Auth-Token": API_KEY
}

# ✅ evitar warning SSL (já que você usa verify=False)
requests.packages.urllib3.disable_warnings()

response = requests.get(url, headers=headers, verify=False)

# ✅ valida resposta
if response.status_code != 200:
    print("Erro na API:", response.status_code)
    exit()

data = response.json()

games = []

for m in data.get("matches", []):

    try:
        team1 = m["homeTeam"]["name"]
        team2 = m["awayTeam"]["name"]

        # ✅ conversão de data UTC → formato DD/MM
        dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))

        date_str = dt.strftime("%d/%m")
        time_str = dt.strftime("%H:%M")

        score_full = m["score"]["fullTime"]
        score_live = m["score"]["regularTime"]

        game = {
            "date": date_str,
            "time": time_str,
            "team1": team1,
            "team2": team2,
            "score1": score_full["home"],
            "score2": score_full["away"],
            "live_score1": score_live["home"],
            "live_score2": score_live["away"],
            "status": m["status"],

            # ✅ evita erro se não tiver grupo
            "group": m.get("group", ""),

            # ✅ opcional (não vem sempre)
            "city": (
                m.get("area", {}).get("name", "")
            )
        }

        games.append(game)

    except Exception as e:
        print("Erro ao processar jogo:", e)

# ✅ salva JSON
with open("games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, indent=2, ensure_ascii=False)

print("games.json atualizado ✅")