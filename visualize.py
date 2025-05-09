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

    if "Durchschnitt" not in df.index:
        avg_row = df.mean(numeric_only=True)
        avg_row.name = "Durchschnitt"
        df = pd.concat([df, pd.DataFrame([avg_row])])

    row = {"model": model}

    for metric in scaled_metrics + absolute_metrics:
        if metric in df.columns:
            row[f"avg_{metric}"] = df.loc["Durchschnitt", metric]
            row[f"max_{metric}"] = df.drop("Durchschnitt", errors="ignore")[metric].max()
            row[f"min_{metric}"] = df.drop("Durchschnitt", errors="ignore")[metric].min()

    summary.append(row)

# Zusammenfassen
summary_df = pd.DataFrame(summary)

# Speicherpfad für Plots vorbereiten
plot_output_path = os.path.join(base_analysis_path, "plots")
os.makedirs(plot_output_path, exist_ok=True)

# Skalenbasierte Metriken
for metric in scaled_metrics:
    if f"avg_{metric}" not in summary_df.columns:
        continue

    plt.figure(figsize=(10, 6))
    plt.title(f"{metric.capitalize()} Vergleich der Modelle")

    plt.bar(summary_df["model"], summary_df[f"avg_{metric}"], label="Durchschnitt", alpha=0.7)
    plt.scatter(summary_df["model"], summary_df[f"max_{metric}"], color='green', label='Bester Wert', zorder=5)
    plt.scatter(summary_df["model"], summary_df[f"min_{metric}"], color='red', label='Schlechtester Wert', zorder=5)

    plt.ylabel(metric)
    plt.ylim(0, 1.05)
    plt.xticks(rotation=30, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_file = os.path.join(plot_output_path, f"{metric}_vergleich.png")
    plt.savefig(plot_file)
    print(f"✅ Gespeichert: {plot_file}")

    plt.show()

# Absolute Metriken
for metric in absolute_metrics:
    if f"avg_{metric}" not in summary_df.columns:
        continue

    plt.figure(figsize=(10, 6))
    plt.title(f"{metric.replace('_', ' ').capitalize()} Vergleich der Modelle")

    plt.bar(summary_df["model"], summary_df[f"avg_{metric}"], label="Durchschnitt", alpha=0.7)
    plt.scatter(summary_df["model"], summary_df[f"max_{metric}"], color='red', label='Schlechtester Wert', zorder=5)
    plt.scatter(summary_df["model"], summary_df[f"min_{metric}"], color='green', label='Bester Wert', zorder=5)

    plt.ylabel("Fehleranzahl (Zeichen)")
    plt.xticks(rotation=30, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_file = os.path.join(plot_output_path, f"{metric}_vergleich.png")
    plt.savefig(plot_file)
    print(f"✅ Gespeichert: {plot_file}")

    plt.show()
