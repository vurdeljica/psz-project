import tkinter as tk
from tkinter import filedialog
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import seaborn as sns
from sklearn.decomposition import PCA
from bokeh.models import HoverTool, BoxZoomTool, PanTool, WheelZoomTool
from bokeh.plotting import *
from bokeh.models import ColumnDataSource
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

checkbox_columns = []
checkbox_values = []
prepared_data_frame = []#pd.read_csv('C:/Users/igvu/Desktop/Fakultet/Drugi semestar/PSZ/psz-project/albums_df_prepared.csv')

class CheckBoxColumns(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        global checkbox_columns
        global checkbox_values
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=20, height=15,
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        checkbox_values = []

        for index, column in enumerate(checkbox_columns):
            var = tk.BooleanVar()
            var.set(True)
            checkbox_values.append(var)
            cb = tk.Checkbutton(self, text=column, variable=var)
            cb.config(background='white', activebackground='white')
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n")  # to force one checkbox per line

root = tk.Tk()

canvas1 = tk.Canvas(root, width=400, height=500, relief='raised')
canvas1.pack()

label1 = tk.Label(root, text='k-Means Clustering')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label1)

label2 = tk.Label(root, text='Type Number of Clusters:')
label2.config(font=('helvetica', 8))
canvas1.create_window(200, 120, window=label2)

entry1 = tk.Entry(root)
canvas1.create_window(200, 140, window=entry1)


def getExcel():
    global df
    global checkbox_columns
    global prepared_data_frame
    import_file_path = filedialog.askopenfilename()
    prepared_data_frame = pd.read_csv(import_file_path)
    checkbox_columns = list(prepared_data_frame.columns.values)
    checkbox_columns = list(filter(lambda column: "generated" not in column, checkbox_columns))
    canvas1.create_window(117, 200, window=CheckBoxColumns(root), anchor='nw')


browseButtonExcel = tk.Button(text=" Import Excel File ", command=getExcel, bg='green', fg='white',
                              font=('helvetica', 10, 'bold'))
canvas1.create_window(200, 70, window=browseButtonExcel)

def getKMeans():
    global df
    global numberOfClusters
    global checkbox_columns
    global checkbox_values
    numberOfClusters = int(entry1.get())
    #numberOfClusters = 10

    selected_columns = []
    for index, checkbox_value in enumerate(checkbox_values):
        if checkbox_value.get() == True:
            selected_columns.append(checkbox_columns[index])

    print(selected_columns)

    info_data_frame = pd.DataFrame()

    prepared_columns = list(prepared_data_frame.columns.values)
    columns_for_model = []
    for column in selected_columns:
        for prepared_column in prepared_columns:
            if (column in prepared_column) and (column != prepared_column):
                columns_for_model.append(prepared_column)
            elif column == prepared_column:
                info_data_frame[column] = prepared_data_frame[prepared_column]

    #columns_for_model = [column for column in columns if column in selected_columns]
    print (columns_for_model)

    features_data_frame = pd.DataFrame()
    for column in columns_for_model:
        features_data_frame[column] = prepared_data_frame[column]

    clustering_kmeans = KMeans(n_clusters=numberOfClusters, precompute_distances='auto')
    features_data_frame['clusters'] = clustering_kmeans.fit_predict(features_data_frame)
    features_data_frame.to_csv('kmeans.csv')

    reduced_data = PCA(n_components=2).fit_transform(features_data_frame)
    results = pd.DataFrame(reduced_data, columns=['pca1', 'pca2'])
    info_data_frame['pca1'] = results['pca1']
    info_data_frame['pca2'] = results['pca2']
    info_data_frame['clusters'] = features_data_frame['clusters']
    results.to_csv('pca.csv')


    cluster_colors = [list(np.random.choice(range(256), size=3)) for _ in range(numberOfClusters)]
    cluster_colors = ["#{0:02x}{1:02x}{2:02x}".format(cluster_color[0], cluster_color[1], cluster_color[2]) for cluster_color in cluster_colors]
    colors = []
    for row in info_data_frame['clusters']:
        colors.append(cluster_colors[row])
        #colors.append('red')
    info_data_frame['color']=colors
    print(colors)

    #numinfo_data_frame[['col1', 'col2', 'col3', 'col4']].groupby(['col1', 'col2']).agg(['mean', 'count'])

    output_file("kmeans.html")
    source = ColumnDataSource(info_data_frame)
    tooltips_tuples = []
    for column in list(info_data_frame.columns.values):
        tuple = (column, '@' + column)
        tooltips_tuples.append(tuple)

    hover = HoverTool(tooltips=tooltips_tuples)
    p = figure(plot_width=800, plot_height=800, tools=[hover, BoxZoomTool(), PanTool(), WheelZoomTool()])
    p.circle('pca1', 'pca2', size=7, source=source, color='color', fill_alpha=0.2)

    show(p)


    #sns.scatterplot(x="pca1", y="pca2", hue=features_data_frame['clusters'], data=results)
    #plt.title('K-means Clustering with 2 dimensions')
    #plt.show()

    #centroids = kmeans.cluster_centers_

    #label3 = tk.Label(root, text=centroids)
    #canvas1.create_window(200, 400, window=label3)

    #figure1 = plt.Figure(figsize=(4, 3), dpi=100)
    #ax1 = figure1.add_subplot(111)
    #ax1.scatter(df['x'], df['y'], c=kmeans.labels_.astype(float), s=50, alpha=0.5)
    #ax1.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)
    #scatter1 = FigureCanvasTkAgg(figure1, root)
    #scatter1.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH)


processButton = tk.Button(text=' Process k-Means ', command=getKMeans, bg='brown', fg='white',
                          font=('helvetica', 10, 'bold'))

canvas1.create_window(117, 200, window=CheckBoxColumns(root), anchor='nw')

canvas1.create_window(200, 170, window=processButton)
#CheckBoxColumns(root).pack(side="top")

root.mainloop()