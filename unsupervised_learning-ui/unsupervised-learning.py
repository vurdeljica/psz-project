import numpy as np
import os.path
import pandas as pd
import tkinter as tk

from bokeh.models import *
from bokeh.plotting import *
from sklearn.cluster import *
from sklearn.decomposition import PCA
from tkinter import filedialog

absolute_path_to_script = os.path.abspath(os.path.dirname(__file__))

checkbox_columns = []
checkbox_values = []
prepared_data_frame = []


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


def get_csv():
    global df
    global checkbox_columns
    global prepared_data_frame
    import_file_path = filedialog.askopenfilename()
    prepared_data_frame = pd.read_csv(import_file_path)
    checkbox_columns = list(prepared_data_frame.columns.values)
    checkbox_columns = list(filter(lambda column: ("generated" not in column) and ("Unnamed" not in column), checkbox_columns))
    canvas1.create_window(117, 250, window=CheckBoxColumns(root), anchor='nw')


def radioButtonAction(param):
    global input_data_label_text
    clustering_alg_name = clustering_algorithm.get()
    if clustering_alg_name == 'kmeans' or clustering_alg_name == 'batch_kmeans':
        input_data_label.config(text="Type Number of Clusters:")
    elif clustering_alg_name == 'mean_shift':
        input_data_label.config(text="Enter quantile:")


def get_input_data():
    input_data = entry1.get()
    if clustering_algorithm.get() == 'kmeans':
        input_data = int(input_data)
    elif clustering_algorithm.get() == 'batch_kmeans':
        input_data = int(input_data)
    elif clustering_algorithm.get() == 'mean_shift':
        input_data = float(input_data)

    return input_data


def get_selected_columns():
    selected_columns = []
    for index, checkbox_value in enumerate(checkbox_values):
        if checkbox_value.get() == True:
            selected_columns.append(checkbox_columns[index])

    return selected_columns


def get_hover_information_data_frame(selected_columns):
    info_data_frame = pd.DataFrame()

    for column in selected_columns:
            info_data_frame[column] = prepared_data_frame[column]

    return info_data_frame


def get_column_names_for_model(selected_columns):
    prepared_columns = list(prepared_data_frame.columns.values)

    columns_for_model = []
    for column in selected_columns:
        for prepared_column in prepared_columns:
            if (column in prepared_column) and (column != prepared_column):
                columns_for_model.append(prepared_column)

    return columns_for_model


def get_features_data_frame(columns_for_model):
    features_data_frame = pd.DataFrame()
    for column in columns_for_model:
        features_data_frame[column] = prepared_data_frame[column]

    return features_data_frame


def get_clustering_algorithm(features_data_frame):
    if clustering_algorithm.get() == 'kmeans':
        clustering_alg = KMeans(n_clusters=input_data, precompute_distances='auto', n_jobs=1)
    elif clustering_algorithm.get() == 'batch_kmeans':
        clustering_alg = MiniBatchKMeans(n_clusters=input_data)
    elif clustering_algorithm.get() == 'mean_shift':
        bandwidth = estimate_bandwidth(features_data_frame, quantile=input_data, n_samples=4000, random_state = 10)
        clustering_alg = MeanShift(bandwidth=bandwidth, bin_seeding=True)

    return clustering_alg


def make_colors_for_each_claster(info_data_frame):
    cluster_colors = [list(np.random.choice(range(256), size=3)) for _ in range(input_data)]
    cluster_colors = ["#{0:02x}{1:02x}{2:02x}".format(cluster_color[0], cluster_color[1], cluster_color[2]) for cluster_color in cluster_colors]
    colors = []
    for row in info_data_frame['clusters']:
        colors.append(cluster_colors[row])
    info_data_frame['color']=colors


def convert_model_from_n_to_2_dimension(features_data_frame, info_data_frame):
    reduced_data = PCA(n_components=2).fit_transform(features_data_frame)
    results = pd.DataFrame(reduced_data, columns=['pca1', 'pca2'])
    info_data_frame['pca1'] = results['pca1']
    info_data_frame['pca2'] = results['pca2']


