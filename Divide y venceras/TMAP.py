import os
import sys
import io
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph, NearestNeighbors
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
import umap
import networkx as nx
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Mapeo etiquetas Fashion-MNIST
LABELS = {
    0: "T-shirt/top", 1: "Trouser", 2: "Pullover", 3: "Dress", 4: "Coat",
    5: "Sandal", 6: "Shirt", 7: "Sneaker", 8: "Bag", 9: "Ankle boot"
}

CSV_PATH = "/mnt/data/fashion-mnist_test.csv"  # archivo que subiste
OUTPUT_DIR = "./tmap_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Intentar importar tmap (puede fallar si no está instalado)
USE_TMAP = False
try:
    import tmap as tm
    import faerun
    USE_TMAP = True
    print("[INFO] Módulo tmap importado: se intentará usar TMAP para layout.")
except Exception as e:
    print("[WARN] tmap no disponible. Usaremos fallback UMAP + MST. Error:", str(e))
    USE_TMAP = False

# ---------- 1) Funciones de carga y preprocesado ----------
def load_fashion_csv(path=CSV_PATH):
    """
    Carga un CSV donde la columna 'label' es la etiqueta
    y el resto son pixels (0..255).
    Si el CSV no tuviera header, intenta inferirlo.
    Devuelve: X_raw (uint8 N x 784), labels (N,)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    # Intentar leer con header
    df = pd.read_csv(path)
    if 'label' not in df.columns:
        # intentar sin header
        df = pd.read_csv(path, header=None)
        df.columns = ['label'] + [f'px{i}' for i in range(df.shape[1]-1)]
    labels = df['label'].astype(int).values
    X = df.drop(columns=['label']).values.astype(np.uint8)
    return X, labels, df

def normalize_for_embedding(X):
    """Normaliza X a rango [0,1] para UMAP/PCA etc."""
    return (X.astype(np.float32) / 255.0)

# ---------- 2) Layout con TMAP (si está instalado) ----------
def compute_tmap_layout_from_uint8(X_uint8):
    """
    Espera X_uint8: numpy array N x D con valores 0..255 (uint8).
    Construye LSHForest y genera layout con tmap.
    Nota: la API de tmap puede variar; este bloque puede requerir ajuste
    según la versión instalada. Se intenta un pipeline estándar.
    """
    # convertir filas a VectorUchar y añadir a LSHForest
    vecs = [tm.VectorUchar(row.tolist()) for row in X_uint8]
    lf = tm.LSHForest()
    for v in vecs:
        lf.add_vector(v)
    lf.index()
    # compute layout (usa el ejemplo de tmap)
    # Se crea una Layout y se usa layout_from_lsh si está disponible
    try:
        # dependencia: la función layout_from_lsh o similar puede existir
        layout = tm.layout_from_lsh(lf)
        # layout es lista de tuples (x,y,id) o similar - adaptamos
        coords = np.array([[p[0], p[1]] for p in layout])
    except Exception:
        # fallback a layout usando vectores (menos eficiente)
        layout_obj = tm.Layout()
        layout_obj.create_layout(vecs)
        pts = layout_obj.get_coords()
        coords = np.array(pts)
    return coords

# ---------- 3) Fallback: UMAP + MST layout ----------
def compute_umap_mst_layout(X_norm, n_neighbors=15, min_dist=0.1, random_state=42):
    """
    X_norm: N x D con valores en [0,1]
    Retorna: coords (N x 2) y mst (NetworkX graph on indices)
    """
    reducer = umap.UMAP(n_components=2, n_neighbors=n_neighbors, min_dist=min_dist, random_state=random_state)
    embedding = reducer.fit_transform(X_norm)
    # kNN graph sobre embedding y MST sobre ese grafo
    knn = kneighbors_graph(embedding, n_neighbors=n_neighbors, include_self=False)
    G = nx.from_scipy_sparse_matrix(knn)
    # asignar pesos como distancias euclidianas sobre el embedding
    for u, v in G.edges():
        G[u][v]['weight'] = float(np.linalg.norm(embedding[u] - embedding[v]))
    mst = nx.minimum_spanning_tree(G, weight='weight')
    return embedding, mst

# ---------- 4) Visualización ----------
def plot_scatter(coords, labels=None, title='Layout', savepath=None, figsize=(10,8)):
    plt.figure(figsize=figsize)
    if labels is None:
        plt.scatter(coords[:,0], coords[:,1], s=6, alpha=0.8)
    else:
        scatter = plt.scatter(coords[:,0], coords[:,1], c=labels, s=8, cmap='tab10', alpha=0.9)
        # crear leyenda con etiquetas de LABELS relevantes (hasta 10)
        handles, _ = scatter.legend_elements(num=10)
        # Mostrar leyenda fuera del plot
        plt.legend(handles=handles, labels=[LABELS[i] for i in sorted(np.unique(labels))], bbox_to_anchor=(1.05,1), loc='upper left')
    plt.title(title)
    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=150, bbox_inches='tight')
        print(f"[SAVED] {savepath}")
    plt.close()

def plot_with_tree(coords, mst, labels=None, title='Layout con MST', savepath=None, figsize=(10,8)):
    plt.figure(figsize=figsize)
    # dibujar aristas del MST
    for u, v in mst.edges():
        x = [coords[u,0], coords[v,0]]
        y = [coords[u,1], coords[v,1]]
        plt.plot(x, y, linewidth=0.3, alpha=0.6, color='gray')
    if labels is None:
        plt.scatter(coords[:,0], coords[:,1], s=6, alpha=0.9)
    else:
        plt.scatter(coords[:,0], coords[:,1], c=labels, s=8, cmap='tab10', alpha=0.9)
    plt.title(title)
    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=150, bbox_inches='tight')
        print(f"[SAVED] {savepath}")
    plt.close()

# ---------- 5) Subset y subclustering ----------
def select_by_label(labels, target_label):
    """Devuelve indices donde labels == target_label"""
    return np.where(labels == target_label)[0]

def find_subclusters(coords_subset, method='dbscan', **kwargs):
    if method == 'dbscan':
        eps = kwargs.get('eps', 0.5)
        min_samples = kwargs.get('min_samples', 5)
        cl = DBSCAN(eps=eps, min_samples=min_samples).fit(coords_subset)
        return cl.labels_
    elif method == 'kmeans':
        k = kwargs.get('k', 6)
        cl = KMeans(n_clusters=k, random_state=0).fit(coords_subset)
        return cl.labels_
    else:
        raise ValueError("Método de subclustering no reconocido")

# ---------- 6) Selección de representantes y mosaicos ----------
def pick_representatives(coords_subset, labels_subset, n_per_cluster=6):
    """
    Para cada subcluster (excluyendo label -1 de ruido), selecciona hasta n_per_cluster
    puntos más cercanos al centroide del subcluster.
    Retorna índices relativos al subset (0..len(subset)-1).
    """
    reps = []
    unique = [c for c in np.unique(labels_subset) if c != -1]
    for c in unique:
        idxs = np.where(labels_subset == c)[0]
        if len(idxs) == 0:
            continue
        centroid = coords_subset[idxs].mean(axis=0)
        dists = np.linalg.norm(coords_subset[idxs] - centroid, axis=1)
        order = np.argsort(dists)
        chosen = idxs[order[:min(n_per_cluster, len(order))]]
        reps.extend(chosen.tolist())
    return reps

def plot_image_mosaic(X_raw, indices_global, ncols=6, title=None, savepath=None):
    """
    X_raw: N x 784 uint8 (0..255)
    indices_global: indices globales al dataset
    """
    n = len(indices_global)
    if n == 0:
        print("[WARN] No hay imágenes para mosaico.")
        return
    nrows = math.ceil(n / ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*1.5, nrows*1.5))
    axs = np.array(axs).reshape(-1)
    for ax in axs:
        ax.axis('off')
    for i, idx in enumerate(indices_global):
        img = X_raw[idx].reshape(28,28)
        axs[i].imshow(img, cmap='gray', interpolation='nearest')
    if title:
        plt.suptitle(title)
    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=150, bbox_inches='tight')
        print(f"[SAVED] {savepath}")
    plt.close()

# ---------- 7) PDF report ----------
def generate_pdf_report(output_pdf_path, images_paths, sections_text):
    """
    images_paths: lista de rutas a imágenes (png/jpg)
    sections_text: lista de tuplas (titulo, texto_descriptivo)
    Crea un PDF con cada pagina conteniendo texto y una imagen.
    """
    c = canvas.Canvas(output_pdf_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    # Portada
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-80, "Análisis TMAP - Fashion-MNIST")
    c.setFont("Helvetica", 11)
    c.drawString(30, height-120, "Pipeline: layout global, selección de cluster, análisis de subclusters y representantes.")
    c.showPage()
    # Agregar secciones (coincidencia entre images_paths y sections_text)
    for (title, paragraph), img_path in zip(sections_text, images_paths):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height-60, title)
        c.setFont("Helvetica", 10)
        textobject = c.beginText(30, height-90)
        for line in paragraph.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        if os.path.exists(img_path):
            pil_img = Image.open(img_path)
            img_reader = ImageReader(pil_img)
            # dibujar imagen ocupando la mitad inferior de la página
            c.drawImage(img_reader, 30, 30, width=width-60, height=height/2, preserveAspectRatio=True)
        c.showPage()
    c.save()
    print(f"[SAVED] {output_pdf_path}")

# ---------- 8) MAIN pipeline ----------
def main(csv_path=CSV_PATH, target_label=7):
    print("[START] Cargando dataset ...")
    X_raw, labels, df = load_fashion_csv(csv_path)
    N = X_raw.shape[0]
    print(f"[INFO] Dataset cargado: {N} muestras. Path: {csv_path}")

    # Preprocesado para embedding
    X_norm = normalize_for_embedding(X_raw)  # float32 0..1

    # Layout global
    if USE_TMAP:
        try:
            coords_global = compute_tmap_layout_from_uint8(X_raw)
            # No obtenemos MST fácilmente a partir del layout en este wrapper simple; dibujar scatter
            out_global = os.path.join(OUTPUT_DIR, "tmap_global.png")
            plot_scatter(coords_global, labels=labels, title="TMAP - layout global (coloreado por etiqueta)", savepath=out_global)
        except Exception as e:
            print("[WARN] Error al ejecutar TMAP. Usando fallback UMAP+MST. Error:", str(e))
            coords_global, mst_global = compute_umap_mst_layout(X_norm)
            out_global = os.path.join(OUTPUT_DIR, "umap_mst_global.png")
            plot_with_tree(coords_global, mst_global, labels=labels, title="UMAP+MST - layout global (coloreado por etiqueta)", savepath=out_global)
    else:
        coords_global, mst_global = compute_umap_mst_layout(X_norm)
        out_global = os.path.join(OUTPUT_DIR, "umap_mst_global.png")
        plot_with_tree(coords_global, mst_global, labels=labels, title="UMAP+MST - layout global (coloreado por etiqueta)", savepath=out_global)

    # Seleccionar cluster por etiqueta (target_label)
    indices_cluster = select_by_label(labels, target_label)
    print(f"[INFO] Seleccionadas {len(indices_cluster)} instancias de la etiqueta {target_label} ({LABELS.get(target_label, 'N/A')}).")

    # Reaplicar layout en subset
    X_subset_raw = X_raw[indices_cluster]
    X_subset_norm = X_norm[indices_cluster]

    if USE_TMAP:
        try:
            coords_subset = compute_tmap_layout_from_uint8(X_subset_raw)
            out_subset = os.path.join(OUTPUT_DIR, f"tmap_subset_label_{target_label}.png")
            plot_scatter(coords_subset, labels=None, title=f"TMAP - subset {LABELS[target_label]}", savepath=out_subset)
        except Exception as e:
            print("[WARN] Error TMAP en subset. Usando UMAP+MST en subset. Error:", str(e))
            coords_subset, mst_subset = compute_umap_mst_layout(X_subset_norm)
            out_subset = os.path.join(OUTPUT_DIR, f"umap_mst_subset_label_{target_label}.png")
            plot_with_tree(coords_subset, mst_subset, labels=None, title=f"UMAP+MST - subset {LABELS[target_label]}", savepath=out_subset)
    else:
        coords_subset, mst_subset = compute_umap_mst_layout(X_subset_norm)
        out_subset = os.path.join(OUTPUT_DIR, f"umap_mst_subset_label_{target_label}.png")
        plot_with_tree(coords_subset, mst_subset, labels=None, title=f"UMAP+MST - subset {LABELS[target_label]}", savepath=out_subset)

    # Subclustering sobre coords_subset (DBSCAN)
    sublabels = find_subclusters(coords_subset, method='dbscan', eps=0.45, min_samples=8)
    unique_subs = np.unique(sublabels)
    print(f"[INFO] Subclusters detectados (DBSCAN): {unique_subs}")

    # Seleccionar representantes por subcluster (índices relativos al subset)
    reps_rel = pick_representatives(coords_subset, sublabels, n_per_cluster=6)
    # Convertir a índices globales
    reps_global = indices_cluster[reps_rel]
    out_mosaic = os.path.join(OUTPUT_DIR, f"representatives_label_{target_label}.png")
    plot_image_mosaic(X_raw, reps_global, ncols=6, title=f"Representantes por subcluster - {LABELS[target_label]}", savepath=out_mosaic)

    # Preparar PDF
    images_for_pdf = [out_global, out_subset, out_mosaic]
    sections_text = [
        ("Mapa global (layout)", "Layout global del dataset coloreado por etiqueta. Observa la distribución y agrupamiento por categoría."),
        (f"Subset: {LABELS[target_label]}", f"Mapa del subset correspondiente a la etiqueta {target_label} - {LABELS[target_label]}. Se observan posibles subclusteres."),
        ("Imágenes representativas", "Imágenes seleccionadas como representativas por subcluster (puntos cercanos al centroide del subcluster).")
    ]
    out_pdf = os.path.join(OUTPUT_DIR, f"reporte_tmap_fashion_label_{target_label}.pdf")
    generate_pdf_report(out_pdf, images_for_pdf, sections_text)

    print("[DONE] Pipeline completado. Revisa la carpeta:", OUTPUT_DIR)

# ---------- 9) Ejecutar ----------
if __name__ == "__main__":
    # permite pasar la etiqueta objetivo por argumento
    target = 7
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except:
            print("[WARN] Argumento inválido para etiqueta. Usando 7 (Sneaker).")
    main(csv_path=CSV_PATH, target_label=target)
