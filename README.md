# Stenograph Project

## Members 
**Team Members** <br>
Muhammad Azreen Bin Muhammad  <br>
Chng Song Heng Aloysius <br>
Muhammad Firdauz Bin Kamarulzaman <br>
Timothy Zoe Delaya <br>
Shaikh Mohamed Irfan  <br>
Nicholas Tan Qin Sheng <br>

## Introduction

## Stenography - Variety of media format
### 1. Image
#### 1.1 Text to Image

### 2. Audio
#### 2.1 Text to Audio
This section explains the **text-to-audio encoding and decoding** functionality using LSB (Least Significant Bit) steganography. The program allows embedding and extracting secret messages within `.wav` audio files.

##### 2.1.1 Encoding Process

1. **Reading the Audio File**:
   - The `.wav` file is opened using the `wave` module. The audio data is read as frames and then converted into a byte array.

2. **Message Conversion**:
   - The message is converted into binary format. Each character in the message is represented as an 8-bit binary number.

3. **Storing the Message Length**:
   - The length of the message (in characters) is converted into a 32-bit binary number and stored in the first 32 bytes of the audio file. This helps in decoding to know how many characters to retrieve.

4. **Embedding the Message**:
   - The binary message is embedded into the least significant bits of the audio file’s bytes. The number of bits (1-8) that are overwritten per byte is determined by the user input.

5. **Writing the Encoded Audio**:
   - The modified byte array is written back to a new `.wav` file, which now contains the hidden message.

##### 2.1.2 Decoding Process

1. **Reading the Encoded Audio**:
   - The encoded audio file is opened, and the byte data is read as it was during the encoding process.

2. **Retrieving the Message Length**:
   - The first 32 bits are extracted from the audio file, representing the length of the hidden message (in characters). This value is converted back into an integer.

3. **Extracting the Message**:
   - Using the retrieved message length, the corresponding bits from the audio file are read and decoded from their least significant bits back into the original message text.

##### 2.1.3 Key Functions

- `encode(byte_array, message, bits)`: Embeds the message into the byte array of the audio file using LSB encoding.
- `run_encode(audio_path, message, audio_output_path, bits)`: This function reads the audio file, encodes the message, and writes a new audio file with the hidden message.
- `run_decode(audio_output_path, bits)`: This function decodes the message from the audio file by extracting the least significant bits.

##### 2.1.4 Notes
- **Bit Usage**: The number of bits (1-8) selected affects both message capacity and audio quality. Using fewer bits ensures higher audio quality, while more bits allow longer messages.
- **Error Handling**: If the message length exceeds the audio file’s capacity, an error will be raised during decoding.
  
### 3. Video
#### 3.1 Text to Video

## Setting up
### Pre-requisite
Please install the required Python libraries
> pip install -r requirements.txt

### Launch web application
> python app.py

## Credits & References
UX/UI - [TailwindCSS](https://tailwindcss.com/)

