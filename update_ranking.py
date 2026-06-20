import json

# carregar dados
with open("games.json", "r", encoding="utf-8") as f:
    games = json.load(f)

with open("palpites.json", "r", encoding="utf-8") as f:
    palpites = json.load(f)

ranking = []

for pessoa, jogos in palpites.items():
    pontos = 0

    for p in jogos:
        # acha jogo real
        jogo_real = next(
            (g for g in games if g["team1"] == p["team1"] and g["team2"] == p["team2"] and g["date"] == p["date"]),
            None
        )

        if not jogo_real:
            continue

        # 🔥 pega placar (final ou ao vivo)
        s1 = jogo_real.get("score1")
        s2 = jogo_real.get("score2")

        # ✅ se não tiver score final, usa live_score
        if s1 is None and jogo_real.get("status") in ["LIVE", "IN_PLAY", "PAUSED"]:
            s1 = jogo_real.get("live_score1")
            s2 = jogo_real.get("live_score2")

        # ✅ ignora jogos sem placar
        if s1 is None or s2 is None:
            continue

        palpite1 = p.get("palpite1")
        palpite2 = p.get("palpite2")

        # ✅ ignora jogos sem palpite
        if palpite1 is None or palpite2 is None:
            continue

        # ✅ placar exato = 5 pts
        if s1 == palpite1 and s2 == palpite2:
            pontos += 5

        # ✅ resultado correto = 3 pts
        elif (
            (s1 > s2 and palpite1 > palpite2) or
            (s2 > s1 and palpite2 > palpite1) or
            (s1 == s2 and palpite1 == palpite2)
        ):
            pontos += 3

    ranking.append({
        "name": pessoa,
        "pts": pontos
    })

# ordena ranking
ranking.sort(key=lambda x: x["pts"], reverse=True)

# salva novo ranking
with open("ranking.json", "w", encoding="utf-8") as f:
    json.dump(ranking, f, ensure_ascii=False, indent=2)

print("✅ Ranking atualizado em tempo real (LIVE + FINAL)")
