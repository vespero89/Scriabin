#!/usr/bin/env python3
from __future__ import division
from custom_parser import *
import queue
import sys
from chromagram import compute_chroma
import threading
import sounddevice as sd
from detection import *
from collections import Counter

global q
global mapping
global datastream
global detected_chord
global args


def audio_callback(indata, frames, time, status):
    global q
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, flush=True)
    # Fancy indexing with mapping creates a (necessary!) copy:
    q.put(indata[::args.downsample, mapping])


class DetectionThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global datastream
        global detected_chord
        block = True  # The first read from the queue is blocking ...
        while True:
            try:
                data = q.get(block=block)
            except queue.Empty:
                break
            # block = False  # ... all further reads are non-blocking

            shift = len(data)
            datastream = np.roll(datastream, -shift, axis=0)
            datastream[-shift:, :] = data
            #datastream = data

            # framing audio
            nfft = 8192
            hop_size = 4096
            nFrames = int(np.round(len(datastream) / (nfft - hop_size)))
            x = np.append(datastream, np.zeros(nfft))
            xFrame = np.empty((nfft, nFrames))
            start = 0
            chroma = np.empty((12, nFrames))
            timestamp = np.zeros(nFrames)

            # compute PCP
            for n in range(nFrames):
                xFrame[:, n] = x[start:start + nfft]
                start = start + nfft - hop_size
                chroma[:, n] = compute_chroma(xFrame[:, n], int(args.samplerate/args.downsample))
                if np.all(chroma[:, n] == 0):
                    chroma[:, n] = np.finfo(float).eps
                else:
                    chroma[:, n] /= np.max(np.absolute(chroma[:, n]))
                timestamp[n] = n * (nfft - hop_size) / int(args.samplerate/args.downsample)

            # get max probability path from Viterbi algorithm
            (PI, A, B) = initialize(chroma, templates, nested_cof)
            (path, states) = viterbi(PI, A, B)

            # normalize path
            #         path[:, i] /= sum(path[:, i])

            # choose most likely chord - with max value in 'path'
            final_chords = []
            indices = np.argmax(path, axis=0)
            final_states = np.zeros(nFrames)

            # find no chord zone
            set_zero = np.where(np.max(path, axis=0) < 0.3 * np.max(path))[0]
            if np.size(set_zero) is not 0:
                indices[set_zero] = -1

            # identify chords
            for i in range(nFrames):
                if indices[i] == -1:
                    final_chords.append('NC')
                else:
                    final_states[i] = states[indices[i], i]
                    final_chords.append(chords[int(final_states[i])])

            detected_chord = Counter(final_chords).most_common()
            detected_chord = detected_chord[0][0]
            print('Chord: ' + str(detected_chord))


def main():
    global q
    global mapping
    global datastream
    global detected_chord
    global args

    mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1

    try:
        devices = sd.query_devices()
        id = 0
        for devs in devices:
            if 'USB PnP Sound Device' in devs['name']:
                sd.default.device = id
            id += 1

        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            args.samplerate = device_info['default_samplerate']

        length = int(np.ceil(args.blocksize * args.samplerate / args.downsample))

        q = queue.Queue(maxsize=length)
        datastream = np.zeros((length, len(mapping)))

        stream = sd.InputStream(channels=max(args.channels),
                                samplerate=args.samplerate,
                                blocksize=int(args.samplerate * args.blocksize),
                                callback=audio_callback)

        with stream:
            t = DetectionThread()
            t.start()

    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))


if __name__ == '__main__':
    main()

