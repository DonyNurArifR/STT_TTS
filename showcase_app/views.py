from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pydub import AudioSegment
import speech_recognition as sr
import edge_tts
import asyncio
import io
# Create your views here.

# def index(request):
#     return HttpResponse("HAI")
    # return render(request, "view/index.html")


def convert_to_wav(audio_file):
    audio = AudioSegment.from_file(audio_file)
    output = io.BytesIO()
    audio.export(output, format="wav", codec="pcm_s16le")
    output.seek(0)
    return output


def stt_view(request):
    if request.method == 'GET':
        return render(request, 'showcase/stt.html')  # Ensure this path is correct and the template exists
    elif request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        if audio_file:
            recognizer = sr.Recognizer()
            try:
                # Convert the audio file to PCM WAV
                audio_data = convert_to_wav(audio_file)
                with sr.AudioFile(audio_data) as source:
                    audio_data = recognizer.record(source)
                    # Use recognize_whisper method for STT
                    text = recognizer.recognize_whisper(audio_data)
                    return JsonResponse({'text': text})
            except sr.UnknownValueError:
                return JsonResponse({'text': "Whisper could not understand the audio."})
            except sr.RequestError as e:
                return JsonResponse({'text': f"Could not request results from Whisper service; {e}"})
            except ValueError as e:
                return JsonResponse({'text': f"Error processing audio file; {e}"})
        return JsonResponse({'error': 'No audio file provided'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

async def text_to_speech(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        voice = request.POST.get('voice', 'en-US-JennyNeural')
        print(f"Requested voice: {voice}") 
        if text:
            tts = edge_tts.Communicate(text, voice=voice)
            audio_stream = bytearray()  # Collect audio data

            try:
                # Fetch and concatenate the audio data from the stream
                async for chunk in tts.stream():
                    if "data" in chunk:
                        audio_stream.extend(chunk["data"])

                # Debug: Check the size of the generated audio
                print(f"Generated audio size: {len(audio_stream)} bytes")

                if len(audio_stream) == 0:
                    return JsonResponse({'error': 'Audio generation failed, no data.'})

                # Return the audio data as an HTTP response
                response = HttpResponse(bytes(audio_stream), content_type='audio/mpeg')
                response['Content-Length'] = len(audio_stream)  # Set the content length explicitly
                response['Content-Disposition'] = 'inline; filename="output.mp3"'
                return response
            
            except Exception as e:
                print(f"Error during TTS processing: {e}")
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'No text provided'})

    return render(request, 'showcase/tts.html')

# Wrap the view function with asyncio to run the async function in Django
def text_to_speech_view(request):
    return asyncio.run(text_to_speech(request))