def visualize_clustering_algorithm(info_data_frame):
    output_file(absolute_path_to_script + '\\results\\' + "clustering.html")
    source = ColumnDataSource(info_data_frame)
    tooltips_tuples = []
    html_tooltips = ""
    for column in list(info_data_frame.columns.values):
        if ("pca" in column) or ("color" in column):
            continue

        html_tooltips += "<b>" + column + ": " + "</b> @" + column + "<br>"
        tuple = (column, '@' + column)
        tooltips_tuples.append(tuple)

    custom_hover = HoverTool()

    custom_hover.tooltips = """
            <style>
                .bk-tooltip>div:not(:first-child) {display:none;}
            </style>

        """ + html_tooltips

    p = figure(plot_width=2000, plot_height=800, tools=[custom_hover, BoxZoomTool(), PanTool(), WheelZoomTool()],
               output_backend='webgl')

    p.sizing_mode = 'scale_width'

    p.circle('pca1', 'pca2', size=5, source=source, color='color', fill_alpha=0.2)

    show(p)


def getKMeans():
    global df
    global input_data
    global checkbox_columns
    global checkbox_values

    input_data = get_input_data()

    selected_columns = get_selected_columns()

    info_data_frame = get_hover_information_data_frame(selected_columns)

    columns_for_model = get_column_names_for_model(selected_columns)

    features_data_frame = get_features_data_frame(columns_for_model)

    clustering_alg = get_clustering_algorithm(features_data_frame)

    features_data_frame['clusters'] = clustering_alg.fit_predict(features_data_frame)
    info_data_frame['clusters'] = features_data_frame['clusters']
    if clustering_algorithm.get() == 'mean_shift':
        input_data = len(np.unique(clustering_alg.labels_))

    convert_model_from_n_to_2_dimension(features_data_frame, info_data_frame)

    make_colors_for_each_claster(info_data_frame)

    visualize_clustering_algorithm(info_data_frame)


root = tk.Tk()
clustering_algorithm = tk.StringVar()

canvas1 = tk.Canvas(root, width=400, height=525, relief='raised')
canvas1.pack()


label1 = tk.Label(root, text='Clustering algorithms')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 20, window=label1)


browseButtonExcel = tk.Button(text=" Import Excel File ", command=get_csv, bg='green', fg='white',
                              font=('helvetica', 10, 'bold'))
canvas1.create_window(200, 60, window=browseButtonExcel)


kmeans_radio_button = tk.Radiobutton(root, text='Kmeans', value='kmeans', var=clustering_algorithm,
                                     command=lambda: radioButtonAction(None))
mini_batch_kmeans_radio_button = tk.Radiobutton(root, text='Batch Kmeans', value='batch_kmeans',
                                                var=clustering_algorithm, command=lambda: radioButtonAction(None))
mean_shift_radio_button = tk.Radiobutton(root, text='Mean Shift', value='mean_shift',
                                           var=clustering_algorithm, command=lambda: radioButtonAction(None))
clustering_algorithm.set("kmeans")
canvas1.create_window(100, 110, window=kmeans_radio_button)
canvas1.create_window(200, 110, window=mini_batch_kmeans_radio_button)
canvas1.create_window(300, 110, window=mean_shift_radio_button)


input_data_label = tk.Label(root, text='Type Number of Clusters:')
input_data_label.config(font=('helvetica', 9))
canvas1.create_window(200, 150, window=input_data_label)


entry1 = tk.Entry(root)
canvas1.create_window(200, 175, window=entry1)


processButton = tk.Button(text=' Process', command=getKMeans, bg='brown', fg='white',
                          font=('helvetica', 10, 'bold'))
canvas1.create_window(200, 210, window=processButton)


canvas1.create_window(117, 250, window=CheckBoxColumns(root), anchor='nw')


root.mainloop()