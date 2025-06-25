# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#VoiceBot UI with Gradio
import os
import gradio as gr

from brain_of_doctor import encode_image, analyze_image_with_query
from voice_of_patient import transcribe_with_groq
from voice_of_doctor import text_to_speech_with_fallback

#load_dotenv()


text_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""
img_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath, chat_msg,mode):
    # 1. Get user input based on mode
    if mode == "voice":
        user_input = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
    else:
        user_input = chat_msg

    encoded_img = None
    system_prompt = img_prompt if image_filepath else text_prompt

    # 2. Prepare image data (only if user wants to include image)
    if image_filepath:
        encoded_img = encode_image(image_filepath)


    # 3. Generate doctor's response
    doctor_response = analyze_image_with_query(
        query=system_prompt + user_input,
        encoded_image=encoded_img,
        model="meta-llama/llama-4-scout-17b-16e-instruct"
    )

    # 4. Generate voice output
  
    voice_of_doctor = text_to_speech_with_fallback(
        input_text=doctor_response,
        output_filepath="final.mp3"
    )

    # 5. Return results
    return user_input, doctor_response, voice_of_doctor

with gr.Blocks(title="AI Doctor with Vision, Voice, and Chat") as demo:
    mode = gr.Radio(["voice", "chat"], label="Choose your input mode:")

    with gr.Column(visible=True) as voice_section:
        audio = gr.Audio(sources=["microphone"], type="filepath")
        image = gr.Image(type="filepath")  # Image now visible in both modes
        voice_chat_message = gr.Textbox(visible=False)  # Hidden for voice mode

    with gr.Column(visible=False) as chat_section:
        chat_message = gr.Textbox(label="Type your message")
        chat_audio = gr.Audio(visible=False)  # Hidden for chat mode
        image = gr.Image(type="filepath")    # Same image input, reused
        chat_image = gr.Image(type="filepath", visible=False)  # Optional/unused

    # Show/hide sections based on mode
    mode.change(
        lambda m: (
            gr.Column(visible=m == "voice"),
            gr.Column(visible=m == "chat")
        ),
        inputs=mode,
        outputs=[voice_section, chat_section]
    )

    # Outputs
    speech_to_text = gr.Textbox(label="Speech to Text")
    doctor_response = gr.Textbox(label="Doctor's Response")
    response_audio = gr.Audio(label="Response Audio")

    # Submit button connection
    btn = gr.Button("Submit")
    btn.click(
        process_inputs,
        inputs=[audio, image, chat_message, mode],
        outputs=[speech_to_text, doctor_response, response_audio]
    )
demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))  # works for both Render and local
)



#http://127.0.0.1:7860