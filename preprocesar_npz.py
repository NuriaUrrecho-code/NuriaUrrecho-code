import shutil
from pathlib import Path
import numpy as np


DATA_DIR = Path(__file__).parent
TRAIN_FILE = DATA_DIR / "trainCards.npz"
TEST_FILE = DATA_DIR / "testCards.npz"


def load_cards(path: Path):
    npzfile = np.load(path, allow_pickle=True)
    return npzfile["Cartas"]


def extract_features(cards):
    features = []
    for card in cards:
        for mot in card.motifs:
            feat = np.asarray(mot.features, dtype=np.float32).flatten()
            if feat.size == 0:
                raise ValueError(f"Motif sin features en carta {card.cardId}")
            features.append(feat)
    # Verifica que todas las filas tengan la misma longitud
    lengths = {f.shape[0] for f in features}
    if len(lengths) != 1:
        raise ValueError(f"Dimensiones de features inconsistentes: {lengths}")
    return np.vstack(features)


def apply_scaled_features(cards, scaled_matrix):
    idx = 0
    for card in cards:
        for mot in card.motifs:
            mot.features = scaled_matrix[idx].tolist()
            idx += 1


def save_cards(path: Path, cards):
    np.savez(path, Cartas=cards)
    print(f"Guardado {path.name}")


def main():
    train_cards = load_cards(TRAIN_FILE)
    test_cards = load_cards(TEST_FILE)

    train_feats = extract_features(train_cards)

    # Recorte suave de outliers en train
    lower = np.percentile(train_feats, 2.0, axis=0)
    upper = np.percentile(train_feats, 98.0, axis=0)
    train_feats = np.clip(train_feats, lower, upper)

    median = np.median(train_feats, axis=0)
    iqr = np.percentile(train_feats, 75, axis=0) - np.percentile(train_feats, 25, axis=0)
    iqr[iqr < 1e-8] = 1.0  # evita divisiones por cero

    # Escalar
    train_scaled = (train_feats - median) / iqr
    test_feats = extract_features(test_cards)
    test_feats = np.clip(test_feats, lower, upper)
    test_scaled = (test_feats - median) / iqr

    # Aplicar
    apply_scaled_features(train_cards, train_scaled)
    apply_scaled_features(test_cards, test_scaled)

    # Sobrescribir
    save_cards(TRAIN_FILE, train_cards)
    save_cards(TEST_FILE, test_cards)


if __name__ == "__main__":
    main()
