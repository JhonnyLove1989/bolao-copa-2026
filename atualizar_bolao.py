import requests
import json
import os
import subprocess
import warnings
warnings.filterwarnings("ignore")

# ============================================
# ⚙️ CONFIGURAÇÃO
# ============================================
API_KEY = os.environ.get("API_KEY", "7986da72567f4d5ea156cbb8acef7948")
API_URL = "https://api.football-data.org/v4/competitions/WC/matches"

# ============================================
# ✅ MAPA DE NOMES (igual ao seu)
# ============================================
TEAM_MAP = {
    "Mexico": "México",
    "South Africa": "África do Sul",
    "Korea Republic": "Coreia do Sul",
    "Czechia": "República Tcheca",
    "Czech Republic": "República Tcheca",
    "Scotland": "Escócia",
    "Morocco": "Marrocos",
    "Haiti": "Haiti",
    "Canada": "Canadá",
    "Switzerland": "Suíça",
    "Qatar": "Catar",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "United States": "EUA",
    "USA": "EUA",
    "Germany": "Alemanha",
    "Netherlands": "Holanda",
    "Japan": "Japão",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "Algeria": "Argélia",
    "Iraq": "Iraque",
    "Norway": "Noruega"
}

def translate(name):
    return TEAM_MAP.get(name, name)

# ============================================
# ✅ BUSCAR API
# ============================================
def fetch_scores():
    print("🔄 Buscando placares...")
    headers = {"X-Auth-Token": API_KEY}
    r = requests.get(API_URL, headers=headers, verify=False)

    if r.status_code != 200:
        print("❌ Erro API")
        return None

    data = r.json()
    matches = data.get("matches", [])
    print(f"✅ {len(matches)} jogos carregados")
    return matches

# ============================================
# ✅ ATUALIZAR GAMES.JSON
# ============================================
def update_games(api_matches):
    with open("games.json", "r", encoding="utf-8") as f:
        local_games = json.load(f)

    for game in local_games:
        game.pop("status", None)
        game.pop("live_score1", None)
        game.pop("live_score2", None)

        for m in api_matches:
            home = translate(m["homeTeam"]["name"])
            away = translate(m["awayTeam"]["name"])

            if game["team1"] != home or game["team2"] != away:
                continue

            status = m["status"]

            if status == "FINISHED":
                ft = m["score"]["fullTime"]
                game["score1"] = ft["home"]
                game["score2"] = ft["away"]
                game["status"] = "FINISHED"

            elif status in ["IN_PLAY", "PAUSED"]:
                ft = m["score"]["fullTime"]
                game["live_score1"] = ft["home"] or 0
                game["live_score2"] = ft["away"] or 0
                game["status"] = "LIVE"

            elif status == "HALFTIME":
                ht = m["score"]["halfTime"]
                game["live_score1"] = ht["home"] or 0
                game["live_score2"] = ht["away"] or 0
                game["status"] = "HALFTIME"

            break

    with open("games.json", "w", encoding="utf-8") as f:
        json.dump(local_games, f, ensure_ascii=False, indent=2)

    print("✅ games.json atualizado")

# ============================================
# ✅ CALCULAR RANKING (SEU ORIGINAL)
# ============================================
def calculate_points():
    with open("games.json", "r", encoding="utf-8") as f:
        games = json.load(f)

    with open("palpites.json", "r", encoding="utf-8") as f:
        palpites = json.load(f)

    results = {}
    for g in games:
        if g["score1"] is not None and g["score2"] is not None:
            key = f"{g['team1']}_{g['team2']}"
            results[key] = (g["score1"], g["score2"])

    ranking = {}
    for nome, jogos in palpites.items():
        total_pts = 0

        for p in jogos:
            key = f"{p['team1']}_{p['team2']}"
            if key not in results:
                continue

            real = results[key]

            if p["palpite1"] == real[0] and p["palpite2"] == realtotal_pts += 5
            elif ((p["palpite1"] > p["palpite2"]) == (real[0] > real[1])):
                total_pts += 3

        ranking[nome] = total_pts

    ranking_list = [{"name": k, "pts": v} for k, v in ranking.items()]
    ranking_list.sort(key=lambda x: -x["pts"])

    with open("ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_list, f, ensure_ascii=False, indent=2)

    print("✅ ranking atualizado")

# ============================================
# ✅ MAIN
# ============================================
if __name__ == "__main__":
    print("🏆 Atualizando bolão...")

    api_matches = fetch_scores()
    if api_matches:
        update_games(api_matches)
        calculate_points()

        # ⚠️ ESSA LINHA É A CHAVE:
        # Só faz push se NÃO estiver rodando no GitHub Actions
        if not os.environ.get("GITHUB_ACTIONS"):
            print("💻 Rodando local - pode fazer push manual")

    else:
        print("❌ Falha API")

    print("✅ FINALIZADO")
