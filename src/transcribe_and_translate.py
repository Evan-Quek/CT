import os, json
from faster_whisper import WhisperModel
from datetime import timedelta

model_path = "/app/model/faster-whisper-medium"
if not os.path.exists(model_path):
    model_path = "medium"

model = WhisperModel(model_path, 
                     device="cuda", 
                     compute_type="float16")

log_prob_threshold = -1.0 # default value by Whisper
compression_ratio_threshold = 2.4 # default value by Whisper

def decode_audio(path, output_dir=None, language=None):   
    os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" 
    print("Transcribing...")
    transcript_srtFilename, transcript_txtFilename,\
    input_language, detected_lang, detected_lang_conf = get_srt_and_txt(path, output_dir=output_dir, language=language,task='transcribe')
    print("Transcribing complete...")
    print("Translating...")
    translation_srtFilename, translation_txtFilename, \
    input_language, detected_lang, detected_lang_conf = get_srt_and_txt(path, output_dir=output_dir, language=language, task='translate')
    print("Translation complete...")

    file_paths = {
        'audio_file' : path, 
        'transcript_srt' : transcript_srtFilename,
        'transcript_txt' : transcript_txtFilename,
        'translation_srt' : translation_srtFilename,
        'translation_txt' : translation_txtFilename,
        'selected_language' : input_language,
        'detected_lang' : detected_lang,
        'detected_lang_conf' : detected_lang_conf
            }
    
    return file_paths


def find_key(target_value):
    with open("/app/model/whisper_language_codes", 'r') as file:
        language_codes = json.load(file)
        
    for key, value in language_codes.items():
        if key.lower() == target_value.lower():
            return str(value)
        elif value.lower() == target_value.lower():
            return str(key)
    return None  

            
def get_srt_and_txt(language, output_dir, task, path=None): #task = 'translate' or 'transcribe'
    if path:
        if task == 'transcribe':    
            filename = os.path.basename(path)
            print(filename)
            srt_path = os.path.join(output_dir,"transcript-srt")
            if not os.path.exists(srt_path):
                os.makedirs(srt_path)
            srtFilename = os.path.join(srt_path, filename[:-4]+".srt")
                
            txt_path = os.path.join(output_dir,"transcript-txt")
            if not os.path.exists(txt_path):
                os.makedirs(txt_path)  
            txtFilename = os.path.join(txt_path, filename[:-4]+".txt")
    
        elif task == 'translate':   
            filename = os.path.basename(path)
            print(filename)
            srt_path = os.path.join(output_dir,"translation-srt")
            if not os.path.exists(srt_path):
                os.makedirs(srt_path)
            srtFilename = os.path.join(srt_path, filename[:-4]+".srt")
                
            txt_path = os.path.join(output_dir,"translation-txt")
            if not os.path.exists(txt_path):
                os.makedirs(txt_path)  
            txtFilename = os.path.join(txt_path, filename[:-4]+".txt")
    else:
        #run model
        segments, info = model.transcribe(audio=path,
                                    beam_size=5,
                                    language=language, 
                                    task=task)
        
        detected_lang = find_key(info[0]).title()
        detected_lang_conf = round((info[1]*100),2)
        if not language:
            print(f"Detected language: {detected_lang} with {detected_lang_conf}% confidence")
        
        for segment in segments:    
            startTime = str(0)+str(timedelta(seconds=int(segment.start)))+',000'
            endTime = str(0)+str(timedelta(seconds=int(segment.end)))+',000'
            text = segment.text
            segmentId = segment.id+1
            srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
        
            #Write .srt and .txt files
            with open(srtFilename, 'a', encoding='utf-8') as srtFile:
                srtFile.write(srt_segment)
            with open(txtFilename, 'a', encoding='utf-8') as file:
                file.write(f"{text}\n")

    return srtFilename, txtFilename, language, detected_lang, detected_lang_conf

