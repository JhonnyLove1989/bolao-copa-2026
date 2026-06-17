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

# ✅ MAPA DE NOMES (API → SEU DASHBOARD)
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
    "Bosnia-Herzegovina": "Bósnia e Herzegovina",
    "United States": "EUA",
    "USA": "EUA",
    "Paraguay": "Paraguai",
    "Germany": "Alemanha",
    "Netherlands": "Holanda",
    "Japan": "Japão",
    "Australia": "Austrália",
    "Türkiye": "Turquia",
    "Turkey": "Turquia",
    "Curaçao": "Curaçao",
    "Curacao": "Curaçao",
    "Côte d'Ivoire": "Costa do Marfim",
    "Ivory Coast": "Costa do Marfim",
    "Ecuador": "Equador",
    "Sweden": "Suécia",
    "Tunisia": "Tunísia",
    "Belgium": "Bélgica",
    "Egypt": "Egito",
    "Iran": "Irã",
    "IR Iran": "Irã",
    "New Zealand": "Nova Zelândia",
    "Spain": "Espanha",
    "Cape Verde": "Cabo Verde",
    "Cabo Verde": "Cabo Verde",
    "Saudi Arabia": "Arábia Saudita",
    "Uruguay": "Uruguai",
    "France": "França",
    "Senegal": "Senegal",
    "Iraq": "Iraque",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argélia",
    "Austria": "Áustria",
    "Jordan": "Jordânia",
    "Portugal": "Portugal",
    "DR Congo": "RD Congo",
    "Congo DR": "RD Congo",
    "Uzbekistan": "Uzbequistão",
    "Colombia": "Colômbia",
    "England": "Inglaterra",
    "Croatia": "Croácia",
    "Ghana": "Gana",
    "Panama": "Panamá",
    "Brazil": "Brasil",
}

def translate(name):
    return TEAM_MAP.get(name, name)

# ============================================
# ✅ 1. BUSCAR PLACARES DA API
# ============================================
def fetch_scores():
    print("🔄 Buscando placares da API...")
    headers = {"X-Auth-Token": API_KEY}
    r = requests.get(API_URL, headers=headers, verify=False)

    if r.status_code != 200:
        print(f"⚠️ Erro na API: {r.status_code}")
        return None

    data = r.json()
    matches = data.get("matches", [])
    played = len([m for m in matches if m["status"] == "FINISHED"])
    live = len([m for m in matches if m["status"] in ["IN_PLAY", "PAUSED", "HALFTIME"]])
    print(f"✅ {len(matches)} jogos encontrados ({played} finalizados, {live} ao vivo)")
    return matches

# ============================================
# ✅ 2. ATUALIZAR GAMES.JSON
# ============================================
def update_games(api_matches):
    print("🔄 Atualizando games.json...")

    with open("games.json", "r", encoding="utf-8") as f:
        local_games = json.load(f)

    updated = 0
    live = 0

    for game in local_games:
        game.pop("status", None)
        game.pop("live_score1", None)
        game.pop("live_score2", None)
        game.pop("minutes", None)

        for m in api_matches:
            api_home = translate(m["homeTeam"]["name"])
            api_away = translate(m["awayTeam"]["name"])

            if game["team1"] != api_home or game["team2"] != api_away:
                continue

            status = m["status"]

            if status == "FINISHED":
                ft = m["score"]["fullTime"]
                game["score1"] = ft["home"]
                game["score2"] = ft["away"]
                game["status"] = "FINISHED"
                updated += 1

            elif status in ["IN_PLAY", "PAUSED"]:
                ft = m["score"]["fullTime"]
                game["live_score1"] = ft["home"] or 0
                game["live_score2"] = ft["away"] or 0
                game["status"] = "LIVE"
                live += 1

            elif status == "HALFTIME":
                ht = m["score"]["halfTime"]
                game["live_score1"] = ht["home"] or 0
                game["live_score2"] = ht["away"] or 0
                game["status"] = "HALFTIME"
                live += 1

            break

    with open("games.json", "w", encoding="utf-8") as f:
        json.dump(local_games, f, ensure_ascii=False, indent=2)

    print(f"✅ {updated} jogos finalizados | {live} jogos ao vivo")

# ============================================
# ✅ 3. CALCULAR PONTOS
# ============================================
def calculate_points():
    print("🔄 Calculando pontos...")

    with open("games.json", "r", encoding="utf-8") as f:
        games = json.load(f)

    with open("palpites.json", "r", encoding="utf-8") as f:
        palpites = json.load(f)

    results = {}
    for g in games:
        if g["score1"] is not None:
            results[f"{g['team1']}_{g['team2']}"] = (g["score1"], g["score2"])

    ranking = {}

    for nome, jogos in palpites.items():
        pts = 0
        for p in jogos:
            key = f"{p['team1']}_{p['team2']}"
            if key not in results:
                continue

            real = results[key]

            if p["palpite1"] == real[0] and p["palpite2"] == real[1]:
                pts += 5
            elif p.get("palpite1") is not None and p.get("palpite2") is not None:
    if (p["palpite1"] > p["palpite2"]) == (real[0] > real[1]):
        pts += 3
        
        ranking[nome] = pts

    ranking_list = [{"name": k, "pts": v} for k, v in ranking.items()]
    ranking_list.sort(key=lambda x: -x["pts"])

    with open("ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_list, f, ensure_ascii=False, indent=2)

    print("✅ Ranking atualizado")

# ============================================
# ✅ EXECUÇÃO
# ============================================
if __name__ == "__main__":
    print("🚀 Rodando atualização do bolão\n")

    api = fetch_scores()

    if api:
        update_games(api)
        calculate_points()
    else:
        print("❌ Falha ao buscar API")

    print("\n✅ Finalizado")
