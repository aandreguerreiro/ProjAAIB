import time 
import numpy as np 
import pandas as pd  
import streamlit as st 
import matplotlib.pyplot as plt
from pathlib import Path 
from scipy.signal import butter, lfilter, find_peaks
import paho.mqtt.client as mqtt 
from numpy.fft import fft

broker ="test.mosquitto.org" 
client = mqtt.Client()
client.connect(broker, port=1883) 
fs = 44100


def plot_senogram(data, t):
    fig, ax = plt.subplots() 
    st.write('* ####  Sonograma')
    ax.set_xlabel("Tempo /s")
    ax.set_ylabel("Data")
    ax.set_title("Sonograma", fontsize = 10)
    ax.plot(t,data)
    plt.show()
    st.pyplot(fig) 

def plot_fft(data, fs):
    st.write('* ####  Dominio das frequências')
    X = fft(data)
    N = len(X)
    n = np.arange(N)
    T = N/fs
    freq = n/T 
    n_oneside = N//2
    f_oneside = freq[:n_oneside]
    
    fig, ax = plt.subplots() 
    plt.plot(f_oneside, np.abs(X[:n_oneside]), 'b')
    plt.xlabel('Freq /Hz')
    plt.ylabel('FFT Amplitude')
    ax.set_title("Transformada de Fourier", fontsize = 10)
    plt.show()
    st.pyplot(fig)
    
def plot_spetrogram(data,fs):
    st.write('* ####  Espectrograma')
    fig, ax = plt.subplots(1, figsize=(14, 8))
    fig.tight_layout(pad=10.0)
    ax.specgram(data, Fs=fs)
    ax.set_xlabel(xlabel='Tempo /s')
    ax.set_ylabel(ylabel='Frequência / rad/s')
    helper = [0, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000]
    spec_yticks = [6.28 * i for i in helper]
    ax.set_yticks(helper)
    ax.set_yticklabels(spec_yticks)
    ax.set_title("Espectrograma", fontsize = 10)
    st.pyplot(fig)

def get_data():
    with open("/workspace/ProjAAIB/sounddata.txt","r") as f:
        last_line = f.readlines()[-1]
        return float(last_line[:-1])

st.set_page_config(
    page_title="Aqusição de Áudio", page_icon="sound", initial_sidebar_state="expanded"
)
st.markdown(" # Cloud-Logger de Instrumentação")
st.markdown("")

def publish_status():
    client.publish("Status", st.session_state["start"])

col1, col2, col3= st.columns([1,1,1])
start = col2.button("Iniciar aquisição de sinal")
if start:
    st.session_state['start'] = True
    publish_status()

st.write('___')
my_file = Path("/workspace/ProjAAIB/sounddata.txt")
if my_file.is_file() and 'start' in st.session_state:              
            
    with col1:
        stop=st.button("Stop")
        with col3:
            reset=st.button("Reset")
            if stop:
                st.session_state['start'] = False
                publish_status()
                
    if 'data' not in st.session_state and st.session_state['start'] == True:
            seconds = 0
            df = pd.DataFrame({"data": []})
            plot = st.line_chart(data=None)
               
            while st.session_state['start'] == True:
                new_data = pd.DataFrame({"data": [get_data()]})
                                
                plot.add_rows(new_data)
                
                df = df.append(new_data,ignore_index = True)
                
                time.sleep(0.1)
                seconds += 0.1
        
                st.session_state['data'] = df
    else:
            st.line_chart(st.session_state['data'])
    
    if reset:           
        del st.session_state['data']
        del st.session_state['start']
        with st.sidebar:
            st.error("...data apagada")
   
    with st.sidebar:
            if 'data' in st.session_state:    
                maxp, mediap = st.columns(2)
                maxp.metric(
                    label="Potência Máxima",
                    value=round(st.session_state['data'].max())
                )
                
                mediap.metric(
                    label="Média Potência",
                    value=round(st.session_state['data'].mean())
                )
                
                st.write('___')
                st.write(" # Gravar data?")
                csv = st.session_state['data'].to_csv(index=False).encode('utf-8')
                save = st.download_button( label="Download", data = csv, file_name="sounddata.csv"  )
                if save:
                    with st.sidebar:
                        st.spinner('Saving...')
                        time.sleep(0.5)
                        st.success("Data guardada")
    if 'start' in st.session_state:
        st.header("Features")
        st.write('___')
        
        data = st.session_state['data']['data']
        idx = (st.session_state['data']['data']).index[-1]
        t = np.arange(0, (idx+1)/10, 0.1)
        
        plot_senogram(data,t)
        st.write('___')
        plot_fft(data, fs) 
        st.write('___')
        plot_spetrogram(data, fs)
        st.write('___')

        y = st.session_state['data']['data'].to_numpy()
        idx = (st.session_state['data']['data']).index[-1]
        t = np.arange(0, idx/10, 0.1)


        yd = np.diff(data)
        st.write("* #### Derivada do Sinal")
        fig, ax = plt.subplots(figsize=(10, 6)) 
        ax.set_title("1st derivative", fontsize = 15)
        ax.set_xlabel("Time /s")
        ax.set_ylabel("Amplitude")
        ax.plot(t, yd)
        st.pyplot(fig)
            
