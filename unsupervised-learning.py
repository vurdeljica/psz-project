import tkinter as tk
from tkinter import filedialog
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

checkbox_columns = ['pera', 'mika', 'zika']
checkbox_values = []

class CheckBoxColumns(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        global checkbox_columns
        global checkbox_values
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=20, height=10,
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for index, column in enumerate(checkbox_columns):
            var = tk.BooleanVar()
            var.set(True)
            checkbox_values.append(var)
            cb = tk.Checkbutton(self, text=column, variable=var)
            cb.config(background='white', activebackground='white')
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n")  # to force one checkbox per line

root = tk.Tk()

canvas1 = tk.Canvas(root, width=400, height=400, relief='raised')
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
    import_file_path = filedialog.askopenfilename()
    #read_file = pd.read_excel(import_file_path)
    #df = DataFrame(read_file, columns=['x', 'y'])
    df = pd.read_csv(import_file_path)
    checkbox_columns = list(df.columns.values)
    canvas1.create_window(117, 200, window=CheckBoxColumns(root), anchor='nw')


browseButtonExcel = tk.Button(text=" Import Excel File ", command=getExcel, bg='green', fg='white',
                              font=('helvetica', 10, 'bold'))
canvas1.create_window(200, 70, window=browseButtonExcel)

def getKMeans():
    global df
    global numberOfClusters
    #numberOfClusters = int(entry1.get())

    #kmeans = KMeans(n_clusters=numberOfClusters).fit(df)
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