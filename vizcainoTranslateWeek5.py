from logging import warning
import requests, json, os, six
import pandas as pd
import numpy  as np
import google.auth
from  google.cloud import translate_v2 as translate
from  google.cloud import storage
from  google.cloud import speech
from tkinter import *
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo, showwarning

class VizcainoTranslator:
    def __init__(self, windowsGui, credentials):
        self.windowsGui_ = windowsGui
        self.windowsGui_.title('Sebastian Vizcaino - Translator')
        self.credentials = credentials
       
        self.createFrames()
        self.configure_widgets()
        self.styling()


    def createFrames(self):
        # Base frame:
        self.mainframe = ttk.Frame(self.windowsGui_
            ,padding='5 15 15 5'
            ,style = 'mainFrameColor.TFrame')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        #Entry Text Frame:
        self.textEntryFrame = ttk.Frame(self.mainframe
            ,padding='5 5 5 5'
            ,relief ='sunken'
            ,borderwidth=5
            ,style='entryFrame.TFrame')
        self.textEntryFrame.grid(column=1, columnspan=1, row=2, rowspan=5,
            sticky=(N, W, E, S))

        #Longer Translation Frame
        self.long_translation_frame = ttk.Frame(self.mainframe
            ,padding ='5 5 5 5'
            ,relief = 'sunken'
            ,borderwidth=5
            ,style = 'longTranslationFrame.TFrame')
        self.long_translation_frame.grid(column=1, columnspan=1, row=10, rowspan=3 )

        #CheckBox Frame:
        self.checkboxFrame = ttk.Frame(self.mainframe
            ,padding='5 5 5 5'
            ,relief='sunken'
            ,borderwidth=5
            ,style='checkboxFrame.TFrame')
        self.checkboxFrame.grid(column=2, columnspan=1, row=2, rowspan=5, 
            sticky=(N, W, E, S))


    def styling(self):
        print('hello')
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Verdana', 18), foreground='#000000', background='#384C5B')
        self.style.configure('mainFrameColor.TFrame', background='#384C5B')
        self.style.configure('entryFrame.TFrame', background='#384C5B')
        self.style.configure('entryFrameButtons.TButton', font=('Noto Sans', 14), foreground ='#C33D38', width = 25)
        self.style.configure('longTrans.TButton', font=('Noto Sans', 14), foreground ='#C33D38', width = 20)
        self.style.configure('checkboxFrame.TFrame', font=('verdana', 14), background='#384C5B')
        self.style.configure('TCheckbutton', font=('Noto Sans', 18), foreground = '#C33D38', background='#384C5B')
        self.style.configure('longTranslationFrame.TFrame', background='#384C5B')

    def configure_widgets(self):

        ##### Main Frame Widgets #####
        ##############################

        short_translation  = ttk.Label(self.mainframe
            ,text='Short Translation'
            ,style = 'TLabel')
        short_translation.grid(column=1, row = 1, stick=W)

        longer_translation = ttk.Label(self.mainframe
            ,text = 'Longer Translation'
            ,style = 'TLabel')
        longer_translation.grid(column=1, row =8, sticky=W)

        translation_language = ttk.Label(self.mainframe
            ,text='Translation Language'
            ,style='TLabel')
        translation_language.grid(column=2, row=1, sticky=E)

        ##### Text Entry Frame Widgets #####
        ####################################

        self.entryPhrase_stVar = StringVar()
        self.textEntryPhrase = ttk.Entry(self.textEntryFrame 
            ,textvariable=self.entryPhrase_stVar
            ,font=('Verdana', 45)
            ,width=30)
        self.textEntryPhrase.grid(column=1, row=1, columnspan=10, 
            rowspan=1, sticky=(N, W, E, S))

        self.translateButton = ttk.Button(self.textEntryFrame
            ,text = 'Translate'
            ,style='entryFrameButtons.TButton'
            ,command =self.translate_input_text)
        self.translateButton.grid(column = 1, row = 5, stick=E, padx=15, pady=20)
        self.translateButton.lift()

        self.clearButton = ttk.Button(self.textEntryFrame
            ,text = 'Clear'
            ,style= 'entryFrameButtons.TButton'
            ,command=self.clear_text)
        self.clearButton.grid(column = 2, row = 5, sticky=W, padx=15, pady=50)

        self.clearTextButton= ttk.Button(self.mainframe
            ,text= 'Clear Text'
            ,style= 'entryFrameButtons.TButton'
            ,command=self.clear_output_text)
        self.clearTextButton.grid(column=1, row=16)

        ##### LONGER TRANSLATION WIDGETS #####
        ######################################

        self.buttons = ['Audio Local', 'Audio Cloud', 'Text File', 'Save']
        self.commands = [self.translate_local, print('Work in Progress'), self.open_text_file, self.save_translated_text]

        for i in range(len(self.buttons)):
            btn = ttk.Button(self.long_translation_frame
                ,text =self.buttons[i]
                ,style ='longTrans.TButton'
                ,command= self.commands[i])
            btn.grid(column=i+1,row=0, padx= 10)

        self.file_path_stVar = StringVar()
        self.file_path_entry = ttk.Entry(self.long_translation_frame
            ,textvariable=self.file_path_stVar
            ,font=('Arial',20)
            ,width = 75)
        self.file_path_entry.grid(column = 0, row = 1, columnspan=6, pady=15, sticky=(N, W, E, S))

        self.letter_count_stVar = StringVar()
        self.file_character_count = ttk.Entry(self.long_translation_frame
            ,textvariable= self.letter_count_stVar
            ,font=('Arial',20)
            )
        self.file_character_count.grid(column = 0, row = 2, columnspan=6, pady=10, sticky=(N, W, E, S))



        ##### CHECK BUTTON FRAME #####
        # ISO 639-1 Language Codes 
        # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes#ES
        ############################################################
        
        self.language = ['english', 'spanish', 'German', 'French', 'Italian', 
                        'Afrikaans', 'Slovak', 'Arabic', 'Hindi', 'Chinese']
        self.langs = ['en', 'es', 'de', 'fr', 'it', 'af', 'sk', 'ar', '	hi', 'zh']

        self.languageSelection = StringVar(value=self.language)
        self.selected_var = StringVar()

        self.l = Listbox(self.checkboxFrame
            ,listvariable=self.languageSelection
            ,height=10
            ,borderwidth=10
            ,cursor='heart' # <3
            ,relief='sunken'
            ,font = ('Noto Sans', 14)
            ,fg='#B8DBD9'
            ,bg = '#384C5B'
            ,activestyle='dotbox'
            ,selectbackground='#081c15')    
        self.l.grid(column=1, row=i,sticky= W)

        #Translated Output Window
        self.text_output = Text(self.mainframe
            ,wrap='word'
            ,width=40
            ,height= 7
            ,bg='#000000'
            ,fg='#586F7C'
            ,font=('Arial', 25))
        self.text_output.grid(column=0, columnspan=3, row=15, rowspan=1, 
            ipadx=5, padx=5, ipady=10, pady=10, sticky=(N, W, E, S))

    def clear_text(self):
        self.entryPhrase_stVar.set("")

    def clear_output_text(self):
        self.text_output.delete(1.0,"end")

    def open_text_file(self):
        filename = filedialog.askopenfile(initialdir='/'
            ,mode = 'r'
            ,title = 'Select A Text File'
            ,filetypes=(("Text files",
                 "*.txt*"),
                 ("all files",
                   "*.*")))
        if filename:
            self.filepath = os.path.abspath(filename.name)
            print(self.filepath)
            self.file_path_stVar.set(f'File: {str(self.filepath)}')
        
        #Couldn't get this to work on its own function
        with open(self.filepath, 'r') as f:
            self.contents = f.read()
            i = 0
            for c in self.contents:
                i += 1
            
        self.letter_count_stVar.set(f'File contains {i} characters')
        print(f'File contains {i} characters')
        
        print('File Closed')
        f.close()

    def translate_local(self):
        client = speech.SpeechClient(credentials=credentials)

        audiolang = {'English': ("en-US", "en-US-Wavenet-D"), # US english
                    'Spanish': ("es-ES",  "es-ES-Wavenet-B"),
                    'German':  ("de-DE",  "de-DE-Wavenet-B"),
                    'French':  ("fr-FR",  "fr-FR-Wavenet-D"),
                    'Italian': ("it-IT",  "it-IT-Wavenet-C"),
                    'Afrikaans': ("af-ZA",  "af-ZA-Standard-A"),
                    'Slovak': ("sk-SK", "sk-SK-Wavenet-A"),
                    'Arabic':  ("ar-XA",  "ar-XA-Wavenet-B"),
                    'Hindi':  ("hi-IN", "hi-IN-Wavenet-A"),
                    'Chinese': ("yue-HK", "yue-HK-Standard-B"),
                    }

        audiofilename = filedialog.askopenfile(initialdir='/'
            ,mode = 'rb'
            ,title = 'Select Audio Fule'
            ,filetypes=(("Audio Files",
                "*.wav*"),
                ("all files",
                "*.*")))
        if audiofilename:
            self.audiofilepath = os.path.abspath(audiofilename.name)

        with open(self.audiofilepath, 'rb') as audio_file:
            recording = audio_file.read()


        self.audioidxs = self.l.curselection()
        if len(self.audioidxs) == 1:
            self.aidx = int(self.audioidxs[0])
            self.audiocode = self.language[self.aidx]
            print(self.audiocode)

        #time_limit = 90
        audio  = speech.RecognitionAudio(content=recording)
        config = speech.RecognitionConfig(language_code=audiolang[self.audiocode][0])
        print(audiolang[self.audiocode][0])
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout = 90)

        chunks = 0
        transcript = ""
        confidence = 0.0
        for result in response.results:
            chunks += 1
            transcript = transcript+result.alternatives[0].transcript
            confidence = confidence+result.alternatives[0].confidence
        
        confidence = 100.0*confidence/chunks
        print(u"Transcript: {}".format(transcript))
        print("Confidence: {}".format(confidence))

        #self.clear_output_text()
        self.text_output.insert(1.0, transcript)

    def clod_translation(self):
        pass


    def translate_input_text(self):
        """Translates text into the target language.
        Target language must be an ISO 639-1 language code.
        See https://g.co/cloud/translate/v2/translate-reference#supported_languages
        """
        
        # Could not set this block of code in its own function, not sure why.
        # This code snippet retrieves the index number of the language selected
        # to then search for the proper ISO language code. which will be set 
        # in the google translate client. 

        self.idxs =  self.l.curselection()
        
        if len(self.idxs) == 0:
            warning = showwarning(title='No Language Selected'
                ,message='Please select a language from the options menu',)
            warning

        if len(self.idxs) == 1:
            self.idx = int(self.idxs[0]) # getting the first item from the tuple
            self.code = self.langs[self.idx]

    
        # self.input_text = self.entryPhrase_stVar.get()
        if len(self.entryPhrase_stVar.get()) == 0:
            try:
                if len(self.contents) != 0:
                    self.input_text = self.contents
            except:
                return
        else:
            self.input_text = self.entryPhrase_stVar.get()
        
        translate_client = translate.Client(credentials=self.credentials)

        if isinstance(self.input_text, six.binary_type):
            self.input_text = self.input_text.decode('utf-8')

        result = translate_client.translate(self.input_text, target_language=self.code)
        self.translation = result["translatedText"]

        #print on console
        print(self.translation)

        self.clear_output_text()
        self.text_output.insert(1.0, self.translation)

    def save_translated_text(self):

        Files = [('All Files', '*.*'),
			('Text Document', '*.txt')]

        with open(filedialog.asksaveasfilename(filetypes=Files, 
              defaultextension = Files), 'w') as save:
            save.write(self.translation)

           
# Notice that this is the Google Translate Credentials file for 
# myself.  If you are using this, it needs to placed in the same
# directory as this app.  Please limit your use to translating
# small files, files with less than 5,000 characters.  A book or
# movie will typically include over 500,000 characters.
google_project_file = "GoogleTranslateCredentials.json"
credentials, project_id = google.auth.\
                          load_credentials_from_file(google_project_file)
root   = Tk()
my_app = VizcainoTranslator(root, credentials)
# Display GUI
root.mainloop()
