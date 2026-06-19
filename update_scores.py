import requests
import json

API_KEY = "7986da72567f4d5ea156cbb8acef7948"

headers = {
    "X-Auth-Token": API_KEY
}

url = "https://api.football-data.org/v4/competitions/WC/matches"

response = requests.get(url, headers=headers, verify=False)
data = response.json()

# ✅ Carrega seu JSON local
with open("games.json", "r", encoding="utf-8") as f:
    games = json.load(f)

# ✅ Atualiza jogos
for api_game in data["matches"]:

    status = api_game["status"]

    # ✅ ACEITA JOGO FINALIZADO E AO VIVO
    if status not in ["FINISHED", "IN_PLAY", "PAUSED"]:
        continue

    team1 = api_game["homeTeam"]["name"]
    team2 = api_game["awayTeam"]["name"]

    score1 = api_game["score"]["fullTime"]["home"]
    score2 = api_game["score"]["fullTime"]["away"]

    for g in games:
        if g["team1"] == team1 and g["team2"] == team2:

            # ✅ salva o status sempre
            g["status"] = status

            if status == "FINISHED":
                # ✅ resultado final
                g["score1"] = score1
                g["score2"] = score2

                # limpa live
                g["live_score1"] = None
                g["live_score2"] = None

            else:
                # ✅ AO VIVO (TURBO)
                # fallback seguro
                live_score1 = api_game["score"]["fullTime"]["home"]
                live_score2 = api_game["score"]["fullTime"]["away"]

                if live_score1 is None:
                    live_score1 = api_game["score"]["halfTime"]["home"]

                if live_score2 is None:
                    live_score2 = api_game["score"]["halfTime"]["away"]

                # último fallback
                live_score1 = live_score1 if live_score1 is not None else 0
                live_score2 = live_score2 if live_score2 is not None else 0

                g["live_score1"] = live_score1
                g["live_score2"] = live_score2

# ✅ Salva atualizado
with open("games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ Games atualizados com sucesso")
