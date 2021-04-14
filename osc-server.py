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
previousMidiNote = 0
previousChord = [0,0,0,0]

majorChords = [[0,4,7,12],[-4,0,3,8],[-7,-3,0,5],[-12,-8,-5,0]]
minorChords = [[0,3,7,12],[-3,0,4,9],[-7,-4,0,5],[-12,-9,-5,0]]
augChords = [[0,4,8,12],[-4,0,4,8],[-8,-4,0,4],[-12,-8,-4,0]]
dimChords = [[0,3,6,12],[-3,0,3,9],[-6,-3,0,6],[-12,-9,-6,0]]
maj7Chords = [[0,4,7,11],[-4,0,3,7],[-7,-3,0,4],[-11,-7,-4,0]]
min7Chords = [[0,3,7,10],[-3,0,4,7],[-7,-4,0,3],[-10,-7,-3,0]]
dom7Chords = [[0,4,7,10],[-4,0,3,6],[-7,-3,0,3],[-10,-6,-3,0]]
dim7Chords = [[0,3,6,9],[-3,0,3,6],[-6,-3,0,3],[-9,-6,-3,0]]
halfdim7Chords = [[0,3,6,10],[-3,0,3,7],[-6,-3,0,4],[-10,-7,-4,0]]
minmaj7Chords = [[0,3,7,11],[-3,0,4,7],[-7,-4,0,3],[-11,-7,-3,0]]
augmaj7Chords = [[0,4,8,11],[-4,0,4,7],[-8,-4,0,3],[-11,-7,-3,0]]
simpleChords = majorChords + minorChords
allChords = majorChords + minorChords + augChords + dimChords + maj7Chords + min7Chords + dom7Chords + dim7Chords + halfdim7Chords + minmaj7Chords + augmaj7Chords


def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

def sendToPd(chord):
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5006, help="The port to listen on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  client.send_message("/note1", chord[0])
  client.send_message("/note2", chord[1])
  client.send_message("/note3", chord[2])
  client.send_message("/note4", chord[3])

def parseInput(note_type, note):
  if note_type == "/midinote":
    parseMidiNote(note)
  elif note_type == "/rootnote":
    parseRootNote(note)

def parseRootNote(note):
  global rootnote 
  global lastMidiNote
  global previousChord
  rootnote = note
  chordStructure = random.choice(simpleChords)
  currentChord = [c + note for c in chordStructure]
  lastMidiNote = note
  sendToPd(currentChord) #change from currentChord to chordStructure if relative structure is needed
  previousChord = currentChord

def parseMidiNote(note):
  global rootnote
  global lastMidiNote
  global previousChord
  if rootnote == 0:
    parseRootNote(note)
  else:
    chordStructure = random.choice(allChords)
    #Maak omkering
    for x in range(len(chordStructure)):
      if chordStructure[x] != 0 and random.random() < 0.1:
        print(chordStructure[x])
        if chordStructure[x] < 0:
          chordStructure[x] += 12
        else:
          chordStructure[x] -= 12
        print(chordStructure)
    
    currentChord = [c + note for c in chordStructure]
    while (abs(min(currentChord)-min(previousChord)) > max(12,abs(lastMidiNote-note))):
      currentChord = [c + note for c in chordStructure]
    sendToPd(currentChord) #change from currentChord to chordStructure if relative structure is needed
    lastMidiNote = note
    previousChord = currentChord


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("/rootnote", parseInput)
  dispatcher.map("/midinote", parseInput)

  server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()