import streamlit as st
import pandas as pd
import google-generativeai as genai
import json
import numpy as np
import os 

st.set_page_config(page_title = "Song-The-Sizr : Songs Synthesizer", page_icon = "🎵")

# Sidebar สำหรับกรอก API Key (AI-assisted)
with st.sidebar:
    st.header("🔑 Log-in System")
    
    api_key = st.text_input(
        "Enter your Gemini API Key for this program",
        type = "password",
        help = "Get your API key from https://makersuite.google.com/app/apikey"
    )
    
    check_button = st.button("🔍 Check API Key", use_container_width=True)
    
    st.divider()
    
    if check_button:
        if not api_key:
            st.error("❌ Please enter an API key")
        else:
            with st.spinner("🤖 Checking API key..."):
                try:
                    # กำหนด API key
                    genai.configure(api_key=api_key)
                    
                    # ทดสอบเรียกใช้ model
                    model = genai.GenerativeModel('gemini-2.5-flash-lite')
                    response = model.generate_content("Say 'API key is valid'")
                    
                    # ถ้าสำเร็จ
                    st.success("✅ API Key is valid. Now you can use Song-The-Sizr 🫡")
                    st.session_state['api_key_valid'] = True
                    st.session_state['api_key'] = api_key
                    
                except Exception as e:
                    st.error(f"❌ API Key is invalid!. Please Enter API Key again 😞")
                    st.error(f"Error: {str(e)}")
                    st.session_state['api_key_valid'] = False


if st.session_state.get('api_key_valid', False):
    
    # Set initial state of Generative AI
    genai.configure(api_key=st.session_state['api_key'])
    model = genai.GenerativeModel('gemini-2.5-flash-lite')       
            
    ## After This , most will be written by myself , AI is used for checking errors
    
    # -- Main Program -- (If API Key Success , The program can run successfully)

    ## ----- Part I : Input UI for User ----- ##
    st.title("Song-The-Sizr : Songs Synthesizer")
    st.write("Welcome to this program. This program can convert Thai song lyrics into Dialogue Analysis and Drama Story 🎭. Wish you enjoy ☺️")
    
    st.subheader("How to use this program" , divider = True)
    st.write("Step 1 : Input Song Name & Band in box and lyrics in CSV form. Don't forget to organize your CSV.")
    st.write("Step 2 : Choose Type of program (Drama Script 🎭) or (Dialogue Analysis 📣)")
    st.write("Step 3 : Process Data then enjoy with your result 🫡")
    
    st.subheader("⚙️ Main Program" , divider = True)
    st.write("Input your song or choose these examples below")
    songs_info = st.selectbox(
                            "Input your song or choose these examples below",
                            ("เพลงรัก - Three Man Down", "น้ำตาสุดท้าย - Cocktail", "เหมือนวิวาห์ - Jeff Satur" , "สวยงามเสมอ - Billkin" , "ผู้ถูกเลือกให้ผิดหวัง - เรนิษรา" , "Others"),
                )
    
    if songs_info == "Others" : # User input by themselves
        songs_info = st.text_input("Input your song in this form `Songs_Name - Songs_Director`")
        
        if songs_info != "" : 
            songs_name = songs_info.split("-")[0].strip() ; songs_director = songs_info.split("-")[1].strip()
            st.write("Your selected song is :" , songs_name , "By" , songs_director)
        
        uploaded_file = st.file_uploader("Don't forget to upload lyrics in CSV Form !!!")
        if uploaded_file is not None :
            songs_dataframe = pd.read_csv(uploaded_file)
        
    else : # Songs Example
        songs_name = songs_info.split("-")[0].strip() ; songs_director = songs_info.split("-")[1].strip()
        st.write("Your selected song is :" , songs_name , "By" , songs_director)
        
        # Create Key:Value for File Path of Example Songs 
        example_songs_filepath = { "เพลงรัก" : "example_lyrics/love_song.csv" ,
                                   "น้ำตาสุดท้าย" : "example_lyrics/last_tear.csv",
                                   "เหมือนวิวาห์" :  "example_lyrics/like_wedding.csv" ,
                                   "สวยงามเสมอ" : "example_lyrics/always_beautiful.csv" , 
                                   "ผู้ถูกเลือกให้ผิดหวัง" : "example_lyrics/chosen_disappointed.csv"
                                 }
        
        songs_dataframe = pd.read_csv(example_songs_filepath[songs_name])
        
    ## Now we have Songs Name , Songs Director , Songs Dataframe 
    ## We need to have user input for type of output (Dialogue Analysis or Drama Script)
    
    desired_output_type = st.radio("Enter your desired output type" , 
                           ['Dialogue Analysis (Dataframe)' , 'Drama Story (Text)'] )
    
    if desired_output_type == 'Dialogue Analysis (Dataframe)' : 
        st.write("⏱️ Please wait a little bit for AI Response.")
        
        # AI-assisted Section
        
        ## Step I : Create Prompt
        prompt = f""" 
            Act as a professional screenwriter. Adapt the following song lyrics into a dramatic dialogue scene.
            Create a conflict or a story based on the lyrics (dataframe) . You can invent characters (e.g., Boy, Girl, Stranger).
    
        **OUTPUT REQUIREMENT:**
        Return ONLY a valid JSON string. The structure must be a list of dictionaries.
        Each dictionary must have these keys:
        - "Scene Number 🎬 ": Order number (1, 2, 3...)
        - "Character 👩🏻‍🦰 ": Name of the character
        - "Dialogue 📢 ": What they say (Thai language preferred for dialogue)
        - "Emotion 🥺 ": Emotional state (e.g., Sad, Angry, Crying)
        - "Action 🎭 ": Physical action (e.g., Wiping tears, Looking away)
        
        Do not use markdown code blocks (```json). Just raw JSON.
        
        Lyrics to adapt:
        {songs_dataframe}
        """
        try:
            # Step II : Get Response from AI
            response = model.generate_content(prompt)
            text_response = response.text
            
            # Step III : Clean Data JSON
            clean_json = text_response.replace("```json", "").replace("```", "").strip()
            
            # Step IV : Transform JSON to Python List 
            data = json.loads(clean_json)
            
            # Step V : Convert to DataFrame
            df_dialogue = pd.DataFrame(data)
            
            st.write(df_dialogue)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการแปลงข้อมูล: {e}")
            st.text("Raw Response from AI:")
            st.text(text_response) # ไว้ดูว่า AI ตอบอะไรมาถ้า Error
            st.write(pd.DataFrame()) # คืนค่าว่างถ้าพัง
    
    elif desired_output_type == 'Drama Story (Text)' : 
        
        # Step I : Generate Prompt 
        prompt = f""" 
            Act as a professional screenwriter. Adapt the following song lyrics into a dramatic drama story.
            Create a conflict or a story based on the lyrics (dataframe) . You can invent characters (e.g., Boy, Girl, Stranger).
    
            **OUTPUT REQUIREMENT:**
            Return novel of 2 paragraph. Need in thai story.
        
            Lyrics to adapt:
            {songs_dataframe}
            
            """
        response = model.generate_content(prompt)
        text_response = response.text
        st.write(text_response)
        
    ## Ending Zone 
    st.write("You can adapt ideas from this program. Hope you guys enjoy!")
    
    st.divider() 
    st.write("This is a part of my Final Project on 2209261 Basic Programming NLP , Semester 1 AY2025")
    st.write("Done by 6730084521 Chatrphol Ovanonchai. Use for educational purposes only!")