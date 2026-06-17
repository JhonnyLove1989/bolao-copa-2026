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
        # Remove status antigo
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

            # JOGO FINALIZADO
            if status == "FINISHED":
                ft = m["score"]["fullTime"]
                game["score1"] = ft["home"]
                game["score2"] = ft["away"]
                game["status"] = "FINISHED"
                updated += 1
                print(f"  ✅ {game['team1']} {game['score1']} x {game['score2']} {game['team2']} (FINALIZADO)")

            # JOGO AO VIVO
            elif status in ["IN_PLAY", "PAUSED"]:
                ft = m["score"]["fullTime"]
                game["live_score1"] = ft["home"] if ft["home"] is not None else 0
                game["live_score2"] = ft["away"] if ft["away"] is not None else 0
                game["status"] = "LIVE"
                game["minutes"] = m.get("minute", "")
                live += 1
                print(f"  🔴 {game['team1']} {game['live_score1']} x {game['live_score2']} {game['team2']} (AO VIVO {game['minutes']}')")

            # INTERVALO
            elif status == "HALFTIME":
                ht = m["score"]["halfTime"]
                game["live_score1"] = ht["home"] if ht["home"] is not None else 0
                game["live_score2"] = ht["away"] if ht["away"] is not None else 0
                game["status"] = "HALFTIME"
                live += 1
                print(f"  ⏸️ {game['team1']} {game['live_score1']} x {game['live_score2']} {game['team2']} (INTERVALO)")

            break

    with open("games.json", "w", encoding="utf-8") as f:
        json.dump(local_games, f, ensure_ascii=False, indent=2)

    print(f"✅ {updated} jogos finalizados | {live} jogos ao vivo")

# ============================================
# ✅ 3. CALCULAR PONTOS DOS PALPITES
# ============================================
def calculate_points():
    print("🔄 Calculando pontos dos palpites...")

    with open("games.json", "r", encoding="utf-8") as f:
        games = json.load(f)

    with open("palpites.json", "r", encoding="utf-8") as f:
        palpites = json.load(f)

    # Mapa de resultados reais
    results = {}
    for g in games:
        if g["score1"] is not None and g["score2"] is not None:
            key = f"{g['team1']}_{g['team2']}"
            results[key] = (g["score1"], g["score2"])

    # Calcula pontos pra cada participante
    ranking = {}
    for nome, jogos in palpites.items():
        total_pts = 0
        exact = 0
        result_ok = 0
        wrong = 0

        for p in jogos:
            key = f"{p['team1']}_{p['team2']}"
            if key not in results:
                p["resultado"] = "⏳"
                p["pontos"] = 0
                continue

            real_s1, real_s2 = results[key]
            p1 = p.get("palpite1")
            p2 = p.get("palpite2")

            if p1 is None or p2 is None:
                p["resultado"] = "❌ Errou"
                p["pontos"] = 0
                wrong += 1
                continue

            if p1 == real_s1 and p2 == real_s2:
                p["resultado"] = "✅ Placar exato!"
                p["pontos"] = 5
                total_pts += 5
                exact += 1
            elif (p1 > p2 and real_s1 > real_s2) or \
                 (p1 < p2 and real_s1 < real_s2) or \
                 (p1 == p2 and real_s1 == real_s2):
                p["resultado"] = "🟡 Acertou resultado"
                p["pontos"] = 3
                total_pts += 3
                result_ok += 1
            else:
                p["resultado"] = "❌ Errou"
                p["pontos"] = 0
                wrong += 1

        ranking[nome] = {
            "name": nome,
            "pts": total_pts,
            "exact": exact,
            "result": result_ok,
            "wrong": wrong
        }

    # Salva palpites atualizados
    with open("palpites.json", "w", encoding="utf-8") as f:
        json.dump(palpites, f, ensure_ascii=False, indent=2)

    # Salva ranking
    ranking_list = sorted(ranking.values(), key=lambda x: (-x["pts"], -x["exact"]))
    with open("ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_list, f, ensure_ascii=False, indent=2)

    print("✅ Pontos calculados e ranking atualizado!")
    print("")
    print("🏆 RANKING ATUAL:")
    print("-" * 45)
    for i, r in enumerate(ranking_list):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        print(f"  {medal} {r['name']}: {r['pts']} pts ({r['exact']}✅ {r['result']}🟡 {r['wrong']}❌)")

# ============================================
# ✅ 4. SUBIR NO GITHUB
# ============================================
def push_to_github():
    print("")
    print("🔄 Enviando pro GitHub...")
    try:
        pasta = os.path.dirname(os.path.abspath(__file__))
        os.chdir(pasta)
        subprocess.run(["git", "add", "games.json", "ranking.json", "palpites.json", "palpites_mm.json"], check=True)
        result = subprocess.run(["git", "commit", "-m", "🔄 Atualização automática dos resultados"],
                               capture_output=True, text=True)
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("ℹ️ Nenhuma alteração nova pra enviar")
            return
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        print("🚀 Enviado pro GitHub com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro no GitHub: {e}")
    except FileNotFoundError:
        print("⚠️ Git não encontrado. Instale: https://git-scm.com")

# ============================================
# ✅ EXECUTAR TUDO
# ============================================
if __name__ == "__main__":
    print("")
    print("=" * 50)
    print("🏆 BOLÃO COPA 2026 — ATUALIZAÇÃO AUTOMÁTICA")
    print("=" * 50)
    print("")

    api_matches = fetch_scores()
    if api_matches:
        update_games(api_matches)
        print("")
        calculate_points()
        # Push é feito pelo GitHub Actions
        if not os.environ.get("API_KEY"):
         push_to_github()
    else:
        print("❌ Falha ao buscar dados da API")

    print("")
    print("=" * 50)
    print("✅ FINALIZADO!")
    print("=" * 50)