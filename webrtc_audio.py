import asyncio
import logging
from aiortc import RTCPeerConnection
from aiortc.mediastreams import AudioStreamTrack
import aiohttp
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GPT_MODEL = "gpt-4o-realtime-preview"
OPENAI_API_URL = "https://api.openai.com/v1/audio/conversations"

async def initialize_audio_stream():
    try:
        pc = RTCPeerConnection()

        # Request microphone permission
        audio_sender = pc.addTrack(AudioStreamTrack())

        # Create an AudioStreamTrack for output
        output_track = AudioStreamTrack()
        pc.addTrack(output_track)

        # Create the offer after adding the tracks
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        
        # Set up WebRTC connection
        answer = await process_offer(offer)
        await pc.setRemoteDescription(answer)

        # Start the audio processing
        asyncio.create_task(process_audio(pc, output_track))

        return pc, output_track
    except Exception as e:
        logger.error(f"Error initializing audio stream: {str(e)}")
        raise

async def process_offer(offer):
    try:
        pc = RTCPeerConnection()
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return pc.localDescription
    except Exception as e:
        logger.error(f"Error processing offer: {str(e)}")
        raise

async def send_audio_to_gpt(audio_data):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "audio/wav"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENAI_API_URL, headers=headers, data=audio_data) as response:
                logger.debug(f"GPT API response status: {response.status}")
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"Error from GPT API: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error sending audio to GPT: {str(e)}")
        return None

async def process_audio(pc, audio_track):
    logger.debug("Starting process_audio function")
    while True:
        try:
            # Get audio data from the RTCRtpReceiver
            audio_receivers = [receiver for receiver in pc.getReceivers() if receiver.track and receiver.track.kind == "audio"]
            logger.debug(f"Number of audio receivers: {len(audio_receivers)}")
            if not audio_receivers:
                await asyncio.sleep(0.1)
                continue
            audio_receiver = audio_receivers[0]
            audio_frame = await audio_receiver.readFrame()
            
            if audio_frame:
                # Convert audio frame to bytes
                audio_data = audio_frame.data.tobytes()
                logger.debug(f"Received audio frame with {len(audio_data)} bytes")
                
                # Send audio data to GPT
                gpt_response = await send_audio_to_gpt(audio_data)
                logger.debug(f"Received GPT response: {'Success' if gpt_response else 'None'}")
                
                if gpt_response:
                    # Create an AudioStreamTrack from the GPT response
                    response_track = AudioStreamTrack()
                    response_track.addFrame(gpt_response)
                    logger.debug("Created response AudioStreamTrack")
                    
                    # Replace the existing audio track with the response track
                    pc.replaceTrack(audio_track, response_track)
                    logger.debug("Replaced audio track with GPT response")
                    
                    # Wait for a short duration to allow audio playback
                    await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f'Error in process_audio: {str(e)}')
        
        # Small delay to prevent busy-waiting
        await asyncio.sleep(0.01)

async def stop_audio_processing(pc):
    try:
        logger.debug("Stopping audio processing")
        # Close all transceivers
        for transceiver in pc.getTransceivers():
            await transceiver.stop()
        
        # Close the peer connection
        await pc.close()

        # Cancel all tasks associated with this peer connection
        tasks = [task for task in asyncio.all_tasks() if task.get_name().startswith(f"pc_{id(pc)}")]
        for task in tasks:
            task.cancel()
        
        # Wait for all tasks to be cancelled
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.debug("Audio processing stopped successfully")
    except asyncio.CancelledError:
        logger.debug("Audio processing was cancelled")
    except Exception as e:
        logger.error(f"Error stopping audio processing: {str(e)}")
    finally:
        # Ensure that the event loop is still running
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No running event loop, creating a new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)
