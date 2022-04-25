import asyncio
import os
import pathlib
import random
import discord
from PIL import Image, ImageFont, ImageDraw

IMG_FORMATS = ["png", "jpg", "jpeg"]  # list of accepted image formats
BG_DIR = pathlib.Path(__file__).parent / "bg"
CACHE_DIR = pathlib.Path(__file__).parent / "cache"


def delete_dir(dir_path: pathlib.Path):
    for filename in os.listdir(dir_path):
        file_path = dir_path / filename

        if file_path.is_dir():
            delete_dir(file_path)
        else:
            os.remove(file_path)

    os.rmdir(dir_path)


# clear caches on startup
if CACHE_DIR.exists():
    print("Clearing image cache...")
    delete_dir(CACHE_DIR)
    print("Image cache cleared!")

os.mkdir(CACHE_DIR)


def center_to_corner(
    center_pos: tuple[int, int], size: tuple[int, int]
) -> tuple[float, float]:
    return (
        center_pos[0] - size[0] // 2,
        center_pos[1] - size[1] // 2,
    )


def circle_image(im: Image.Image) -> Image.Image:
    """
    Get a circular cut-out of a PIL Image
    """

    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)

    circle_image = im.copy()
    circle_image.putalpha(mask)
    return circle_image


async def generate_levels_image(
    member: discord.Member, level: int, xp: int, max_xp: int
) -> pathlib.Path:
    """
    Generates an image for displaying a member's level and XP.
    Returns a path to the generated image.
    """

    loop = asyncio.get_event_loop()

    # define paths
    bg_path = random.choice(
        [
            BG_DIR / image_name
            for image_name in os.listdir(BG_DIR)
            if image_name.split(".")[-1] in IMG_FORMATS
        ]
    )
    avatar_path = CACHE_DIR / f"member_avatar_{member.id}.png"
    final_img_path = CACHE_DIR / f"member_levels_{member.id}.jpg"

    # prepare member avatar
    await member.display_avatar.save(avatar_path)
    avatar = Image.open(avatar_path, formats=IMG_FORMATS).resize((540, 540))
    circle_avatar = circle_image(avatar)

    # prepare final image
    bg = Image.open(bg_path, formats=IMG_FORMATS)
    avatar_pos = center_to_corner((350, bg.size[1] // 2), circle_avatar.size)
    bg.paste(circle_avatar, avatar_pos, circle_avatar)
    await loop.run_in_executor(None, bg.convert("RGB").save, final_img_path)

    return final_img_path
