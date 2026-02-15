import ttkbootstrap as tb
from ui import BinauralBeatApp

def main():
    root = tb.Window(themename="darkly")
    app = BinauralBeatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
