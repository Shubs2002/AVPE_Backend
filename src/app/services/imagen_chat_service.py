"""
Imagen Chat Service - Frame generation using chat sessions for continuity

This service uses Gemini chat sessions to generate frames with better continuity.
For continuous segments, it updates the previous frame rather than generating from scratch.
"""

import os
from io import BytesIO
from PIL import Image
from datetime import datetime
from google import genai
from google.genai import types
from app.config import settings


def get_genai_client():
    """Get configured Gemini client"""
    return genai.Client(api_key=settings.GOOGLE_API_KEY)


class FrameGenerationChat:
    """
    Manages a chat session for frame generation with continuity.
    
    Usage:
        chat = FrameGenerationChat()
        
        # Generate first frame (new scene)
        first_frame = chat.generate_first_frame(
            character_images=[img1, img2],
            frame_description="...",
            character_names=["Floof", "Poof"],
            character_subjects=["fluffy pink creature", "small blue robot"],
            style="cute character animation"
        )
        
        # Generate last frame (continuous from first)
        last_frame = chat.generate_last_frame(
            last_frame_description="..."
        )
        
        # Next segment - if continuous, reuse chat
        # If new scene, create new FrameGenerationChat instance
    """
    
    def __init__(self, model: str = "gemini-2.5-flash-image"):
        """Initialize chat session"""
        self.client = get_genai_client()
        self.model = model
        self.chat = None
        self.current_frame = None
        self.character_images = []
        self.character_names = []
        self.character_subjects = []
        self.style = None
        
    def _build_character_identification(self) -> str:
        """Build character identification section"""
        if not self.character_names or not self.character_subjects:
            return ""
        
        identification = "\n\n**CHARACTER IDENTIFICATION**:\n"
        for i, (name, subject) in enumerate(zip(self.character_names, self.character_subjects), 1):
            identification += f"- Character {i} is **{name}**: {subject}\n"
        return identification
    
    def _build_style_instruction(self) -> str:
        """Build style instruction"""
        if not self.style:
            return ""
        return f"\n\n**VISUAL STYLE**: {self.style}\nMaintain this style throughout."
    
    def generate_first_frame(
        self,
        character_images: list,
        frame_description: str,
        character_names: list = None,
        character_subjects: list = None,
        style: str = None,
        aspect_ratio: str = "9:16",
        resolution: str = "2K",
        output_dir: str = "frames"
    ) -> tuple[Image.Image, str]:
        """
        Generate first frame for a new scene using chat.
        
        Args:
            character_images: List of PIL Image objects (character photos)
            frame_description: Detailed description of the frame
            character_names: List of character names
            character_subjects: List of character appearance descriptions
            style: Visual style
            aspect_ratio: Image aspect ratio
            resolution: Image resolution (1K, 2K, 4K)
            output_dir: Directory to save frame
            
        Returns:
            tuple: (PIL.Image, filepath)
        """
        print(f"🎨 Creating new chat session for first frame...")
        
        # Store character info for continuity
        self.character_images = character_images
        self.character_names = character_names or []
        self.character_subjects = character_subjects or []
        self.style = style
        
        # Create new chat session
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                )
            )
        )
        
        # Build prompt
        char_identification = self._build_character_identification()
        style_instruction = self._build_style_instruction()
        
        num_chars = len(character_images)
        char_refs_text = "characters" if num_chars > 1 else "character"
        
        prompt = f"""Create a high-quality image based on this description:

{frame_description}
{char_identification}
{style_instruction}

⚠️ CRITICAL CHARACTER CONSISTENCY:
Use the reference image(s) EXACTLY as provided. DO NOT modify the {char_refs_text}:
- Keep EXACT same appearance, colors, features, clothing from reference images
- Keep EXACT same body shape, size, proportions
- DO NOT change art style or make more realistic/cartoonish
- Focus on the POSE, ENVIRONMENT, and LIGHTING described

Requirements:
- High quality, detailed rendering
- ZERO changes to character appearance
- Each character clearly visible and distinct
- Clear, vibrant colors
- Professional composition"""
        
        print(f"📝 Sending first frame request...")
        print(f"👥 Using {num_chars} character reference(s)")
        if style:
            print(f"🎭 Style: {style}")
        
        # Send message with character images
        contents = [prompt] + character_images
        response = self.chat.send_message(contents)
        
        # Extract generated image
        generated_image = None
        for part in response.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif image := part.as_image():
                generated_image = image
                print(f"✅ First frame generated: {generated_image.size}")
                break
        
        if generated_image is None:
            raise Exception("No image generated in response")
        
        # Save frame
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"first_frame_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        generated_image.save(filepath, "PNG")
        print(f"💾 First frame saved: {filepath}")
        
        # Store current frame for continuity
        self.current_frame = generated_image
        
        return generated_image, filepath
    
    def generate_last_frame(
        self,
        last_frame_description: str,
        aspect_ratio: str = "9:16",
        resolution: str = "2K",
        output_dir: str = "frames"
    ) -> tuple[Image.Image, str]:
        """
        Generate last frame by updating the current frame in the chat.
        This maintains continuity from the first frame.
        
        Args:
            last_frame_description: Description of the ending frame
            aspect_ratio: Image aspect ratio
            resolution: Image resolution
            output_dir: Directory to save frame
            
        Returns:
            tuple: (PIL.Image, filepath)
        """
        if self.chat is None or self.current_frame is None:
            raise Exception("Must generate first frame before last frame")
        
        print(f"🎨 Updating frame in existing chat session...")
        
        # Build update prompt
        char_identification = self._build_character_identification()
        style_instruction = self._build_style_instruction()
        
        prompt = f"""Update the previous image to show this ending pose/position:

{last_frame_description}
{char_identification}
{style_instruction}

⚠️ CRITICAL CONTINUITY REQUIREMENTS:
- Keep the SAME characters with EXACT same appearance
- Keep the SAME environment and lighting
- Keep the SAME visual style
- ONLY change: character poses, positions, and any objects that moved
- Maintain all colors, textures, and atmosphere from the previous frame

This is the ending frame of the same scene, so everything should feel continuous."""
        
        print(f"📝 Sending last frame update request...")
        
        # Send update message (chat maintains context)
        response = self.chat.send_message(
            prompt,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                )
            )
        )
        
        # Extract generated image
        generated_image = None
        for part in response.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif image := part.as_image():
                generated_image = image
                print(f"✅ Last frame generated: {generated_image.size}")
                break
        
        if generated_image is None:
            raise Exception("No image generated in response")
        
        # Save frame
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"last_frame_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        generated_image.save(filepath, "PNG")
        print(f"💾 Last frame saved: {filepath}")
        
        # Update current frame
        self.current_frame = generated_image
        
        return generated_image, filepath
    
    def generate_next_segment_first_frame(
        self,
        frame_description: str,
        aspect_ratio: str = "9:16",
        resolution: str = "2K",
        output_dir: str = "frames"
    ) -> tuple[Image.Image, str]:
        """
        Generate first frame for next continuous segment.
        Uses the chat context to maintain continuity.
        
        Args:
            frame_description: Description of the new starting frame
            aspect_ratio: Image aspect ratio
            resolution: Image resolution
            output_dir: Directory to save frame
            
        Returns:
            tuple: (PIL.Image, filepath)
        """
        if self.chat is None:
            raise Exception("Chat session not initialized. Use generate_first_frame() for new scenes.")
        
        print(f"🎨 Generating next segment's first frame (continuous)...")
        
        # The last frame becomes the basis for the next first frame
        prompt = f"""Continue the scene with this new starting position:

{frame_description}

⚠️ CRITICAL CONTINUITY:
- This is a CONTINUOUS scene from the previous frame
- Keep ALL characters, environment, lighting, and style EXACTLY the same
- ONLY update character poses/positions as described
- Maintain perfect continuity - this should feel like the next moment"""
        
        print(f"📝 Sending continuous frame request...")
        
        response = self.chat.send_message(
            prompt,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                )
            )
        )
        
        # Extract generated image
        generated_image = None
        for part in response.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif image := part.as_image():
                generated_image = image
                print(f"✅ Continuous frame generated: {generated_image.size}")
                break
        
        if generated_image is None:
            raise Exception("No image generated in response")
        
        # Save frame
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"first_frame_continuous_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        generated_image.save(filepath, "PNG")
        print(f"💾 Continuous frame saved: {filepath}")
        
        # Update current frame
        self.current_frame = generated_image
        
        return generated_image, filepath
