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
            (g for g in games if g["team1"] == p["team1"] and g["team2"] == p["team2"]),
            None
        )

        if not jogo_real:
            continue

        if jogo_real["score1"] is None or jogo_real["score2"] is None:
            continue

        s1 = jogo_real["score1"]
        s2 = jogo_real["score2"]

        palpite1 = p["palpite1"]
        palpite2 = p["palpite2"]

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

print("✅ Ranking atualizado com sucesso")