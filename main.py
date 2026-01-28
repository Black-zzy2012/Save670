import os
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from threading import Thread
from datetime import datetime
class PixelLogic:
    @staticmethod
    def DoDither(pic, lv=6):
        # Bayer矩阵
        m = np.array([
            [0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]
        ]) / 16.0
        d = np.array(pic).astype(float) / 255.0
        h, w, c = d.shape
        mm = np.tile(m, (h // 4 + 1, w // 4 + 1))[:h, :w]
        mm = np.repeat(mm[:, :, np.newaxis], 3, axis=2)
        out = np.floor(d * (lv - 1) + mm)
        final = np.clip(out / (lv - 1) * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(final)


class MyCamApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkDnDVersion = TkinterDnD._require(self)
        self.title("LoFiCamSim v1.2")
        self.geometry("850x650")
        self.LangMode = "zh"
        self.MakeUI()

    def MakeUI(self):
        # 侧边栏
        self.A1 = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.A1.pack(side="left", fill="y", padx=10, pady=10)

        self.BtnLang = ctk.CTkButton(self.A1, text="Switch to English", command=self.ChangeLang)
        self.BtnLang.pack(pady=15, padx=20)

        ctk.CTkLabel(self.A1, text="LoFi Cam Sim", font=("Arial", 20)).pack(pady=10)

        self.BtnPick = ctk.CTkButton(self.A1, text="选择图片", command=self.GetFiles)
        self.BtnPick.pack(pady=10, padx=20)

        self.BtnDir = ctk.CTkButton(self.A1, text="选择文件夹", command=self.GetFolder)
        self.BtnDir.pack(pady=10, padx=20)

        self.BtnClean = ctk.CTkButton(self.A1, text="清空状态", fg_color="#555", command=self.ResetText)
        self.BtnClean.pack(pady=10, padx=20)

        self.Txt1 = ctk.CTkLabel(self.A1, text="输出宽度:")
        self.Txt1.pack(pady=(20, 0))
        self.InputW = ctk.CTkEntry(self.A1)
        self.InputW.insert(0, "320")
        self.InputW.pack(pady=5)

        self.Txt2 = ctk.CTkLabel(self.A1, text="色彩级别:")
        self.Txt2.pack(pady=(10, 0))
        self.SliColor = ctk.CTkSlider(self.A1, from_=2, to=12, number_of_steps=10)
        self.SliColor.set(6)
        self.SliColor.pack(pady=5)

        self.Txt3 = ctk.CTkLabel(self.A1, text="风格预设:")
        self.Txt3.pack(pady=(10, 0))
        self.StyleBox = ctk.CTkOptionMenu(self.A1, values=["默认", "冷调紫", "暖阳光"])
        self.StyleBox.pack(pady=5)

        self.CheckDate = ctk.CTkCheckBox(self.A1, text="添加水印")
        self.CheckDate.select()
        self.CheckDate.pack(pady=20)

        # 拖拽区
        self.MainBox = ctk.CTkFrame(self, border_width=1, corner_radius=12)
        self.MainBox.pack(expand=True, fill="both", padx=20, pady=20)
        self.InfoLabel = ctk.CTkLabel(self.MainBox, text="拖到这里或者点左边按钮", font=("Arial", 16))
        self.InfoLabel.place(relx=0.5, rely=0.5, anchor="center")

        self.MainBox.drop_target_register(DND_FILES)
        self.MainBox.dnd_bind('<<Drop>>', self.OnDrop)

    def ChangeLang(self):
        if self.LangMode == "zh":
            self.LangMode, T = "en", "切换至中文"
            self.BtnPick.configure(text="Select Images")
            self.BtnDir.configure(text="Select Folder")
            self.BtnClean.configure(text="Clear")
            self.Txt1.configure(text="Output Width:")
            self.Txt2.configure(text="Color Levels:")
            self.Txt3.configure(text="Presets:")
            self.StyleBox.configure(values=["Standard", "Vintage Purple", "Warm Sunlight"])
            self.StyleBox.set("Standard")
            self.CheckDate.configure(text="Date Stamp")
            self.InfoLabel.configure(text="Drag & Drop or Use Sidebar")
        else:
            self.LangMode, T = "zh", "Switch to English"
            self.BtnPick.configure(text="选择图片")
            self.BtnDir.configure(text="选择文件夹")
            self.BtnClean.configure(text="清空状态")
            self.Txt1.configure(text="输出宽度:")
            self.Txt2.configure(text="色彩级别:")
            self.Txt3.configure(text="风格预设:")
            self.StyleBox.configure(values=["默认", "冷调紫", "暖阳光"])
            self.StyleBox.set("默认")
            self.CheckDate.configure(text="添加水印")
            self.InfoLabel.configure(text="拖到这里或者点左边按钮")
        self.BtnLang.configure(text=T)

    def AddWatermark(self, photo):
        draw = ImageDraw.Draw(photo)
        s = datetime.now().strftime("%Y %m %d")
        try:
            f = ImageFont.truetype("arial.ttf", int(photo.width * 0.04))
        except:
            f = ImageFont.load_default()
        margin = int(photo.width * 0.05)
        draw.text((photo.width - margin * 4, photo.height - margin * 2), s, fill=(255, 120, 0), font=f)
        return photo

    def StupidJpg(self, path):
        try:
            p = Image.open(path).convert("RGB")
            # 风格预设逻辑
            mode = self.StyleBox.get()
            if mode in ["冷调紫", "Vintage Purple"]:
                r, g, b = p.split()
                r = r.point(lambda i: i * 1.05)
                g = g.point(lambda i: i * 0.92)
                b = b.point(lambda i: i * 1.12)
                p = Image.merge("RGB", (r, g, b))
            elif mode in ["暖阳光", "Warm Sunlight"]:
                r, g, b = p.split()
                r = r.point(lambda i: i * 1.1)
                g = g.point(lambda i: i * 1.05)
                b = b.point(lambda i: i * 0.9)
                p = Image.merge("RGB", (r, g, b))

            p = ImageEnhance.Contrast(p).enhance(1.2)
            p = ImageEnhance.Color(p).enhance(1.4)

            w = int(self.InputW.get())
            h = int(p.height * (w / p.width))
            small = p.resize((w, h), Image.BILINEAR)
            pixel = PixelLogic.DoDither(small, lv=int(self.SliColor.get()))
            final = pixel.resize(p.size, Image.NEAREST)

            if self.CheckDate.get(): final = self.AddWatermark(final)

            folder, name = os.path.split(path)
            out = os.path.join(folder, "Converted_Results")
            if not os.path.exists(out): os.makedirs(out)
            final.save(os.path.join(out, f"LOFI_{os.path.splitext(name)[0]}.png"))
            return out
        except:
            return None

    def GoBatch(self, files):
        self.InfoLabel.configure(text="..." if self.LangMode == "en" else "正在搞...")

        def RunJob():
            last, count = None, 0
            for f in files:
                res = self.stupid_process(f) if hasattr(self, 'stupid_process') else self.StupidJpg(f)
                if res: count += 1; last = res
            msg = f"Done: {count}" if self.LangMode == "en" else f"搞定了: {count}"
            self.InfoLabel.configure(text=f"{msg}\n\n-> Converted_Results")
            if last: os.startfile(last)

        Thread(target=RunJob).start()

    def GetFiles(self):
        f = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if f: self.GoBatch(f)

    def GetFolder(self):
        d = filedialog.askdirectory()
        if d:
            f = [os.path.join(d, x) for x in os.listdir(d) if x.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            self.GoBatch(f)

    def ResetText(self):
        self.InfoLabel.configure(
            text="拖到这里或者点左边按钮" if self.LangMode == "zh" else "Drag & Drop or Use Sidebar")

    def OnDrop(self, event):
        raw = event.data
        items = raw.strip('{}').split('} {') if raw.startswith('{') else self.tk.splitlist(raw)
        all_f = []
        for x in items:
            if os.path.isdir(x):
                all_f.extend([os.path.join(x, i) for i in os.listdir(x) if
                              i.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
            else:
                all_f.append(x)
        self.GoBatch(all_f)


if __name__ == "__main__":
    MyCamApp().mainloop()