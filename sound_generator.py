import wave
import math
import struct
import random
import os

def generate_tone(frequency, duration, volume=1.0, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = math.sin(2.0 * math.pi * frequency * t) * volume
        data.append(int(value * 32767.0))
    return data

def generate_jump_sound(filename):
    sample_rate = 44100
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = i / n_samples
        
        # Rising frequency from 300 to 500
        freq = 300 + (300 * progress)
        
        # Envelope: Attack and Decay
        volume = 0.5
        if progress < 0.1:
            volume *= (progress / 0.1)
        else:
            volume *= (1.0 - (progress - 0.1) / 0.9)
        
        # Boost overall volume
        volume *= 0.8
            
        value = math.sin(2.0 * math.pi * freq * t) * volume
        data.append(int(value * 32767.0))
    
    write_wav(filename, data, sample_rate)

def generate_land_sound(filename):
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        progress = i / n_samples
        
        # White noise
        noise = (random.random() * 2.0 - 1.0)
        
        # Envelope: Fast decay but louder start
        volume = 1.0 * (1.0 - progress)**2
        
        value = noise * volume
        data.append(int(value * 32767.0))
        
    write_wav(filename, data, sample_rate)

def generate_skid_sound(filename):
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    data = []
    
    # Filter state
    last_val = 0
    
    for i in range(n_samples):
        # Noise
        noise = (random.random() * 2.0 - 1.0)
        
        # Low pass filter for "rough" sound
        value = last_val * 0.8 + noise * 0.2
        last_val = value
        
        volume = 0.6
        
        data.append(int(value * 32767.0 * volume))
        
    write_wav(filename, data, sample_rate)

def generate_dash_sound(filename):
    sample_rate = 44100
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = i / n_samples
        
        # White noise mixed with tone
        noise = (random.random() * 2.0 - 1.0) * 0.5
        
        # Frequency Sweep (Air rush)
        freq = 800 - (600 * progress)
        tone = math.sin(2.0 * math.pi * freq * t) * 0.5
        
        volume = 0.6 * (1.0 - progress)**0.5
        
        value = (noise + tone) * volume
        data.append(int(value * 32767.0))
        
    write_wav(filename, data, sample_rate)

def generate_jump_variant(filename, pitch_factor=1.0, type="sine"):
    sample_rate = 44100
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = i / n_samples
        
        # Rising frequency
        base_freq = 300 * pitch_factor
        freq = base_freq + (base_freq * progress)
        
        volume = 0.5
        if progress < 0.1: volume *= (progress / 0.1)
        else: volume *= (1.0 - (progress - 0.1) / 0.9)
        
        # Boost overall volume
        volume *= 1.2
        
        if type == "sine":
            value = math.sin(2.0 * math.pi * freq * t) * volume
        elif type == "square":
            value = (1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0) * volume * 0.5
            
        data.append(int(value * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_dash_variant(filename, pitch_factor=1.0):
    sample_rate = 44100
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = i / n_samples
        
        noise = (random.random() * 2.0 - 1.0) * 0.5
        freq = (800 * pitch_factor) - (600 * pitch_factor * progress)
        tone = math.sin(2.0 * math.pi * freq * t) * 0.5
        volume = 0.6 * (1.0 - progress)**0.5
        
        value = (noise + tone) * volume
        data.append(int(value * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_wall_slide_sound(filename):
    sample_rate = 44100
    duration = 0.5
    n_samples = int(sample_rate * duration)
    data = []
    
    last_val = 0
    for i in range(n_samples):
        noise = (random.random() * 2.0 - 1.0)
        
        # Stronger Low pass
        value = last_val * 0.9 + noise * 0.1
        last_val = value
        
        volume = 0.3
        
        data.append(int(value * 32767.0 * volume))
        
    write_wav(filename, data, sample_rate)

def generate_sword_sound(filename):
    # Sharp metallic swish (Link)
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = i / n_samples
        noise = (random.random() * 2.0 - 1.0) * 0.3
        freq = 1500 - (1000 * progress)
        tone = math.sin(2.0 * math.pi * freq * t) * 0.7
        volume = 1.0 * (1.0 - progress)**2
        # Boost
        value = (noise + tone) * volume * 1.2
        # Clip
        value = max(-1.0, min(1.0, value))
        data.append(int(value * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_shuriken_sound(filename):
    # Sharp hiss (Ninja)
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        progress = i / n_samples
        noise = (random.random() * 2.0 - 1.0)
        volume = 0.8 * (1.0 - progress)**4
        value = noise * volume * 1.5
        value = max(-1.0, min(1.0, value))
        data.append(int(value * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_coin_sound(filename):
    # Mario Coin sound (Musical)
    sample_rate = 44100
    duration = 0.4
    n_samples = int(sample_rate * duration)
    data = []
    # B5 (987.77 Hz) to E6 (1318.51 Hz)
    freq1 = 987.77
    freq2 = 1318.51
    switch_point = int(n_samples * 0.15)
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        freq = freq1 if i < switch_point else freq2
        value = math.sin(2.0 * math.pi * freq * t) * 0.8
        # Decay
        if i >= switch_point:
             progress = (i - switch_point) / (n_samples - switch_point)
             value *= (1.0 - progress)
             
        data.append(int(value * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_laugh_sound(filename):
    # Spooky/Glitchy laugh (Madeline)
    sample_rate = 44100
    duration = 0.6
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        # Jittery frequency
        freq = 800 + math.sin(t * 50) * 200 + math.sin(t * 15) * 100
        if (i // 1000) % 2 == 0: freq += 100
        
        value = math.sin(2.0 * math.pi * freq * t) * 0.5
        volume = 1.0 * (1.0 - (i/n_samples))
        # Boost high freq
        value = math.sin(2.0 * math.pi * freq * t) * 0.8
        data.append(int(value * volume * 32767.0))
    write_wav(filename, data, sample_rate)

def generate_squish_sound(filename):
    # Meat squish
    sample_rate = 44100
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    last_val = 0
    for i in range(n_samples):
        noise = (random.random() * 2.0 - 1.0)
        # Wet filter: alternate high pass / low pass? 
        # Just simple low pass with resonance attempt
        value = last_val * 0.6 + noise * 0.4
        last_val = value
        volume = 1.0 * (1.0 - i/n_samples)**2
        data.append(int(value * volume * 32767.0))
    write_wav(filename, data, sample_rate)


def write_wav(filename, data, sample_rate):
    with wave.open(filename, 'w') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 2 bytes per sample (16-bit)
        f.setframerate(sample_rate)
        
        # Pack data
        packed_data = struct.pack('<' + ('h' * len(data)), *data)
        f.writeframes(packed_data)
    print(f"Generated {filename}")

def generate_all_sounds(output_dir="sounds"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    generate_jump_sound(os.path.join(output_dir, "jump.wav"))
    generate_land_sound(os.path.join(output_dir, "land.wav"))
    generate_skid_sound(os.path.join(output_dir, "skid.wav"))
    generate_dash_sound(os.path.join(output_dir, "dash.wav"))
    generate_wall_slide_sound(os.path.join(output_dir, "wall_slide.wav"))
    
    generate_sword_sound(os.path.join(output_dir, "sword.wav"))
    generate_shuriken_sound(os.path.join(output_dir, "shuriken.wav"))
    generate_coin_sound(os.path.join(output_dir, "coin.wav"))
    generate_laugh_sound(os.path.join(output_dir, "laugh.wav"))
    generate_squish_sound(os.path.join(output_dir, "squish.wav"))
    
    # Character Variants
    # Mario: Classic slide whistle-ish (Sine)
    generate_jump_variant(os.path.join(output_dir, "jump_Mario.wav"), 1.0, "sine")
    # Meat Boy: Squishier/Higher
    generate_jump_variant(os.path.join(output_dir, "jump_Super Meat Boy.wav"), 1.5, "square")
    # Link: Normal
    generate_jump_variant(os.path.join(output_dir, "jump_Link.wav"), 0.9, "sine")
    # Madeline: Soft
    generate_jump_variant(os.path.join(output_dir, "jump_Madeline.wav"), 1.2, "sine")
    # Ninja: Sharp
    generate_jump_variant(os.path.join(output_dir, "jump_Ninja (N++).wav"), 1.3, "sine")
    
if __name__ == "__main__":
    generate_all_sounds()
