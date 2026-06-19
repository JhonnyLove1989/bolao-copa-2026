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
    if api_game["status"] != "FINISHED":
        continue

    team1 = api_game["homeTeam"]["name"]
    team2 = api_game["awayTeam"]["name"]

    score1 = api_game["score"]["fullTime"]["home"]
    score2 = api_game["score"]["fullTime"]["away"]

    for g in games:
        if g["team1"] == team1 and g["team2"] == team2:
            g["score1"] = score1
            g["score2"] = score2
            g["status"] = "FINISHED"

# ✅ Salva atualizado
with open("games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ Games atualizados com sucesso")