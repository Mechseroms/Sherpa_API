from openai import OpenAI
api_key = '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'
messages = [ {"role": "system", "content":  
              "You are a intelligent assistant."} ] 

assistant = OpenAI(api_key=api_key)


def generate_text(prompt):
    messages.append( 
        {"role": "user", "content": prompt}, 
    ) 
    response = assistant.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

import torch, datetime, string, random
from diffusers import AnimateDiffPipeline, LCMScheduler, MotionAdapter, StableDiffusionXLPipeline, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
from huggingface_hub import hf_hub_download


def construct_unique_name(length, type):
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(":", "").replace(".", "")
    letters = string.ascii_letters
    return f"{timestamp}-gen-{type}-{''.join(random.choice(letters) for i in range(length))}"

def generate_image(prompt):

    base = "stabilityai/stable-diffusion-xl-base-1.0"
    repo = "ByteDance/SDXL-Lightning"
    ckpt = "sdxl_lightning_4step_lora.safetensors" # Use the correct ckpt for your step setting!

    # Load model.
    pipe = StableDiffusionXLPipeline.from_pretrained(base, torch_dtype=torch.float16, variant="fp16").to("cuda")
    pipe.load_lora_weights(hf_hub_download(repo, ckpt))
    pipe.fuse_lora()

    # Ensure sampler uses "trailing" timesteps.
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    file_name = construct_unique_name(6, type="image")
    file_path = f"generated_images/{file_name}.jpg"

    # Ensure using the same inference steps as the loaded model and CFG set to 0.
    pipe(prompt, num_inference_steps=4, guidance_scale=0).images[0].save(file_path)
    return file_path

def generate_gif(prompt):
    adapter = MotionAdapter.from_pretrained("wangfuyun/AnimateLCM", torch_dtype=torch.float16)
    pipe = AnimateDiffPipeline.from_pretrained("emilianJR/epiCRealism", motion_adapter=adapter, torch_dtype=torch.float16)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear")

    pipe.load_lora_weights("wangfuyun/AnimateLCM", weight_name="AnimateLCM_sd15_t2v_lora.safetensors", adapter_name="lcm-lora")
    pipe.set_adapters(["lcm-lora"], [0.8])

    pipe.enable_vae_slicing()
    pipe.enable_model_cpu_offload()

    output = pipe(
        prompt=prompt,
        negative_prompt="bad quality, worse quality, low resolution",
        num_frames=15,
        guidance_scale=2.0,
        num_inference_steps=6,
        generator=torch.Generator("cpu").manual_seed(0),
    )
    frames = output.frames[0]

    file_name = construct_unique_name(6, type="gif")
    file_path = f"generated_gifs/{file_name}.gif"
    print(file_path)
    export_to_gif(frames, file_path)
    return file_path