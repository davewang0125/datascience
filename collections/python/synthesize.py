#!/usr/bin/env python

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Text-To-Speech API sample application .

Example usage:
    python synthesize_text.py --text "hello"
    python synthesize_text.py --ssml "<speak>Hello there.</speak>"
"""

import argparse
from google.cloud import texttospeech

class synthesize:
    __lang__ = "en_US"
    __name__ = "en-US-Standard-C"
    __gender__ = texttospeech.SsmlVoiceGender.NEUTRAL

    def __init__(self, lang, name, gender):
        self.__lang__ = lang
        self.__name__ = name
        if gender == "Male":
            self.__gender__ = texttospeech.SsmlVoiceGender.MALE
        else:
            self.__gender__ = texttospeech.SsmlVoiceGender.FEMALE
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=self.__lang__,
            name=self.__name__,
            ssml_gender=self.__gender__,
        )
            #ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        self.client = texttospeech.TextToSpeechClient()
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
 
    def synthesize_text(self, text, audioFile,):
        """Synthesizes speech from the input string of text."""
        input_text = texttospeech.SynthesisInput(text=text)

        response = self.client.synthesize_speech(
            request={"input": input_text, "voice": self.voice, "audio_config": self.audio_config}
        )

        # The response's audio_content is binary.
        with open(audioFile, "wb") as out:
            out.write(response.audio_content)
            print('text %s Audio content written to file %s' % (text, audioFile))

 
    # [START tts_synthesize_ssml]
    def synthesize_ssml(self, ssml, audioFile):
        """Synthesizes speech from the input string of ssml.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/

        Example: <speak>Hello there.</speak>
        """
        print ("--", ssml)
        input_text = texttospeech.SynthesisInput(ssml=ssml)
        response = self.client.synthesize_speech(
            input=input_text, voice=self.voice, audio_config=self.audio_config
        )

        # The response's audio_content is binary.
        with open(audioFile, "wb") as out:
            out.write(response.audio_content)
            print('ssml %s Audio content written to file %s' % (ssml, audioFile))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument("--text", help="The text from which to synthesize speech.")
    # group.add_argument(
    #     "--ssml", help="The ssml string from which to synthesize speech."
    # )
    group.add_argument("--file", help="The file contains all info for synthesize speech.")
    group.add_argument("--config", help="The file contains all info for synthesize speech.")
    group.add_argument("--datadir", help="The audio directory ", default="/tmp/audio/")
    
    args = parser.parse_args() 
    
    # tool = synthesize(args.config)
    tool = synthesize("en-US", "en-US", "Male")
    file1 = open(args.file, 'r')
    Lines = file1.readlines()
    lnum = 0
    for line in Lines:
        (type, text) = line.split("|")
        audioFile = args.datadir + "audio" + str(lnum) + ".mp3"
        lnum = lnum + 1
        if type == "text":
            tool.synthesize_text(text, audioFile.strip())
        else:
            tool.synthesize_ssml(text, audioFile.strip())
    print("done")