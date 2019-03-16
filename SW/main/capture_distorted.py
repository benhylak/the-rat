from picamera import PiCamera

image_path = "/home/pi/the-rat/SW/main/shot.jpg"
camera = PiCamera()


def capture():
    """
    Takes picture from over the stove.
    :return: Image path
    """
    camera.rotation = 180
    camera.capture(image_path)

    return image_path


if __name__ == "__main__":
    main()
