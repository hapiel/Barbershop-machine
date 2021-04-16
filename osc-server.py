"""Barbershop OSC python server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math
import random

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

rootnote = 0
previousChord = [0,0,0]

majorChord = [3.86,7.02,12]
maj7Chord = [3.86,7.02,10.88]
min7Chord = [2.94,7.02,9.69]
dom7Chord = [3.86,7.02,9.69]
dim7Chord = [2.94,6.12,8.84]
halfDim7Chord = [2.94,6.12,9.69]
added6Chord = [3.86,8.84,12]

# majorChord = [4,7,12]
# minorChord = [3,7,12]
# augChord = [4,8,12]
# dimChord = [3,6,12]
# maj7Chord = [4,7,11]
# min7Chord = [3,7,10]
# dom7Chord = [4,7,10]
# dim7Chord = [3,6,9]
# halfDim7Chord = [3,6,10]
# minMaj7Chord = [3,7,11]
# augMaj7Chord = [4,8,11]
# added6Chord = [4,9,12]


def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

def sendToPd(root,chord):
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5006, help="The port to listen on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  client.send_message("/root", root)
  client.send_message("/note1", chord[0])
  client.send_message("/note2", chord[1])
  client.send_message("/note3", chord[2])

def parseInput(input_type, input):
  if input_type == "/rootnote":
    parseRootNote(input)
  elif input_type == "/beat":
    parseBeat(input)

def parseRootNote(note):
  global rootnote
  global previousChord
  rootnote = note
  previousChord = [0,0,0]

def parseBeat(beat):
  global rootnote
  global previousChord
  
  rootchange, chord = generateChord()
  rootnote += rootchange
  previousChord = chord
  sendToPd(rootnote, chord)

def generateChord():
  rootchange = 0
  chord = majorChord
  position = rootnote%12

  print(position)

  x = random.random()

  if previousChord == dom7Chord:
    print("dom7\n")
    #After multiple dom7 chords, try to go to back to a major chord
    if position == 2 and x < 0.9:
      rootchange = 5
      chord = dom7Chord
    elif position == 7 and x < 0.5:
      rootchange = 5
      chord = majorChord
    elif position == 7 and x < 0.9:
      rootchange = 5
      chord = dom7Chord
    elif x < 0.5:
      rootchange, chord = random.choice([(1,dom7Chord),(2,dom7Chord),(5,dom7Chord),(6,dom7Chord),(9,dom7Chord)])
    elif x < 0.8:
      rootchange, chord = random.choice([(1,majorChord),(2,majorChord),(4,majorChord),(5,majorChord),(7,majorChord),(8,majorChord),(11,majorChord)])
    else:
      rootchange, chord = random.choice([(0,dim7Chord),(9,halfDim7Chord)])
  elif previousChord == majorChord:
    print("maj\n")
    if x < 0.7:
      rootchange = 2
      chord = dom7Chord
    elif x < 0.9:
      rootchange = 5
      chord = dom7Chord
    else: 
      rootchange, chord = random.choice([(6,dom7Chord),(7,dom7Chord),(0,maj7Chord),(9,min7Chord),(0,added6Chord)])
  elif previousChord == maj7Chord:
    print("maj7\n")
    rootchange = 0
    chord = majorChord
  elif previousChord == min7Chord:
    print("min7\n")
    rootchange = 5
    chord = majorChord
  elif previousChord == dim7Chord:
    print("dim7\n")
    rootchange = 0
    chord = dom7Chord
  elif previousChord == halfDim7Chord:
    print("halfDim7\n")
    rootchange = 8
    chord = dom7Chord
  elif previousChord == added6Chord:
    print("maj6\n")
    rootchange = 0
    chord = majorChord
  return rootchange, chord

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("/rootnote", parseInput)
  dispatcher.map("/beat", parseInput)

  server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()