import requests
import json
import os

# 🔐 API KEY
API_KEY = os.getenv("API_KEY")

url = "https://api.football-data.org/v4/competitions/WC/matches"

headers = {
    "X-Auth-Token": API_KEY
}

# ✅ evitar warning SSL
requests.packages.urllib3.disable_warnings()

response = requests.get(url, headers=headers, verify=False)

# ✅ valida resposta
if response.status_code != 200:
    print("Erro na API:", response.status_code)
    exit()

data = response.json()

games = []

# ✅ LOOP CORRETO
for m in data.get("matches", []):
    try:
        status_api = m["status"]

        # ✅ NORMALIZA STATUS
        if status_api in ["IN_PLAY", "PAUSED"]:
            status = "LIVE"
        else:
            status = status_api

        # ✅ SCORES
        score_full1 = m["score"]["fullTime"]["home"]
        score_full2 = m["score"]["fullTime"]["away"]

        score_half1 = m["score"]["halfTime"]["home"]
        score_half2 = m["score"]["halfTime"]["away"]

        score1 = score_full1
        score2 = score_full2

        # ✅ LIVE SCORE INTELIGENTE
        live1 = score_half1 if score_half1 is not None else score_full1
        live2 = score_half2 if score_half2 is not None else score_full2

        # ✅ MONTA JOGO
        game = {
            "date": m["utcDate"][8:10] + "/" + m["utcDate"][5:7],
            "time": m["utcDate"][11:16],
            "team1": m["homeTeam"]["name"],
            "team2": m["awayTeam"]["name"],
            "score1": score1,
            "score2": score2,

            # ✅ AQUI ESTÁ A CORREÇÃO PRINCIPAL
            "live_score1": live1,
            "live_score2": live2,

            "status": status,
            "group": m.get("group", "A"),
            "city": ""
        }

        games.append(game)

    except Exception as e:
        print("Erro ao processar jogo:", e)

# ✅ SALVA JSON
with open("games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ games.json atualizado com sucesso")
