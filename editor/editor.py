from tkinter import filedialog, messagebox
import tkinter as tk
import tkinter.ttk as ttk
import os
import platform
import subprocess
import math
import json

if platform.system() == "Darwin":
    ctrl_key = "Command"
else:
    ctrl_key = "Control"

class PreferencesScreen:
    def __init__(self, p) -> None:
        self.wnd = tk.Toplevel()
        self.wnd.title("Preferences")
        self.wnd.option_add("*Font", "18")
        self.wnd.minsize(300, 200)

        self._defStyle = ttk.Style()
        self._defStyle.configure("editor.TButton", font=("Courier", 11))

        self._fontVar = None
        self._themeVar = None
        self._pyOptionTextbox = None
        self._applyButton = ttk.Button(self.wnd, text = "Apply Changes", style="editor.TButton")

        self._themeDict = dict()

        self._preferences = p


    def showWindow(self) -> None:
        self._makeUI()
        self.wnd.mainloop()


    def getSettingsCommand(self, editor) -> None:
        self._applyButton.config(command=lambda: editor.applySettings(
            {
                "fontSize": int(self._fontVar.get()),
                "theme" : self._themeDict[self._themeVar.get()],
                "pyinterp": self._pyOptionTextbox.get()
            }
        ))


    def _makeFontFrame(self) -> None:
        fontFrame = tk.Frame(self.wnd)

        fontOptions = ["12", "14", "16", "18", "20", "24"]
        self._fontVar = tk.StringVar(self.wnd)
        self._fontVar.set(str(self._preferences["fontSize"]))

        fontLabel = tk.Label(fontFrame, text="Font Size: ")
        fontMenu = ttk.OptionMenu(fontFrame, self._fontVar, str(self._preferences["fontSize"]), *fontOptions)

        fontLabel.pack(side="left")
        fontMenu.pack(side="right")
        fontFrame.pack(padx=30,pady=20)


    def _makeThemeFrame(self) -> None:
        themeFrame = tk.Frame(self.wnd)

        themeOptions = []
        
        files = tuple(os.walk(f"{os.getcwd().replace(os.sep, '/')}/editor/theme"))[0][-1]
        for i in files:
            f = open(f"{os.getcwd().replace(os.sep, '/')}/editor/theme/{i}")
            name = json.loads(f.read())["name"]
            themeOptions.append(name)
            self._themeDict[name] = i
            f.close()

        self._themeVar = tk.StringVar(self.wnd)
        self._themeVar.set(str(self._preferences["theme"]))

        f = open(f'{os.getcwd().replace(os.sep, "/")}/editor/theme/{self._preferences["theme"]}')
        themeLabel = tk.Label(themeFrame, text="Theme: ")
        themeMenu = ttk.OptionMenu(themeFrame, self._themeVar, json.loads(f.read())["name"], *themeOptions)
        f.close()

        themeLabel.pack(side="left")
        themeMenu.pack(side="right")
        themeFrame.pack(padx=50,pady=20)


    def _makePyInterpreterOptionFrame(self) -> None:
        pyOptionFrame = tk.Frame(self.wnd)
        pyOptionLabel = tk.Label(pyOptionFrame, text="Python interpreter: ")

        self._pyOptionTextbox = tk.Entry(pyOptionFrame)
        self._pyOptionTextbox.delete(0, tk.END)
        self._pyOptionTextbox.insert(0, self._preferences["pyinterp"])

        pyOptionLabel.pack()
        self._pyOptionTextbox.pack(ipady=5, ipadx=5)
        pyOptionFrame.pack(pady=20)

    def _makeUI(self) -> None:
        self._makeFontFrame()
        self._makeThemeFrame()
        self._makePyInterpreterOptionFrame()
        self._applyButton.pack(ipady=5, ipadx=5, pady=20)

    def handleCloseFunction(self, f) -> None:
        self.wnd.protocol("WM_DELETE_WINDOW", lambda: f(self.wnd))

