import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
import mplcursors

# Clase para cargar el dataset

class FashionMNISTDataset:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self.labels = self.data['label'].values
        self.images = self.data.drop('label', axis=1).values

# Ruta del archivo CSV

csv_path = r"C:\Users\Kirby\Documents\Cucei\Quinto Semestre\Analisis de algoritmos\Clustering\fashion-mnist_test.csv"

dataset = FashionMNISTDataset(csv_path)

# Preprocesamiento

scaler = StandardScaler()
X_scaled = scaler.fit_transform(dataset.images)

# Reducimos dimensionalidad con PCA y luego UMAP
pca = PCA(n_components=50)
X_pca = pca.fit_transform(X_scaled)

umap_model = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
embedding = umap_model.fit_transform(X_pca)

# Etiquetas y colores

class_names = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

colors = plt.cm.tab10(dataset.labels / 10)

# Gráfico base

fig, ax = plt.subplots(figsize=(10, 8))
sc = ax.scatter(embedding[:, 0], embedding[:, 1], c=dataset.labels, cmap='tab10', s=10)
plt.title("Mapa UMAP – Fashion MNIST (pasa el cursor para ver la prenda)")
plt.xlabel("UMAP 1")
plt.ylabel("UMAP 2")

# Interactividad con mplcursors

cursor = mplcursors.cursor(sc, hover=True)

@cursor.connect("add")
def on_hover(sel):
    idx = sel.index
    img = dataset.images[idx].reshape(28, 28)
    label = dataset.labels[idx]
    class_name = class_names[label]
    
    # Mostrar imagen en ventana flotante
    fig_img, ax_img = plt.subplots(figsize=(2, 2))
    ax_img.imshow(img, cmap='gray')
    ax_img.set_title(f"{class_name}")
    ax_img.axis("off")
    plt.show(block=False)

plt.show()