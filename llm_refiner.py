import random

LIGHTING = [
    "dramatic cinematic lighting",
    "soft natural golden hour lighting",
    "neon glow reflections and deep shadows",
    "volumetric light rays cutting through fog",
    "high contrast studio lighting"
]

CAMERA = [
    "captured from a wide angle perspective",
    "shot using DSLR photography style",
    "low angle view to enhance depth",
    "shallow depth of field with sharp focus",
    "dynamic cinematic framing"
]

STYLE = [
    "ultra realistic textures",
    "photorealistic details",
    "8k high resolution quality",
    "professional color grading",
    "award winning photography style"
]

ENVIRONMENT = [
    "set in a visually stunning environment",
    "surrounded by a vibrant atmospheric background",
    "creating a powerful immersive mood",
    "with dynamic composition and rich colors",
    "enhancing the storytelling feel of the scene"
]


def refine_prompt(basic_prompt: str):

    lighting = random.choice(LIGHTING)
    camera = random.choice(CAMERA)
    style = random.choice(STYLE)
    env = random.choice(ENVIRONMENT)

    refined = (
        f"A highly detailed scene of {basic_prompt}, {env}. "
        f"The environment is designed to feel cinematic and visually engaging, "
        f"with {lighting}. The image is {camera}, helping create depth and realism "
        f"while highlighting the main subject. {style} bring the scene to life "
        f"with a professional and immersive visual experience."
    )

    return {
        "original_prompt": basic_prompt,
        "refined_prompt": refined,
        "explanation": "Prompt expanded into natural cinematic description for better diffusion output."
    }