class Editor:
    def __init__(self) -> None:
        self._rootWnd = tk.Tk()
        self._rootWnd.title("untitled")
        self._curOpenFile = "untitled"
        self._curFileIsSaved = False

        # default preferences
        self._preferences = {
            "fontSize": 16,
            "pyinterp": "python",
            "theme": "defaultDark.json"
        }
        self._loadPreferences()
        self._prefWindowIsOpen = False

        # default dark theme
        self._theme = {
            "name": "default dark",
            "background": "#030d22",
            "foreground": "#ffffff",
            "selectBackground": "#35008b",
            "inactiveselectbackground": "#310072",
            "cursorColor": "#ee0077",
            "keywords": "#ff2cf1",
            "functionName": "#ffd400",
            "strings": "#0ef3ff",
            "comments": "#0098df"
        }
        self._loadTheme()

        self._menuBar = tk.Menu(self._rootWnd)
        self._textArea = tk.Text(self._rootWnd, borderwidth=0,
            insertbackground=self._theme["cursorColor"],
            bg=self._theme["background"],
            fg=self._theme["foreground"],
            font=("Consolas", self._preferences["fontSize"]),
            selectbackground=self._theme["selectBackground"],
            inactiveselectbackground=self._theme["inactiveselectbackground"]
        )

        self._textArea.bind("<KeyRelease>", self._handleKeyRelease)

        self._textArea.bind(f"<{ctrl_key}-Key-s>", self._saveFile)
        self._textArea.bind(f"<{ctrl_key}-Key-o>", self._openFile)
        self._textArea.bind("<Tab>", self._tab)
        self._textArea.bind("<Shift-Tab>", self._shiftTab)

        self._colorTokens = {
            "fun", "if", "else", "elsif", "for", "while", 
            "return",  "var", "true", "false", "continue", "break",
            "=",  "==", ">", ">=", "<", "<=", "!", "!=", "+", "-", "*", "/"
        }

    def _tab(self, e) -> str:
        try:
            start = self._textArea.index(tk.SEL_FIRST)
            start = f"{start[:start.index('.')]}.0"

            end = self._textArea.index(tk.SEL_LAST)
            end = f"{end[:end.index('.')]}.250"

            selected = self._textArea.get(start, end)
            selected = selected.split('\n')
        except:
            selected = None

        if selected:        
            for k,l in enumerate(selected):
                i = 0
                while i <= len(l):
                    if i >= 4:
                        break
                    selected[k] = ' ' + selected[k]
                    i += 1
            
            output = ''
            for i in selected:
                output += i + '\n'

            self._textArea.delete(start, end)
            self._textArea.insert(start, output)
            self._textArea.mark_set(tk.INSERT, start)
            self._textArea.tag_add("sel", start, end)
        else:
            self._textArea.insert(tk.INSERT, " "*4)
        return "break"

    def _shiftTab(self, e) -> str:
        try:
            start = self._textArea.index(tk.SEL_FIRST)
            start = f"{start[:start.index('.')]}.0"

            end = self._textArea.index(tk.SEL_LAST)
            end = f"{end[:end.index('.')]}.250"

            selected = self._textArea.get(start, end)
            selected = selected.split('\n')
        except:
            selected = None
        
        if selected:
            for k,l in enumerate(selected):
                i = 0
                while i <= len(l):
                    if i >= 4:
                        break
                    if len(selected[k]) > 0 and selected[k][0] == ' ':
                        selected[k] = selected[k][1:]
                    i += 1
            
            output = ''
            for i in selected:
                output += i + '\n'

            self._textArea.delete(start, end)
            self._textArea.insert(start, output)
            self._textArea.mark_set(tk.INSERT, start)
            self._textArea.tag_add("sel", start, end)
        else:
            end: str = self._textArea.index(tk.INSERT)
            start = f"{end[:end.index('.')]}.{int(end[end.index('.')+1:])-4}"
            self._textArea.delete(start, end)

        return "break"
        

    def showWindow(self) -> None:
        self._makeUI()
        self._rootWnd.mainloop()

    def _makeUI(self) -> None:
        self._makeMenu()
        self._makeTextArea()

    # menu bar
    def _makeMenu(self) -> None:
        fileMenu = tk.Menu(self._menuBar, tearoff=0)
        fileMenu.add_command(label="Open", command=self._openFile)
        fileMenu.add_command(label="Save", command=self._saveFile)
        fileMenu.add_command(label="Save As", command=self._saveAsFile)
        self._menuBar.add_cascade(label = "File", menu=fileMenu)

        runMenu = tk.Menu(self._menuBar, tearoff=0)
        runMenu.add_command(label="Run", command=self._runProgram)
        runMenu.add_command(label="Run (debug)", command=self._runDebug)
        self._menuBar.add_cascade(label = "Run", menu=runMenu)

        settingsMenu = tk.Menu(self._menuBar, tearoff=0)
        settingsMenu.add_command(label="Preferences", command=self._showPreferences)
        self._menuBar.add_cascade(label = "Options", menu=settingsMenu)

        self._rootWnd.config(menu=self._menuBar)

    def _makeTextArea(self) -> None:
        self._textArea.pack(expand=True, fill=tk.BOTH)


    def _prefWindowIsClosed(self, w) -> None:
        w.destroy()
        self._prefWindowIsOpen = False

    def _showPreferences(self) -> None:
        if not self._prefWindowIsOpen:
            self._prefWindowIsOpen = True
            self._loadPreferences()

            p = PreferencesScreen(self._preferences)
            
            p.getSettingsCommand(self)
            p.handleCloseFunction(self._prefWindowIsClosed)
            p.showWindow()

    def _savePreferences(self, s) -> None:
        self._preferences = s

        if "data" not in list(os.walk(f"{os.getcwd().replace(os.sep, '/')}/editor"))[0][1]:
            os.mkdir(f"{os.getcwd().replace(os.sep, '/')}/editor/data")

        with open(f"{os.getcwd().replace(os.sep, '/')}/editor/data/preferences.json", "w+") as f:
            f.write(json.dumps(
                s,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            ))


    def _loadPreferences(self) -> None:
        if "data" not in list(os.walk(f"{os.getcwd().replace(os.sep, '/')}/editor"))[0][1]:
            os.mkdir(f"{os.getcwd().replace(os.sep, '/')}/editor/data")
        
        try:
            with open(f"{os.getcwd().replace(os.sep, '/')}/editor/data/preferences.json") as f:
                self._preferences = json.loads(f.read())
        except FileNotFoundError:
            with open(f"{os.getcwd().replace(os.sep, '/')}/editor/data/preferences.json", "w+") as f:
                f.write(json.dumps(
                    self._preferences,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                ))

    def _loadTheme(self) -> None:
        if "theme" not in list(os.walk(f"{os.getcwd().replace(os.sep, '/')}/editor"))[0][1]:
            os.mkdir(f"{os.getcwd().replace(os.sep, '/')}/editor/theme")

        path: str = f'{os.getcwd().replace(os.sep, "/")}/editor/theme/{self._preferences["theme"]}'
        
        with open(path) as f:
            self._theme = json.loads(f.read())

    def _applyTheme(self, theme) -> None:
        self._textArea.config(
            insertbackground=theme["cursorColor"],
            bg=theme["background"],
            fg=theme["foreground"],
            selectbackground=theme["selectBackground"],
            inactiveselectbackground=theme["inactiveselectbackground"]
        )
        self._highlight()

    def applySettings(self, s) -> None:
        self._savePreferences(s)
        self._textArea.config(font=("Consolas", s["fontSize"]))

        self._loadTheme()
        self._applyTheme(self._theme)


    def _handleKeyRelease(self, e) -> None:
        self._autoCompleteAndFormat(e)
        self._changeTitleOnSave()
        self._highlight()
    
    # auto complete and format code
    def _autoCompleteAndFormat(self, e) -> None:
        self._autoComplete(e)
        self._autoformat(e)

    def _autoComplete(self, e) -> None:
        if e.char in ['(', '{', '[', "'", '"']:
            p = self._textArea.index(tk.INSERT)

            if e.char == '(':
                self._textArea.insert(tk.INSERT, ')')
            if e.char == '{':
                self._textArea.insert(tk.INSERT, '}')
            if e.char == '[':
                self._textArea.insert(tk.INSERT, ']')
            if e.char == '"':
                self._textArea.insert(tk.INSERT, '"')
            if e.char == "'":
                self._textArea.insert(tk.INSERT, "'")

            self._textArea.mark_set(tk.INSERT, p)

    def _autoformat(self, e) -> None:
        if e.char == '\r':
            cur = self._textArea.index(tk.INSERT)
            line = math.floor(float(cur))

            fulltxt = self._textArea.get("1.0", tk.END).split('\n')

            while fulltxt[-1] == '':
                fulltxt.pop()
                if len(fulltxt) == 0:
                    return

            spaceCount = 0
            if not (line-2) >= len(fulltxt):
                for c in fulltxt[line-2]:
                    if c == ' ':
                        spaceCount += 1
                    else:
                        break
                
            for _ in range(spaceCount):
                self._textArea.insert(tk.INSERT, ' ')
                
            if (line-2) >= len(fulltxt):
                return 
            try:
                if fulltxt[line-2][-1] == '{':
                    cur = self._textArea.index(tk.INSERT)
                    line = int(float(cur))
                    char = int(cur[cur.index('.')+1:])
                    self._textArea.delete(f"{line}.{char}")
                    cur = self._textArea.index(tk.INSERT)
                    
                    insertStr = ""
                    for _ in range(spaceCount):
                        insertStr += ' '
                    insertStr += "    \n"
                    
                    for _ in range(spaceCount):
                        insertStr += ' '
                    insertStr += '}'

                    self._textArea.insert(cur, insertStr)

                    line = int(float(cur))
                    char = int(cur[cur.index('.')+1:])
                    self._textArea.mark_set(tk.INSERT, f"{line}.{char+4}")
            except:
                pass
    # end auto complete and format code


    def _changeTitleOnSave(self) -> None:
        # change title and set state if file is not saved
        if not self._curFileIsSaved:
            self._rootWnd.title(self._curOpenFile + '*')
            
        if self._curFileIsSaved:
            f = open(self._curOpenFile)
            s = f.read()
            f.close()
            text = self._textArea.get("1.0", tk.END)
            if s != text:
                self._curFileIsSaved = False

    def _highlight(self) -> None:
        self._highlightTokens()
        self._highlightStrings()
        self._highlightFuncName()
        self._highlightComments()

    def _highlightTokens(self) -> None:
        for i in self._colorTokens:
            try:
                pos = self._textArea.search(i, "1.0", stopindex="end")
                line = int(float(pos))
                char = int(pos[pos.index('.')+1:])
                self._textArea.tag_configure(i, foreground=self._theme["keywords"])

                end = f"{line}.{char+len(i)}"

                while pos:
                    self._textArea.tag_add(i, pos, end)
                    pos = self._textArea.search(i, end, stopindex="end")
                    line = int(float(pos))
                    char = int(pos[pos.index('.')+1:])
                    end = f"{line}.{char+len(i)}"

            except:
                pass

    def _highlightStrings(self) -> None:
        # highlight string
        try:
            cVar = tk.IntVar()
            pos = self._textArea.search(r'".*\s*"', "1.0", stopindex="end", count=cVar, regexp=True)
            line = int(float(pos))
            char = int(pos[pos.index('.')+1:])
            self._textArea.tag_configure("str", foreground=self._theme["strings"])

            end = f"{line}.{char+cVar.get()}"

            while pos:
                self._textArea.tag_add("str", pos, end)
                pos = self._textArea.search(r'".*\s*"', end, stopindex="end")
                line = int(float(pos))
                char = int(pos[pos.index('.')+1:])
                end = f"{line}.{char+cVar.get()}"
        except:
            pass

    def _highlightFuncName(self) -> None:
        # highlight function name
        try:
            cVar = tk.IntVar()
            pos = self._textArea.search(r'\w+\s*\(', "1.0", stopindex="end", count=cVar, regexp=True)
            line = int(float(pos))
            char = int(pos[pos.index('.')+1:])
            self._textArea.tag_configure("fnname", foreground=self._theme["functionName"])

            end = f"{line}.{char+cVar.get()-1}"

            while pos:
                if self._textArea.get(pos, end) not in self._colorTokens:
                    self._textArea.tag_add("fnname", pos, end)
                pos = self._textArea.search(r'\w+\s*\(', end, stopindex="end", count=cVar, regexp=True)
                line = int(float(pos))
                char = int(pos[pos.index('.')+1:])
                end = f"{line}.{char+cVar.get()-1}"
        except:
            pass

    def _highlightComments(self) -> None:
        self._highlightSingleLineComments()
        self._highlightMultiLineComments()

    def _highlightSingleLineComments(self) -> None:
        try:
            cVar = tk.IntVar()
            pos = self._textArea.search(r'\/\/[^\n\r]*', "1.0", stopindex="end", count=cVar, regexp=True)
            line = int(float(pos))
            char = int(pos[pos.index('.')+1:])
            self._textArea.tag_configure("scomment", foreground=self._theme["comments"])

            end = f"{line}.{char+cVar.get()}"

            while pos:
                self._textArea.tag_add("scomment", pos, end)
                pos = self._textArea.search(r'\/\/[^\n\r]*', end, stopindex="end", count=cVar, regexp=True)
                line = int(float(pos))
                char = int(pos[pos.index('.')+1:])
                end = f"{line}.{char+cVar.get()}"
        except:
            pass
    
    # this doesn't work all the time
    def _highlightMultiLineComments(self) -> None:
        try:
            cVar = tk.IntVar()
            
            # these didn't work  
            # \/\*[\s\S]*\*\/
            # \/\*[^*]*\**(?:[^/*][^*]*\*+)*(\/)?
            pos = self._textArea.search(r"\/\*\s*\S*\*\/", "1.0", stopindex="end", count=cVar, regexp=True)
            
            line = int(float(pos))
            char = int(pos[pos.index('.')+1:])

            fulltxt = self._textArea.get("1.0", tk.END).split('\n')
            while fulltxt[-1] == '':
                fulltxt.pop()

            self._textArea.tag_configure("mcomment", foreground=self._theme["comments"])
            end = f"{line}.{char+cVar.get()}"
            

            if (char+cVar.get()) > len(fulltxt[line-1]):
                totalLen = 0
                for i in fulltxt[:-1]:
                    totalLen += len(i)
                end = f"{len(fulltxt)}.{(char+cVar.get())-totalLen}"  


            while pos:
                self._textArea.tag_add("mcomment", pos, end)

                pos = self._textArea.search(r'\/\*\s*\S*\*\/', end, stopindex="end", count=cVar, regexp=True)
                line = int(float(pos))
                char = int(pos[pos.index('.')+1:])

                fulltxt = self._textArea.get("1.0", tk.END).split('\n')
                while fulltxt[-1] == '':
                    fulltxt.pop()

                end = f"{line}.{char+cVar.get()}"

                if (char+cVar.get()) > len(fulltxt[line-1]):
                    totalLen = 0
                    for i in fulltxt[:-1]:
                        totalLen += len(i)
                    end = f"{len(fulltxt)}.{(char+cVar.get())-totalLen}"

        except:
            pass
    
    def _getFileContent(self, name: str) -> str:
        f = open(name, 'r')
        s = f.read()
        f.close()
        return s        
    
    def _openFile(self, e=None) -> None:
        name =  tk.filedialog.askopenfilename(
            initialdir = os.getcwd(), 
            title = "Select file",
            filetypes = (("Locks files", "*.lks"), ("All files", "*.*"))
        )
        if name == '':
            return

        s = self._getFileContent(name)
        self._textArea.delete("1.0", tk.END)
        self._textArea.insert("1.0", s)
        self._rootWnd.title(name)
        self._curOpenFile = name
        self._highlight()
        self._curFileIsSaved = True

    def _saveAsFile(self) -> None:
        f =  tk.filedialog.asksaveasfile(
            mode = 'w', 
            title = "Select file",
            filetypes = [("Locks File (*.lks)", "*.lks"), ("Text File (*.txt)", "*.txt")],
            defaultextension = ("Locks File (*.lks)", "*.lks")
        )

        if f == None:
            return

        text = self._textArea.get("1.0", tk.END)
        f.write(text)
        self._rootWnd.title(f.name)
        self._curOpenFile = f.name
        f.close()
        self._curFileIsSaved = True

    def _saveFile(self, e=None) -> None:
        if self._curOpenFile == "untitled":
            return self._saveAsFile()
            
        f =  open(self._curOpenFile, 'w')
        text = self._textArea.get("1.0", tk.END)
        f.write(text)
        self._rootWnd.title(f.name)
        f.close()
        self._curFileIsSaved = True

    def _runProgram(self, e=None) -> None:
        if self._curOpenFile == "untitled":
            self._saveAsFile()

        if not self._curFileIsSaved:
            r = messagebox.askyesno("Save File", "Do you want to save the file before running?")
            if r:
                self._saveFile()

        if platform.system() == "Windows":
            subprocess.Popen(f'{self._preferences["pyinterp"]} "{os.getcwd().replace(os.sep, "/")}/locks-interpreter.py" "{self._curOpenFile}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(f'{self._preferences["pyinterp"]} "{os.getcwd().replace(os.sep, "/")}/locks-interpreter.py" "{self._curOpenFile}"', shell=True)

    def _runDebug(self, e=None) -> None:
        if self._curOpenFile == "untitled":
            self._saveAsFile()

        if not self._curFileIsSaved:
            r = messagebox.askyesno("Save File", "Do you want to save the file before running?")
            if r:
                self._saveFile()

        if platform.system() == "Windows":
            subprocess.Popen(f'{self._preferences["pyinterp"]} "{os.getcwd().replace(os.sep, "/")}/locks-interpreter.py" "{self._curOpenFile}" -d', creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(f'{self._preferences["pyinterp"]} "{os.getcwd().replace(os.sep, "/")}/locks-interpreter.py" "{self._curOpenFile}" -d', shell=True)

