import os
import pandas as pd
import matplotlib.pyplot as plt

# Alle Modelle
model_dirs = ["pixtral", "gpt", "deepseek", "textract", "azure", "google_vision"]
base_analysis_path = "analysis"

# Bewertungsmetriken
scaled_metrics = ["accuracy", "precision", "recall", "f1_score"]
absolute_metrics = ["levenshtein_total"]

summary = []

for model in model_dirs:
    path = os.path.join(base_analysis_path, model, f"ocr_comparison_{model}.xlsx")
    if not os.path.exists(path):
        print(f"⚠️ Datei nicht gefunden für {model}: {path}")
        continue

    df = pd.read_excel(path, index_col=0)

    # Dokumenttyp trennen
    df_clean = df[~df.index.str.contains("noise", case=False, na=False)]
    df_rausch = df[df.index.str.contains("noise", case=False, na=False)]

    avg_clean = df_clean.mean(numeric_only=True)
    avg_rausch = df_rausch.mean(numeric_only=True)

    row = {"model": model}
    for metric in scaled_metrics + absolute_metrics:
        row[f"clean_{metric}"] = avg_clean.get(metric, None)
        row[f"rausch_{metric}"] = avg_rausch.get(metric, None)

    summary.append(row)

# Zusammenfassen
summary_df = pd.DataFrame(summary)

# Speicherpfad für Plots vorbereiten
plot_output_path = os.path.join(base_analysis_path, "plots")
os.makedirs(plot_output_path, exist_ok=True)

# Diagramme für skalierte Metriken
for metric in scaled_metrics:
    if f"clean_{metric}" not in summary_df.columns:
        continue

    plt.figure(figsize=(10, 6))
    plt.title(f"{metric.capitalize()} – Vergleich Original vs. Verrauscht")
    x = summary_df["model"]
    x_pos = range(len(x))
    width = 0.35

    plt.bar([p - width/2 for p in x_pos], summary_df[f"clean_{metric}"], width=width, label="Original", alpha=0.7)
    plt.bar([p + width/2 for p in x_pos], summary_df[f"rausch_{metric}"], width=width, label="Verrauscht", alpha=0.7)

    plt.ylabel(metric)
    plt.ylim(0, 1.05)
    plt.xticks(x_pos, x, rotation=30, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_file = os.path.join(plot_output_path, f"{metric}_vergleich_clean_vs_noise.png")
    plt.savefig(plot_file)
    print(f"✅ Gespeichert: {plot_file}")
    plt.show()

# Diagramme für absolute Metriken
for metric in absolute_metrics:
    if f"clean_{metric}" not in summary_df.columns:
        continue

    plt.figure(figsize=(10, 6))
    plt.title(f"{metric.replace('_', ' ').capitalize()} – Vergleich Original vs. Verrauscht")
    x = summary_df["model"]
    x_pos = range(len(x))
    width = 0.35

    plt.bar([p - width/2 for p in x_pos], summary_df[f"clean_{metric}"], width=width, label="Original", alpha=0.7)
    plt.bar([p + width/2 for p in x_pos], summary_df[f"rausch_{metric}"], width=width, label="Verrauscht", alpha=0.7)

    plt.ylabel("Fehleranzahl (Zeichen)")
    plt.xticks(x_pos, x, rotation=30, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_file = os.path.join(plot_output_path, f"{metric}_vergleich_clean_vs_noise.png")
    plt.savefig(plot_file)
    print(f"✅ Gespeichert: {plot_file}")
    plt.show()
