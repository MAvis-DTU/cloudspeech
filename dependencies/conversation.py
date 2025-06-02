from __init__ import *
from dependencies.helpers import *
from googlestream import *

def conditional_say(pepper_response, 
                    openaiClient, 
                    naoServices, 
                    elevenlabsStream, 
                    verbose):
    if naoServices:
        if elevenlabsStream.voice_select == 0 and elevenlabsStream.multi_lingual:
            audio_gesture_thread = AudioGestureGeneratorThread(verbose=verbose, text=pepper_response, openaiClient=openaiClient, elevenlabsStream=elevenlabsStream)
            thread_returns = audio_gesture_thread.run()
            gesture_thread = GestureThread(naoServices, thread_returns[1][0], thread_returns[1][1])
            # Execute the gesture thread and then play the audio stream
            gesture_thread.run()
            stream(thread_returns[0])
            # Terminate the gesture thread after the audio stream has finished playing
            gesture_thread.terminate()
            
        elif elevenlabsStream.voice_select == 0 and not elevenlabsStream.multi_lingual:
            if verbose:
                print("-----------------")
                print("Gesture generation: START")
                start = time.time()
            split_sentences, gesture_numbers = get_gestures(pepper_response, openaiClient, verbose=verbose)
            if verbose:
                end = time.time()
                print(f"Time taken: {end-start:.2f} s")
                print("Gesture generation: END")
                print("-----------------")
            gesture_thread = GestureThread(naoServices, split_sentences, gesture_numbers)
            gesture_thread.run()
            naoServices.nao_say(pepper_response)
            gesture_thread.terminate()
    elif elevenlabsStream:
        if verbose:
            print("-----------------")
            print("Audio generation: START")
            start = time.time()
        audio_stream = elevenlabsStream._generate_stream(pepper_response)
        if verbose:
            end = time.time()
            print(f"Time taken: {end-start:.2f} s")
            print("Audio generation: END")
            print("-----------------")
            print("Audio stream: START")
            start = time.time()
        stream(audio_stream)
        if verbose:
            end = time.time()
            print(f"Time taken: {end-start:.2f} s")
            print("Audio stream: END\n")
    else:
        return

def getName(main_prompt: str, 
            temperature: float, 
            openaiClient, 
            naoServices,
            elevenlabsStream,
            max_tokens: int =255,
            top_p: float =1.0,
            language: str ='en-US', 
            robot_name: str ='Pepper', 
            verbose: bool =False,
            gpt_model="gpt-4-turbo"): 
    # Some introductory phrases
    prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"You are a robot called Pepper, and you are engaging in a conversation. Briefly introduce yourself in one sentence ask for the other person's name in a fun and engaging way. Use the following language: {language}"}]}]
    introduction = getResponse(prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, openaiClient=openaiClient, model=gpt_model, verbose=verbose, response_type='Name')
    conditional_say(introduction, openaiClient=openaiClient, naoServices=naoServices, elevenlabsStream=elevenlabsStream, verbose=verbose)

    print(f'{robot_name}: ' + introduction)
    if verbose:
        print("-----------------")

    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)

    # loop until the user says their name
    print("### GET NAME LOOP ###")
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            if verbose: 
                print("-----------------")
                print("Listening: START")
                start = time.time()
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            #listen("Start")
            human_response = client.streaming_recognize(streaming_config, requests)
            human_response = listen_print_loop('Human', human_response, verbose=verbose)
            if verbose:
                end = time.time()
                print(f"Time taken: {end-start:.2f} s")
                print("Listening: END\n")
                print("-----------------")
                
            system_message  = 'What did the human say his name was in the following sentence? \n If the human did not specify write: -nothing, otherwise write ONLY the name of the human.\n\n'

            prompt = [{"role": "system", "content": [{"type": "text", "text": system_message}]}, {"role": "user", "content": [{"type": "text", "text": human_response}]}]          
            
            pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=1.0, \
                                          openaiClient=openaiClient, frequency_penalty=1.5, presence_penalty=1, \
                                          model=gpt_model, verbose=verbose, response_type='Name')

            if '-nothing' in pepper_response.lower() or '-ingenting' in pepper_response.lower():
                prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"You missed the other person's name, and you should ask again. Be kind and understanding. The response should be in {language}."}]}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=1.0, openaiClient=openaiClient, model=gpt_model, verbose=verbose, response_type='Name')
                conditional_say(pepper_response, openaiClient=openaiClient, naoServices=naoServices, elevenlabsStream=elevenlabsStream, verbose=verbose)

                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
            else: 
                name = pepper_response
                prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"Great! So the human has introduced themselves as {name}. Now acknowledge it. The response should be in {language}."}]}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=top_p, openaiClient=openaiClient, model=gpt_model, verbose=verbose, response_type='Name')
                conditional_say(pepper_response, openaiClient=openaiClient, naoServices=naoServices, elevenlabsStream=elevenlabsStream, verbose=verbose)

                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
                return name, pepper_response

def startConversation(prompt, 
                      speaker, 
                      temperature, 
                      max_tokens, 
                      top_p, 
                      openaiClient,
                      naoServices,
                      elevenlabsStream,
                      language='en-US', 
                      vision=True,
                      gpt_model="gpt-4-turbo",
                      verbose=False):
    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)
    voice_changed = 0
    # start the conversation loop
    print("### CONVERSATION LOOP ###")

    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            if verbose: 
                print("-----------------")
                print("Listening: START")
                start = time.time()
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            human_response = client.streaming_recognize(streaming_config, requests)
            
            #print('Human: ')
            try:
                human_response = listen_print_loop(speaker, human_response, verbose=verbose)
            except Exception as e:
                if verbose:
                    print(e)
                continue
                    
            if verbose:
                end = time.time()
                print(f"Time taken: {end-start:.2f} s")
                print("Listening: END\n")
                print("-----------------")
            
            if elevenlabsStream.enable_voice_change:
                voice_changed = changeVoice('Human:' + human_response, 
                                            openaiClient=openaiClient, 
                                            elevenlabsStream=elevenlabsStream, 
                                            verbose=verbose,
                                            model=gpt_model)

            # fetch the string from objects.txt 
            with open('dependencies/vision/objects.txt', 'r') as file:
                objects = file.read()

            # fetch the string from vision.txt if vision is enabled
            if vision:
                with open('dependencies/vision/vision.txt', 'r') as file:
                    vision = file.read()
                prompt += [{"role": "user", "content": [{"type": "text", "text": human_response + '\n\n' + objects + '\n\n' "This is your own descripton of what you see with your eyes: " + vision}]}]
            else:
                prompt += [{"role": "user", "content": [{"type": "text", "text": human_response + '\n\n' + objects}]}]

            if voice_changed:
                # response = "Certainly! I will change my voice. Is it better now?"
                voice_prompt = prompt + [{"role": "system", "content": "You have changed your voice. Showcase the new voice and ask if the human likes it."}]
                response = getResponse(voice_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, openaiClient=openaiClient, model=gpt_model, verbose=verbose, response_type='Convo')
            else: 
                response = getResponse(prompt, temperature=temperature, max_tokens=max_tokens, top_p = top_p, openaiClient=openaiClient, model=gpt_model, verbose=verbose, response_type='Convo')

            # We should now generate some gestures for the robot
            conditional_say(response, openaiClient=openaiClient, naoServices=naoServices, elevenlabsStream=elevenlabsStream, verbose=verbose)
            print('Pepper: ' + response)
            if verbose:
                print("-----------------")

            prompt += [{"role": "assistant", "content": response}]
