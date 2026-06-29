import pandas as pd
import json

arquivo = r"C:\Users\f106263\Documents\Bolão da Copa\Bolao_Copa_do_Mundo_2026.xlsx"

games = []

# =========================
# ✅ FASE DE GRUPOS
# =========================
df_grupos = pd.read_excel(arquivo, sheet_name="Fase de Grupos")

for _, row in df_grupos.iterrows():

    score1 = None if pd.isna(row[5]) else int(row[5])
    score2 = None if pd.isna(row[7]) else int(row[7])

    status = "SCHEDULED" if score1 is None else "FINISHED"

    games.append({
        "date": str(row[1]),
        "time": str(row[2]),
        "team1": row[4],
        "team2": row[8],
        "score1": score1,
        "score2": score2,
        "live_score1": score1,
        "live_score2": score2,
        "status": status,
        "group": row[3],
        "city": row[9] if not pd.isna(row[9]) else ""
    })

# =========================
# ✅ MATA-MATA
# =========================
df_mm = pd.read_excel(arquivo, sheet_name="Mata-Mata")

for _, row in df_mm.iterrows():

    score1 = None if pd.isna(row[4]) else int(row[4])
    score2 = None if pd.isna(row[6]) else int(row[6])

    status = "SCHEDULED" if score1 is None else "FINISHED"

    games.append({
        "date": str(row[2]),
        "time": str(row[9]),  # ✅ AGORA PEGA HORÁRIO
        "team1": row[3],
        "team2": row[7],
        "score1": score1,
        "score2": score2,
        "live_score1": score1,
        "live_score2": score2,
        "status": status,
        "group": row[1],  # ✅ pega "16 avos", "Oitavas" etc
        "city": ""
    })

# =========================
# ✅ SALVAR JSON
# =========================
with open(r"C:\Users\f106263\Documents\Bolão da Copa\games.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ games.json atualizado com grupos + mata-mata + horário ✅")