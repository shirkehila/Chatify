import tkinter as tk
from operator import itemgetter

# Define the data points


class Bar(tk.Frame):
    def __init__(self, master, data, topic, t_words):
        tk.Frame.__init__(self, master)
        c_width = 30 + 30*len(data)  # Define it's width
        print(data)
        c_height = 140  # Define it's height
        c = tk.Canvas(self, width=c_width, height=c_height, bg='white')
        c.pack()
        words = tk.Text(self, height=4, width=45, wrap=tk.WORD)
        words.insert(tk.END, "File will be classified to topic {}\n".format(str(topic)))
        words.insert(tk.END, "Defined by words: {}".format(t_words))
        words.configure(state=tk.DISABLED)
        words.pack()
        # The variables below size the bar graph
        y_stretch = 100  # The highest y = max_data_value * y_stretch
        y_gap = 20  # The gap between lower canvas edge and x axis
        x_stretch = 10  # Stretch x wide enough to fit the variables
        x_width = 20  # The width of the x-axis
        x_gap = 20  # The gap between left canvas edge and y axis

        # A quick for loop to calculate the rectangle
        for x, y in data:
            p = data.index((x,y))
            p, x = x, p
            print(p)
            # coordinates of each bar

            # Bottom left coordinate
            x0 = x * x_stretch + x * x_width + x_gap

            # Top left coordinates
            y0 = c_height - (y * y_stretch + y_gap)

            # Bottom right coordinates
            x1 = x * x_stretch + x * x_width + x_width + x_gap

            # Top right coordinates
            y1 = c_height - y_gap

            # Draw the bar
            c.create_rectangle(x0, y0, x1, y1, fill="red")

            # Put the y value above the bar
            c.create_text(x0, y0, anchor=tk.SW, text="{0:.2f}".format(y))
            c.create_text(x0+int((x_width-len(str(x)*6))/2), y1+20, anchor=tk.SW, text=str(p))

