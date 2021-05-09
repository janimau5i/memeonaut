from PIL import Image as img, ImageOps, ImageDraw

base_image_path = "./assets/base_image.png"
bonk_device_path = "./assets/bonk_device.png"

gif_out_path = "./bonked.gif"

# hard-coded center of rotation to keep bonk device in paw
rotation_center = (700, 757)
# placement of avatar in base image
avatar_position = (950, 400)

def make_round(avatar):
    """
    Make a circular cutout for the avatar, since that how the avatars are shown inside discord
    """

    # stolen from https://stackoverflow.com/questions/890051/how-do-i-generate-circular-thumbnails-with-pil
    if avatar.size != (256, 256):
    # avatar might be smaller
        print("resizing avatar to 256x256")
        avatar = avatar.resize((256, 256))

    size = avatar.size
    mask = img.new('L', size, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + size, fill=255)

    output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

def create_bonk_gif(user_avatar):
    base_image = img.open(base_image_path)
    bonk_device = img.open(bonk_device_path)
    avatar = img.open(user_avatar)

    avatar = make_round(avatar)
    # put avatar into base image
    base_image.alpha_composite(avatar, avatar_position)

    bonk_device_on_head = bonk_device.rotate(-6, center=rotation_center)
    # bonked: bonk stick on cheems' head
    bonked = img.alpha_composite(base_image, bonk_device_on_head)

    # pre-bonked: bonk stick not on cheems' head (rotated by 30°)
    pre_bonked = img.alpha_composite(
        base_image, bonk_device.rotate(30, center=rotation_center))

    pre_bonked.save(fp=gif_out_path,
                    format="GIF",
                    append_images=[bonked],
                    save_all=True,
                    duration=200,
                    loop=0)
    return gif_out_path

