from Tkinter import *
from ttk import Progressbar
import Tkinter, Tkconstants, tkFileDialog

import numpy as np
from lib import GEM_COM_classes as COM_class
import binascii
from multiprocessing import Process,Pipe
import time
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array
import pickle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()
class menu():
    def __init__(self,main_window,gemroc_handler):
        self.scan_matrixs={}
        self.GEMROC_reading_dict=gemroc_handler
        self.error_window_main = Toplevel(main_window)
        self.error_window=Frame(self.error_window_main)
        self.error_window.pack(side=LEFT,pady=10,padx=10)

        Label(self.error_window,text='Noise measure',font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4,columnspan=10)
        tot=len(self.GEMROC_reading_dict)

        self.TD_scan_result={}
        number_list=[]
        i=0
        self.first_row=Frame(self.error_window)
        self.first_row.grid(row=1, column=1, sticky=S, pady=4,columnspan=10)

        self.plotting_gemroc = 0
        self.plotting_TIGER = 0
        self.plotting_Channel = 0

        self.second_row_frame=Frame(self.error_window)
        self.second_row_frame.grid(row=2, column=1, sticky=S, pady=4,columnspan=10)


        self.GEMROC_num = StringVar(self.error_window)
        self.TIGER_num_first = IntVar(self.error_window)
        self.TIGER_num_last = IntVar(self.error_window)
        self.CHANNEL_num_first = IntVar(self.error_window)
        self.CHANNEL_num_last = IntVar(self.error_window)



        Label(self.second_row_frame, text='First TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='First Channel  ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last Channel   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_last).pack(side=LEFT)


        fields_optionsG = self.GEMROC_reading_dict.keys()
        fields_optionsG.append("All")
        OptionMenu(self.first_row, self.GEMROC_num, *fields_optionsG).pack(side=LEFT)
        self.third_row=Frame(self.error_window)
        self.third_row.grid(row=3, column=1, sticky=S, pady=4,columnspan=10)
        Button(self.third_row, text ='Start TP',  command=self.start_TP).pack(side=LEFT)

        Button(self.third_row, text ='Threshold scan',  command=self.noise_scan).pack(side=LEFT)
        Button(self.third_row, text="Load from file last scan", command=self.LOAD).pack(side=LEFT)

        self.corn0 = Frame(self.error_window)
        self.corn0.grid(row=4, column=0, sticky=S, pady=4,columnspan=10)
        self.LBOCC = Label(self.corn0, text='Threshold scan', font=("Times", 18))
        self.LBOCC.grid(row=0, column=1, sticky=S, pady=4)
        self.butleftG = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM = Label(self.corn0, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 12))
        self.LBGEM.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)
        self.butleftT = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "T")).grid(row=2, column=0, sticky=S, pady=4)
        self.LBTIG = Label(self.corn0, text='TIGER {}'.format(self.plotting_TIGER), font=("Courier", 12))
        self.LBTIG.grid(row=2, column=1, sticky=S, pady=4)
        self.butrightT = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "T")).grid(row=2, column=2, sticky=S, pady=4)

        self.usefullframe=Frame(self.corn0)
        self.usefullframe.grid(row=3, column=1, sticky=S, pady=4)
        Button(self.usefullframe, text='<', command=lambda: self.change_G_or_T(-1, "C")).grid(row=0, column=0, sticky=S, pady=4)

        self.LBCH = Label(self.usefullframe, text='CHANNEL ', font=("Courier", 12))
        self.LBCH.grid(row=0, column=1, sticky=S, pady=4)
        self.CHentry=Entry(self.usefullframe,textvariable=self.plotting_Channel,width=4)
        self.CHentry.grid(row=0, column=2, sticky=S, pady=4)
        Button(self.usefullframe, text='Go', command=lambda: self.change_G_or_T(1, "GO")).grid(row=0, column=3, sticky=S, pady=4)
        Button(self.usefullframe, text='>', command=lambda: self.change_G_or_T(1, "C")).grid(row=0, column=4, sticky=S, pady=4)

        self.corn1 = Frame(self.error_window)
        self.corn1.grid(row=12, column=1, sticky=S, pady=4,columnspan=100)

        # Plot
        x = np.arange(0, 64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(6,6))
        self.plot_rate = self.fig.add_subplot(111)
        self.scatter, = self.plot_rate.plot(x, v, 'r+')
        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
        self.plot_rate.set_ylabel("Rate [Hz]", fontsize=14)
        self.plot_rate.set_xlabel("Thresnold", fontsize=14)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.corn1)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.corn1)
        self.toolbar.draw()
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            self.scan_matrixs[number]=np.zeros((8,64,64))

        # self.Conf_Frame=Frame(self.error_window_main)
        # self.Conf_Frame.pack(side=LEFT,pady=10,padx=20)
        # Global_frame=LabelFrame(self.Conf_Frame)
        # Global_frame.grid(row=0,column=0,sticky=N,pady=10,padx=10)
        # Label(Global_frame,text="Global configurations").pack()
        # fields_frame=Frame(Global_frame)
        # fields_frame.pack()
        # with open("lib" + sep + "keys" + sep + "global_conf_file_keys", 'r') as f:
        #     i = 0
        #     lenght = len(f.readlines())
        #     # print lenght
        #     f.seek(0)
        #     Label(fields_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0)
        #     Label(fields_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0)
        #     Label(fields_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0)
        #     Label(fields_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0)
        #
        #     for line in f.readlines():
        #         self.field_array.append(Label(fields_frame, text='-'))
        #         self.input_array.append(Entry(fields_frame, width=3))
        #         self.label_array.append(Label(fields_frame, text=line))
        #
        #         if i < lenght / 2:
        #             self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
        #             self.input_array[i].grid(row=i + 2, column=2, sticky=W, pady=0)
        #             self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
        #         else:
        #             self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
        #             self.input_array[i].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
        #             self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)
        #
        #         i += 1
        #
        #
        #
        # ChannelFrame=LabelFrame(self.Conf_Frame)
        # ChannelFrame.grid(row=0,column=1,sticky=N,pady=10,padx=10)
        # Label(ChannelFrame,text="Channel configurations").pack()


    def noise_scan(self):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.error_window)
        #self.bar_win.focus_set()  # set focus on the ProgressWindow
        #self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dictio = {}
        GEMROC_n=self.GEMROC_num.get()
        Label(self.bar_win, text="Threshold Scan completition").pack()

        if GEMROC_n == "All":
            dictio = self.GEMROC_reading_dict.copy()
        else:
            dictio["{}".format(GEMROC_n)] = self.GEMROC_reading_dict[GEMROC_n]
        i = 0
        for number, GEMROC_number in dictio.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            maxim = ((self.CHANNEL_num_last.get()-self.CHANNEL_num_first.get()))*(self.TIGER_num_last.get()-self.TIGER_num_first.get())
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dictio.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.noise_scan_process, args=(number,  pipe_out))
            # pipe_in.send(progress_bars[i])
            process_list.append(p)
            pipe_list.append(pipe_in)
            p.start()
            i += 1
        while True:
            alive_list = []
            for process in process_list:
                alive_list.append(process.is_alive())
            if all(v == False for v in alive_list):
                break
            else:
                for progress, pipe in zip(progress_list, pipe_list):
                    try:
                        progress.set(pipe.recv())
                    except:
                        Exception("Can't acquire status")
                        #print ("Can't acquire status")

                    self.bar_win.update()
                    time.sleep(0.1)
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()
        for number, GEMROC_num in dictio.items():
            filename=GEMROC_num.GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_num.GEM_COM.GEMROC_ID) + sep +"scan_matrix"
            with  open(filename, 'rb') as f:
                self.scan_matrixs[number]=pickle.load(f)
        self.plotta()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def noise_scan_process(self, number,  pipe_out):
        scan_matrix=np.zeros((8,64,64))
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        first = self.TIGER_num_first.get()
        last = self.TIGER_num_last.get()+1
        firstch = self.CHANNEL_num_first.get()
        lastch = self.CHANNEL_num_last.get()+1
        GEMROC_ID = GEM_COM.GEMROC_ID



        for T in range(first,last):#TIGER
            for J in range (firstch,lastch):#Channel
                for i in range (0,64):#THR
                    scan_matrix[T,J,i]=test_c.noise_scan_using_GEMROC_COUNTERS_progress_bar(T,J, i,False)
                position = (T * 64+1) + (J)
                pipe_out.send(position)


        test_r.thr_scan_matrix=scan_matrix
        test_r.thr_scan_rate=scan_matrix*10
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "rate", first, last, True)
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "conteggi", first, last)

        filename=GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep +"scan_matrix"
        with  open(filename,'wb') as f:
            pickle.dump(test_r.thr_scan_rate,f)


        print "GEMROC {} done".format(GEMROC_ID)
        position = (last * 64 + 1) + (lastch)
        pipe_out.send(position)

    def change_G_or_T(self, i, G_or_T):
        if G_or_T == "G":
            self.plotting_gemroc = self.plotting_gemroc + i
            if self.plotting_gemroc == -1:
                self.plotting_gemroc = 0
            if self.plotting_gemroc == 20:
                self.plotting_gemroc = 19

        if G_or_T == "T":
            self.plotting_TIGER = self.plotting_TIGER + i
            if self.plotting_TIGER == -1:
                self.plotting_TIGER = 0
            if self.plotting_TIGER == 8:
                self.plotting_TIGER = 7

        if G_or_T == "C":
            self.plotting_Channel = self.plotting_Channel + i
            if self.plotting_Channel < 0:
                self.plotting_Channel = 0
            if self.plotting_Channel > 63:
                self.plotting_Channel = 63
        if G_or_T == "GO":
            self.plotting_Channel=int(self.CHentry.get())

        self.refresh_plot()


    def refresh_plot(self):
        self.LBGEM['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text'] = 'TIGER {}'.format(self.plotting_TIGER)
        # self.LBCH['text'] = 'CHANNEL {}'.format(self.plotting_Channel)
        self.CHentry.delete(0,END)
        self.CHentry.insert(END,self.plotting_Channel)
        self.plotta()
    def start_TP(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            GEMROC_number.GEM_COM.Soft_TP_generate(5)
    def plotta(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            if int(number.split()[1]) == int(self.plotting_gemroc):
                print self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel]

                self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
                self.scatter.set_ydata(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])
                self.plot_rate.set_ylim(top=np.max(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])+ np.max(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])*0.2)
                break
            else:
                self.plot_rate.set_title("GEMROC not active")
                self.scatter.set_ydata(np.zeros((64)))
        self.canvas.draw()
        self.canvas.flush_events()
    def SAVE(self):
        dictio={}
        GEMROC_n=self.GEMROC_num.get()
        Label(self.bar_win, text="Threshold Scan completition").pack()

        if GEMROC_n == "All":
            dictio = self.GEMROC_reading_dict.copy()

            self.scan_matrixs
        else:
            dictio["{}".format(GEMROC_n)] = self.GEMROC_reading_dict[GEMROC_n]


    def LOAD(self):
        filename = tkFileDialog.askopenfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))

        for number, GEMROC_num in self.GEMROC_reading_dict.items():
            try:
                with  open(filename, 'rb') as f:
                    self.scan_matrixs[number]=pickle.load(f)
            except:
                print ("No file found for {}".format(number))