#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example 6: STT + Dialog - queryByVoice"""

from __future__ import print_function

import grpc
import time
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import os
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
try:
  GPIO.setmode(GPIO.BCM)
except Exception as e:
  GPIO.cleanup()
  GPIO.setmode(GPIO.BCM)
GPIO.setup([17,27,22], GPIO.OUT)
GPIO.setup([3], GPIO.IN)
red=17
yellow=27
green=22
def set_color(color):
    GPIO.output(17,GPIO.LOW)
    GPIO.output(27,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(color,GPIO.HIGH)


sensor=Adafruit_DHT.DHT11
pin=3
### STT

import audioop
from ctypes import *

RATE = 16000
CHUNK = 512

HOST = 'gate.gigagenie.ai'
PORT = 4080

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

def generate_request():
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()
		messageReq = gigagenieRPC_pb2.reqQueryVoice()
		messageReq.reqOptions.lang=0
		messageReq.reqOptions.userSession="1234"
		messageReq.reqOptions.deviceId="aklsjdnalksd"
		yield messageReq
		for content in audio_generator:
			message = gigagenieRPC_pb2.reqQueryVoice()
			message.audioContent = content
			yield message
			rms = audioop.rms(content,2)

def queryByVoice():
  global sensor,pin
  print ("\n\n\n질의할 내용을 말씀해 보세요.\n\n듣고 있는 중......\n")
  channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials())
  stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)
  request = generate_request()
  resultText = ''
  response = stub.queryByVoice(request)
  if response.resultCd == 200:
          print("질의 내용: %s" % (response.uword))
          if response.uword.find('온도')>=0 or response.uword.find('습도')>=0:
              humid,temper=Adafruit_DHT.read_retry(sensor,pin)
              return "현재 온도는 "+str(temper)+ "도 이며 현재 습도는 "+str(humid)+"퍼센트 입니다.."
          elif response.uword.find('빨간불')>=0:
              set_color(red)
              return "빨간불을 켭니다."
            
          for a in response.action:
                  response = a.mesg
                  parsing_resp = response.replace('<![CDATA[', '')
                  parsing_resp = parsing_resp.replace(']]>', '')
                  resultText = parsing_resp
                  print("\n질의에 대한 답변: " + parsing_resp +'\n\n\n')

  else:
          print("\n\nresultCd: %d\n" % (response.resultCd))
          print("정상적인 음성인식이 되지 않았습니다.")
  return resultText

def main():
	queryByVoice()
	time.sleep(0.5)

if __name__ == '__main__':
	main()
