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
*****for m in data.get("matches", []):

    status_api = m["status"]

    # ✅ NORMALIZA STATUS
    if status_api in ["IN_PLAY", "PAUSED"]:
        status = "LIVE"
    else:
        status = status_api

    # ✅ PEGA SCORE
    score1 = m["score"]["fullTime"]["home"]
    score2 = m["score"]["fullTime"]["away"]

    game = {
        "date": m["utcDate"][8:10] + "/" + m["utcDate"][5:7],
        "time": m["utcDate"][11:16],
        "team1": translate(m["homeTeam"]["name"]),
        "team2": translate(m["awayTeam"]["name"]),
        "score1": score1,
        "score2": score2,

        # ✅ ESSENCIAL
        "live_score1": score1,
        "live_score2": score2,

        "status": status,
        "group": m.get("group", "A"),  # ajuste se necessário
        "city": ""
    }

    games.append(game)
    
    except Exception as e:
        print("Erro ao processar jogo:", e)

# ✅ salva JSON
with open("games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("games.json atualizado ✅")
