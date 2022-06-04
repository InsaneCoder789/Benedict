import asyncio
import os
import pathlib
import random
import discord
from PIL import Image, ImageFont, ImageDraw

IMG_FORMATS = ["png", "jpg", "jpeg"]  # list of accepted image formats
BG_DIR = pathlib.Path(__file__).parent / "bg"
FONTS_DIR = pathlib.Path(__file__).parent / "fonts"
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


def rounded_rectangle(
    size: tuple[int, int], corner_radius: float, color: tuple[int, ...] | str
) -> Image.Image:
    """
    Get a rectangle with rounded corners of solid color
    """

    im = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((0, 0, size[0], size[1]), corner_radius, color)
    return im


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

    bg = Image.open(bg_path)

    # prepare member avatar
    await member.display_avatar.save(avatar_path)
    avatar = Image.open(avatar_path).resize((540, 540)).convert("RGBA")
    circle_avatar = circle_image(avatar)
    avatar_pos = center_to_corner((350, bg.size[1] // 2), circle_avatar.size)

    # prepare text backdrop
    txt_bd = rounded_rectangle((1070, 350), 25, (0, 0, 0, 175))

    # prepare xp bar
    xp_bar_height = 55
    xp_bar_max_width = 990
    xp_bg_color = tuple([35 for _ in range(3)])
    xp_color = tuple([random.randint(0, 255) for _ in range(3)])
    xp_bar_bg = rounded_rectangle(
        (xp_bar_max_width, xp_bar_height), xp_bar_height / 2, xp_bg_color
    )
    xp_bar = rounded_rectangle(
        (int(xp / max_xp * xp_bar_max_width), xp_bar_height),
        xp_bar_height / 2,
        xp_color,
    )

    # prepare fonts
    font_path = FONTS_DIR / "Roboto Round Regular.ttf"
    username_font = ImageFont.truetype(str(font_path), 70)
    level_font = ImageFont.truetype(str(font_path), 50)

    # prepare final image
    final_img = bg.copy()
    final_draw = ImageDraw.Draw(final_img)

    # text backdrop
    final_img.paste(txt_bd, (717, (bg.size[1] - txt_bd.size[1]) // 2), txt_bd)

    # username
    final_draw.text((757, 395), str(member), fill="white", font=username_font)

    # xp bar
    xp_bar_pos = (759, 580)
    final_img.paste(xp_bar_bg, xp_bar_pos, xp_bar_bg)
    final_img.paste(xp_bar, xp_bar_pos, xp_bar)

    # xp info
    xp_text = f"{xp/1000:.2f}K / {max_xp/1000:.2f}K XP"
    xp_text_size = final_draw.textsize(xp_text, font=level_font)
    xp_text_pos = (
        xp_bar_pos[0] + xp_bar_max_width - xp_text_size[0] - 10,
        xp_bar_pos[1] - xp_text_size[1] - 20,
    )
    final_draw.text(xp_text_pos, xp_text, fill="white", font=level_font)

    # level
    lvl_text = f"Level {level}"
    lvl_text_size = final_draw.textsize(lvl_text, font=level_font)
    lvl_text_pos = (
        xp_bar_pos[0] + 10,
        xp_bar_pos[1] - lvl_text_size[1] - 20,
    )
    final_draw.text(lvl_text_pos, lvl_text, fill="white", font=level_font)

    # member avatar
    final_img.paste(circle_avatar, avatar_pos, circle_avatar)

    # save image and return image path
    await loop.run_in_executor(
        None, final_img.convert("RGB").save, final_img_path
    )
    return final_img_path
