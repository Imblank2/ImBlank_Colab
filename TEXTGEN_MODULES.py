def main_func(var):
    
    import sys, os, sys, base64, subprocess, json, shutil, requests, time, pathlib, multiprocessing
    from IPython.display import clear_output, display, HTML
    from IPython.utils import capture
    from PIL import Image
    
    #Oobabooga 
    Upload_ProfilePic=var[2]
    save_logs_to_google_drive=var[3]
    model=var[4]
    text_streaming=var[5]
    activate_sending_pictures=var[6]
    activate_character_bias=var[7]
    chat_language=var[8]
    RunWebUI=var[9]
    GetAPI=var[10]
    Debug=var[11]
    
    #Main Directories:
    base_folder = "/content/gdrive/MyDrive/oobabooga-data"
    main_dir = "/content/text-generation-webui/"
    cache = f"{main_dir}cache"
    activate_google_translate= (chat_language != "English")
    
    #Extra
    GrantBot_Access_to_Bing = False
    load_in_8bit = True
    if ('GPTQ' in model or '4bit' in model or '128' in model): load_in_8bit = False
    old_ooba = True
    complex_memory = True
    filler=" "
    
    #PART 1 INSTALL 
    
    def jpy(cmd):
        """Emulate Jupyter Notebook commands."""
    
        # Get the first word in the command
        action = cmd.split()[0]
        
        if action == 'cd':
            # Change directory
            os.chdir(' '.join(cmd.split()[1:]))
        elif action == 'ls':
            # List files and directories
            print(subprocess.check_output(['ls', '-la']).decode())
        elif action == 'pwd':
            # Print current working directory
            print(os.getcwd())
        elif action.startswith('!'):
            # Run shell commands           
            with subprocess.Popen(cmd[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True) as proc:
              while True:
                out = proc.stdout.readline() or proc.stderr.readline()
                if not out:
                  break
                print(out.decode().strip())                
          #cmd_prompt=subprocess.run(cmd[1:], shell=True)
        else:
            print(f"Error: unknown command {action}")
    
    def universal_download(link1, path1, nan3):
      jpy(f"!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M {link1} -d {path1} -o {nan3}")
      
    def debug_():
      if not Debug:clear_output()
      return None
    
    ####### COMPLEX STUFF #######
    
    #SillyTavern
    def install_silly(): #$
      jpy("cd /")
      ForceInitSteps = []
      class IncrementialInstall:
        def __init__(self, root = "/", tasks = [], force = []):
            self.tasks = tasks
            self.path = os.path.join(root, ".ii")
            self.completed = list(filter(lambda x: not x in force, self.__completed()))
        def __completed(self):
            try:
                with open(self.path) as f:
                    return json.load(f)
            except:
                return []
        def addTask(self, name, func):
            self.tasks.append({"name": name, "func": func})
        def run(self):
            todo = list(filter(lambda x: not x["name"] in self.completed, self.tasks))
            try:
                for task in todo:
                    task["func"]()
                    self.completed.append(task["name"])
            finally:
                with open(self.path, "w") as f:
                    json.dump(self.completed, f)
      def create_paths(paths):
        for directory in paths:
            if not os.path.exists(directory):
                os.makedirs(directory)
      def link(srcDir, destDir, files):
        '''
            Link source to dest copying dest to source if not present first
        '''
        for file in files:
            source = os.path.join(srcDir, file)
            dest = os.path.join(destDir, file)
            if not os.path.exists(source):
                jpy('!cp -r "$dest" "$source"')
            jpy('!rm -rf "$dest"')
            jpy('!ln -fs "$source" "$dest"')
      if not save_logs_to_google_drive:
        create_paths([
                "/content/SillyTavern-Data"
        ])
      ii = IncrementialInstall(force=ForceInitSteps)
    # ---
    # SillyTavern py modules
      def cloneTavern():
        jpy("cd /")
        jpy("!git clone https://github.com/Cohee1207/SillyTavern")
        jpy("!wget https://huggingface.co/Imablank/AnythingV3-1/resolve/main/ooba/globals.py && wget https://huggingface.co/Imablank/AnythingV3-1/resolve/main/ooba/extras_server.py")
      ii.addTask("Clone SillyTavern", cloneTavern)
      ii.run()
      kargs = ["/content/ckds"]
      kargs += ["--localtunnel", "yes"]
    
    # ---
    # nodejs
      jpy('cd /')
      def installNode():
        jpy("!npm install -g n")
        jpy("!n 19")
        jpy("!node --version")
      installNode()
    # ---
    # TavernAI extras
      import globals
      globals.params = []
      globals.params.append('--cpu')
      jpy("cd /SillyTavern")
      if save_logs_to_google_drive:
        os.environ['googledrive']=2
        def setupTavernPaths():
            jpy("cd /SillyTavern")
            tdrive = "/content/gdrive/MyDrive/SillyTavern"
            create_paths([
                    tdrive,
                    os.path.join("public", "groups"),
                    os.path.join("public", "group chats")
            ])
            link(tdrive, "public", [
                    "settings.json",
                    "backgrounds",
                    "characters",
                    "chats",
                    "User Avatars",
                    "worlds",
                    "group chats",
                    "groups",
            ])
        ii.addTask("Setup Tavern Paths", setupTavernPaths)
        ii.run()
    
      def installTavernDependencies():
        jpy("cd /SillyTavern")
        jpy("!npm install")
        jpy("!npm install -g localtunnel")
      ii.addTask("Install Tavern Dependencies", installTavernDependencies)
      ii.run()
    
    '''
    def edgegpt(): #$
      import zipfile
      %cd /content/
      !wget https://huggingface.co/Imablank/AnythingV3-1/resolve/main/ooba/EdgeGPT_working.zip
      with zipfile.ZipFile('/content/EdgeGPT_working.zip', 'r') as zip:
        zip.extractall("/content/text-generation-webui/extensions")
      !pip install -r {main_dir}extensions/EdgeGPT/requirements.txt && rm -rf /content/EdgeGPT_working.zip
      %cd {main_dir}
    '''
    
    def find_name(): #$
      if os.path.exists(f"{base_folder}/User"):
        try: # Check if There's something
          user_profile = os.listdir(f"{base_folder}/User")
          for count1 in user_profile:
            jpy(f"!cp -r {base_folder}/User/{count1} {main_dir}cache")
        except: pass # In case if the folder is empty, then pass
      try:
          username_find_dir=os.listdir(f"{main_dir}cache/")
          for k in username_find_dir: username_located=k.index("-settings-colab.json") if "-settings-colab.json" in k else ''
          username_found=k[0:username_located]      
      except: username_found = None
      finally: return username_found
    
    def overwrite_profile(): #$
      global _username_
      UserName=var[1]
      #OverWrite UserName
      if not username_found == None and not "" == UserName:    
        jpy(f"!rm -rf {cache}/{username_found}-settings-colab.json")
      #Load Previous UserName
      elif not username_found == None and "" == UserName: UserName = username_found
      #Force to Default Name
      elif username_found == None and "" == UserName: UserName="Anon-san"
      jpy(f"cd {main_dir}")
      j = json.loads(open('settings.json', 'r').read())
      j["google_translate-language string"] = language_codes[chat_language]
      j["name1"] = UserName
      if " " in UserName: UserName=UserName.replace(" ", "_")
      _username_= f"{UserName}-settings-colab.json" 
      with open(_username_, 'w') as f:
        f.write(json.dumps(j, indent=4))
      jpy(f"!mv {main_dir}{_username_} {main_dir}cache")
      debug_()
    
    def install_ooba(): #$
      jpy("cd /content")
      jpy("!apt-get -y install -qq aria2")
      jpy(f"!mkdir {main_dir}cache")
      if save_logs_to_google_drive:
        if not os.path.exists(f"{base_folder}"):
          os.mkdir(f"{base_folder}")
        if not os.path.exists(f"{base_folder}/logs"):
          os.mkdir(f"{base_folder}/logs")
        if not os.path.exists(f"{base_folder}/User"):
          os.mkdir(f"{base_folder}/User")
        if not os.path.exists(f"{base_folder}/softprompts"):
          os.mkdir(f"{base_folder}/softprompts")
        if not os.path.exists(f"{base_folder}/characters"):
          shutil.move("text-generation-webui/characters", f"{base_folder}/characters")
        else:
          jpy(f"!rm -rf {main_dir}characters")
            
          jpy("!rm -r text-generation-webui/softprompts")
          jpy(f"!ln -s {base_folder}/logs text-generation-webui/")
          jpy(f"!ln -s {base_folder}/softprompts text-generation-webui/softprompts")
          jpy(f"!ln -s {base_folder}/characters text-generation-webui/characters")
          jpy(f"!ln -s {base_folder}/User .")
      else:
        jpy("!mkdir text-generation-webui/logs")
            
      jpy("!ln -s text-generation-webui/logs .")
      jpy("!ln -s text-generation-webui/characters .")
      jpy("!ln -s text-generation-webui/models .")
      
      jpy("!rm -r sample_data")
    
      jpy(f"cd {main_dir}")
      jpy(f"!wget https://oobabooga.github.io/settings-colab.json")
      jpy("!rm -rf /content/text-generation-webui/presets/Default.txt /content/text-generation-webui/settings-colab-template.json /content/text-generation-webui/settings-template.json")
    
      link="https://huggingface.co/Imablank/AnythingV3-1/raw/main/GPT4.txt, https://huggingface.co/Imablank/AnythingV3-1/raw/main/Alpha.json, https://huggingface.co/Imablank/AnythingV3-1/resolve/main/Alpha.png, https://huggingface.co/Imablank/AnythingV3-1/raw/main/settings.json"
      path="/content/text-generation-webui/presets/, /content/characters/, /content/characters/, /content/text-generation-webui/"
      nan3="GPT4.txt, Alpha.json, Alpha.png, settings.json"; link=link.split(', '); path=path.split(', '); nan3=nan3.split(', ')
      for link, path, nan3 in zip(link, path, nan3):
        universal_download(link, path, nan3)
    
      jpy("!pip install -r requirements.txt && pip install -r extensions/google_translate/requirements.txt && pip install -r extensions/api/requirements.txt")
        
      if ('GPTQ' in model or '4bit' in model or '128' in model): #$
        jpy("!mkdir /content/text-generation-webui/repositories")
        jpy(f"cd {main_dir}/repositories/")
        jpy("!git clone -b v1.2 https://github.com/camenduru/GPTQ-for-LLaMa.git")
        jpy(f"cd {main_dir}/repositories/GPTQ-for-LLaMa/")
        jpy("!python setup_cuda.py install")
    
    def download_model(type): #$
      print("\033[92m")
      tmp_repo=f"/content/.{huggingface_repo}"
      jpy(f"!git lfs install --skip-smudge && export GIT_LFS_SKIP_SMUDGE=1 && git clone https://huggingface.co/{huggingface_org}/{huggingface_repo} /content/.{huggingface_repo} --branch {huggingface_branch}")
      jpy(f"!rm -rf {tmp_repo}/PygmalionCoT-7b-ggml-model-f16.bin {tmp_repo}/PygmalionCoT-7b-ggml-q4_2.bin {tmp_repo}/PygmalionCoT-7b-ggml-q5_1.bin {tmp_repo}/PygmalionCoT-7b-ggml-q8_0.bin {tmp_repo}/PygmalionCoT-7b-4bit-128g.safetensors {tmp_repo}/pytorch_model.bin.index.json {tmp_repo}/training_args.bin {tmp_repo}/trainer_state.json {tmp_repo}/all_results.json {tmp_repo}/eval_results.json {tmp_repo}/.gitattributes {tmp_repo}/train_results.json")
      repo = os.listdir(tmp_repo); clear_output()
      for download in repo:    
        link_path = f"https://huggingface.co/{huggingface_org}/{huggingface_repo}/"
        if ".json" in download or ".txt" in download:
          link_path += f"raw/{huggingface_branch}/{download}"
        else: link_path += f"resolve/{huggingface_branch}/{download}"
        jpy(f"!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M {link_path} -d /content/text-generation-webui/models/{type} -o {download}")
    ################################
    
    # Install #$
    
    if (not os.path.exists(main_dir) or ('GPTQ' in model or '4bit' in model or '128' in model) and not os.path.exists(f"{main_dir}repositories")):
      jpy("cd /content")
      jpy(f"!git clone https://github.com/oobabooga/text-generation-webui && git clone https://github.com/theubie/complex_memory {main_dir}/extensions/complex_memory")
      if old_ooba:
         jpy(f"cd {main_dir}")
         jpy("!git checkout f052ab9c8fed3dedc446c3847f10ab22e42bfb37")
      debug_()
      
      if not Debug:
        display(HTML("<img src='https://huggingface.co/Imablank/AnythingV3-1/resolve/main/BoochiLoading.gif' width='280px'/>"))
        print("\033[92m[Installing oobabooga]")
        with capture.capture_output() as cap:
          install_ooba(); #edgegpt()
          if GetAPI: install_silly()
          del cap
      else:
        install_ooba(); #edgegpt()
        if GetAPI: install_silly()
    else:
      if GetAPI: install_silly()
      debug_(); print("\033[92m\n[ ALREADY INSTALLED -- SKIPPING INSTALL.. ]")
    
    def upload_profile(): #$
      from google.colab import files
      def png_convert():
      #Path reader & png format converter
          pfp = os.listdir("/.pfp/");
          for o in pfp: pfp=o.replace(" ", "_"); pfp=f"/.pfp/{o}"
          if os.path.exists(f"{base_folder}/User"):
            if ".png" in o:
              a = os.rename(pfp, "pfp_me.png")
              jpy(f"!mv /.pfp/pfp_me.png {base_folder}/User")
            else:
              Ima1 = Image.open(r""+pfp)
              Ima1.save(r"/content/gdrive/MyDrive/oobabooga-data/User/pfp_me.png") #cache
          else:
            if ".png" in o:
              a = os.rename(pfp, "pfp_me.png")
              jpy(f"!mv /.pfp/pfp_me.png {main_dir}cache")
            else:
              Ima1 = Image.open(r""+pfp)
              Ima1.save(r"/content/text-generation-webui/cache/pfp_me.png")
        
      #Upload Profile pic in ooba
      try: #$
        debug_()
        jpy("!rm -rf /.pfp/ && mkdir /.pfp/")
        if Upload_ProfilePic:
          jpy("cd /.pfp/")
          print("\033[92m[Upload Your Profile Picture]\n"); files.upload(); png_convert()
      except: pass
    jpy("cd /content")
    upload_profile()
    
    jpy(f"cd {main_dir}")
    language_codes = {'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'iw', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu', 'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Korean': 'ko', 'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi', 'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no', 'Nyanja (Chichewa)': 'ny', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese (Portugal, Brazil)': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala (Sinhalese)': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tagalog (Filipino)': 'tl', 'Tajik': 'tg', 'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'}
    username_found = find_name()
    overwrite_profile()
    
    if "Pygmalion-350m(CPU)" in model:
      huggingface_org="alpindale";huggingface_repo="pygm-350m-experimental";huggingface_branch="main"
    elif "PygmalionCoT-7b" in model:
      huggingface_org="notstoic";huggingface_repo="PygmalionCoT-7b";huggingface_branch="main"
    elif "Wizard-Vicuna-13B-Uncensored-GPTQ" in model:
      huggingface_org="TheBloke";huggingface_repo="Wizard-Vicuna-13B-Uncensored-GPTQ";huggingface_branch= "main"
    elif "Pygmalion_6B_main_Sharded" in model:
      huggingface_org="waifu-workshop";huggingface_repo="pygmalion-6b";huggingface_branch="sharded"
    elif "Pygmalion_6B_original_Sharded" in model:
      huggingface_org="waifu-workshop";huggingface_repo="pygmalion-6b";huggingface_branch="original-sharded"
    elif "Pygmalion_6B_dev_Sharded" in model:
      huggingface_org="waifu-workshop";huggingface_repo="pygmalion-6b";huggingface_branch="dev-sharded"
    elif "Pygmalion-7B" in model:
      huggingface_org="TehVenom";huggingface_repo="Pygmalion-7b-Merged-Safetensors";huggingface_branch="main"
    elif "Metharme-7B" in model:
      huggingface_org="Imablank";huggingface_repo="Metharme-7B-MERGED_WEIGHTS";huggingface_branch="main"
    elif "Pygmalion-13B-4bit" in model:
      huggingface_org="notstoic";huggingface_repo="pygmalion-13b-4bit-128g";huggingface_branch="main"
    elif "Metharme-13B-4bit" in model:
      huggingface_org="TehVenom";huggingface_repo="Metharme-13b-4bit-GPTQ";huggingface_branch="main"
    
    b=f"{huggingface_repo}_{huggingface_branch}" if (not "main" == huggingface_branch) else huggingface_repo
    
    if not os.path.exists(f"/content/models/{huggingface_repo}"):download_model(b);debug_();print(f"\033[96m\n[{model} Installed]\n");debug_()
    
    # Starting the web UI
    
    params = set()
    if ('GPTQ' in model or '4bit' in model or '128' in model): params.add('--wbits 4 --groupsize 128 --model_type Llama')
    if load_in_8bit: params.add('--load-in-8bit')
    #if Debug: params.add('--cpu')
    
    params.add('--share --chat') if not GetAPI else params.add('--public-api --chat')
    
    if not text_streaming or activate_google_translate: params.add('--no-stream')
    active_extensions = []
    if activate_sending_pictures: active_extensions.append('send_pictures')
    if activate_character_bias: active_extensions.append('character_bias')
    if complex_memory: active_extensions.append('complex_memory')
    if activate_google_translate: active_extensions.append('google_translate')
    if GetAPI: active_extensions.append('api')
    if GrantBot_Access_to_Bing: active_extensions.append('EdgeGPT')
    
    active_extensions.append('gallery')
    
    if len(active_extensions) > 0: params.add(f'--extensions {" ".join(active_extensions)}')
    print("\033[1m "+"\033[92m ")
    
    stuff = ' '.join(params)
    
    def run_webui_():
      def run_ooba():#$
        cmd = f"python server.py --verbose --model {b} --settings {main_dir}cache/{_username_} {stuff}"
        print(cmd)
        jpy(f"!{cmd}")
    
      def run_silly_tavern(): #$
        time.sleep(1)
        os.environ['colaburl']={url}
        os.environ['SILLY_TAVERN_PORT']=7860
        p = subprocess.Popen(["lt", "--port", "7860"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Link=(p.stdout.readline().decode().strip())
        # Get external IP address
        external_ip = requests.get('https://api.ipify.org').text
        external_ip=f"\n\n\n###Copy Google Colab's Endpoint IP###\nEndpoint IP: \033[4;92m{external_ip}\033[0m"
        print(external_ip, f"\n###SillyTavern LINK###\n{Link}", sep="\n"); print('\n\n')
        jpy("!node /SillyTavern/server.js")
        
      if GetAPI:
        multi=[]
        p=multiprocessing.Process(target=run_silly_tavern); p.start(); multi.append(p)
        p=multiprocessing.Process(target=run_ooba); p.start(); multi.append(p)
        for multi in multi: multi.join()
      else:
        run_ooba()
        #Save to drive system
        if os.path.exists(f"{base_folder}/User"):
          username_delete = os.listdir(f"{base_folder}/User")
          try: username_delete.remove("pfp_me.png")
          except: pass
          for username_delete in username_delete:
            jpy(f"!rm -rf {base_folder}/User/{username_delete}")
          if os.path.exists("/content/text-generation-webui/cache/pfp_me.png"):filler=" /content/text-generation-webui/cache/pfp_me.png "
          jpy(f"!cp -r /content/text-generation-webui/cache/{_username_}{filler}{base_folder}/User")
    
    if RunWebUI: run_webui_()
    if not Debug:
      debug_()
      display(HTML("<img src='https://huggingface.co/Imablank/AnythingV3-1/resolve/main/bocchi-the-rock-bocchi.gif' width='300px'/>"))
    
    print("\033[1m "+"\033[92m ")
    print("\n[TEXT-GEN-WEBUI SERVICE TERMINATED]")