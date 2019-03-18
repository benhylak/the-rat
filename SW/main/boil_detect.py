from skimage.measure import compare_ssim
import cv2
import numpy as np
import time
import queue
from moving_average import MovingAverage
import enum


class BoilState(enum.Enum):
    not_boiling = 0
    is_simmering = 1
    is_boiling = 2


class UpdateState(enum.Enum):
    initial_setup = 0
    process_frames = 1
    perform_comparison = 2


class BoilDetector:

    def __init__(self):
        # temp
        self.file = open("f.txt", "a")
        self.MIN_BOILING_TEMP = 0  # temp considered to be boiling
        self.THRESH = 0.985  # thresh to boil
        self.MASK_THRESH = 0.5  # thresh to recalculate mask
        self.SSIM_COUNT = 5  # how often median will be found
        self.BOIL_COUNT = 10  # window size of the boiling list
        self.FRAME_FREQUENCY = 1  # frequency of frames being compared
        self.frames_elapsed = 0  # frames that have passed

        # keeps track of each burner's state, default no-boiling
        self.boil_state = [BoilState.not_boiling,
                           BoilState.not_boiling,
                           BoilState.not_boiling,
                           BoilState.not_boiling]

        # defines what state the update function is in
        self.update_state = UpdateState.initial_setup

        # List of MovingAverages holding X number of calculated SSIMs for each burner
        # median SSIM is determined once each queue reaches X SSIMs
        self.median_SSIM = [MovingAverage(self.SSIM_COUNT),
                            MovingAverage(self.SSIM_COUNT),
                            MovingAverage(self.SSIM_COUNT),
                            MovingAverage(self.SSIM_COUNT)]

        # List of MovingAverages holding X number of calculated median SSIMs for each burner
        # used to determine if a given pot is detected to be boiling
        self.boiling = [MovingAverage(self.BOIL_COUNT),
                        MovingAverage(self.BOIL_COUNT),
                        MovingAverage(self.BOIL_COUNT),
                        MovingAverage(self.BOIL_COUNT)]

        self.start_boiling = [0, 0, 0, 0]  # times each burner started boiling
        self.masks = [None, None, None, None]  # mask used for each burner

        self.last_image = None
        self.current_image = None
        self.last_quads = [None, None, None, None]
        self.current_quads = [None, None, None, None]

    def __compare_images(self, gray1, gray2):
        """
        Compute the Structural Similarity Index (SSIM) between the two
        images, ensuring that the SSIM is returned
        :param gray1: grayscale image
        :param gray2: grayscale image
        :return: SSIM score between two images between 0 and 1
        """
        (score, diff) = compare_ssim(gray1, gray2, full=True)
        return score

    def __create_mask(self, img):
        """
        Returns a mask with the cut out ellipse to be used in all iterations.
        Created using the input image after calculating ellipse.
        :param img: Image off which ellipse is based
        :return: Mask to be used for the image
        """
        copy = img.copy()
        gray_img = cv2.cvtColor(copy, cv2.COLOR_BGR2GRAY)

        # increase the contrast in the image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl1 = clahe.apply(gray_img)

        # create a black mask
        mask = np.zeros_like(gray_img)

        # thresh
        (thresh, im_bw) = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # find contours
        contours, _ = cv2.findContours(im_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # sort the contours from largest area to smallest, get the largest contour
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        cnt = sorted_contours[0]

        # fit an ellipse to the largest contour
        ellipse = cv2.fitEllipse(cnt)
        # Unpack the properties of the returned ellipse
        x = int(ellipse[0][0])  # x coordinate of the center
        y = int(ellipse[0][1])  # y coordinate of the center
        a = int(ellipse[1][0] / 2)  # major semi-axis
        b = int(ellipse[1][1] / 2)  # minor semi-axis
        theta = int(ellipse[2])  # rotation angle

        # draw the found ellipse onto the mask
        cv2.ellipse(mask, (x, y), (a, b), theta, 0, 360, ((255, 255, 255)), -1)
        return mask

    def __apply_mask(self, img, mask):
        """
        Applies the given mask to the input image.
        :param img: Image to be masked
        :param mask: Mask to be used
        :return: A masked version of the image
        """
        copy = img.copy()
        return cv2.bitwise_and(copy, copy, mask=mask)

    def __split_frame(self, frame):
        """
        Takes input frame and splits it into 4 equal quadrants.
        Best bet so far would be to take in distorted frame.
        :param frame: Frame to be split.
        :return: Four images representing the split frame.
        """
        height, width = frame.shape[:2]
        center_col = int(width / 2)
        center_row = int(height / 2)

        first_quad = frame[0:center_row, 0:center_col]
        second_quad = frame[0:center_row, center_col:width]
        third_quad = frame[center_row:height, 0:center_col]
        fourth_quad = frame[center_row:height, center_col:width]

        return [first_quad, second_quad, third_quad, fourth_quad]

    def __split_frame_mod(self, frame):
        """
        Takes input frame and splits it into 4 equal quadrants.
        Best bet so far would be to take in distorted frame.
        Splits it as close to stove as possible.
        :param frame: Frame to be split.
        :return: Four images representing the split frame.
        """
        height, width = frame.shape[:2]
        eighth_col = int(width / 4)
        center_col = int(width / 2)
        center_row = int(height / 2)

        first_quad = frame[0:center_row, eighth_col:center_col]
        second_quad = frame[0:center_row, center_col:width - eighth_col]
        third_quad = frame[center_row:height, eighth_col:center_col]
        fourth_quad = frame[center_row:height, center_col:width - eighth_col]

        return [first_quad, second_quad, third_quad, fourth_quad]

    def ___get_score(self, mask, quad1, quad2):
        """
        Helper function to return SSIM score between two images
        :param mask: Mask to be applied to image
        :param quad1: First image quadrant being compared
        :param quad2: Second image quadrant
        :return:
        """
        masked1 = self.__apply_mask(quad1, mask)
        masked2 = self.__apply_mask(quad2, mask)

        # converts the masked images images to grayscale
        gray1 = cv2.cvtColor(masked1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(masked2, cv2.COLOR_BGR2GRAY)

        # compare the two images
        return self.__compare_images(gray1, gray2)

    def __check_boiling(boiling, thresh):
        """
        Checks to see if the past values recorded in boiling
        average out to be less than a given boiling threshhold.
        :param boiling: List containing an X number of median SSIM's
        :param thresh: Value signaling if average has fallen beneath certain boiling thresh
        :return: Boolean signaling if the input list values indicate boiling
        """
        average = sum(boiling) / len(boiling)
        if average < thresh:
            return True
        else:
            return False

    def __initialize_masks(self, burners):
        """
        Refreshes mask if a pot is newly detected on the burners.
        :param burners: Stove burners
        """
        masks = self.masks
        for mask, burner, quad in zip(masks, burners, self.last_quads):
            # mask never made before
            if mask is None and quad is not None and burner.pot_detected:
                self.masks.append(self.__create_mask(quad))
            # if pot no longer detected resets the mask
            elif burner.pot_detected is False:
                idx = masks.index(mask)
                self.masks[idx] = None

    def update(self, frame_path, stove):
        """
        Takes an input frame and updates the boiling state of the burners.
        :param frame_path: Input frame path to be used to update boiling status
        :param stove: Stove object holding current stove state
        """
        # recurring processes
        frame = cv2.imread(frame_path)
        self.file = open("f.txt", "a")
        # updates frames_elapsed
        self.frames_elapsed = self.frames_elapsed + 1
        burners = stove.get_burners()

        # creates new masks if a pot was added or thresh changes
        self.__initialize_masks(burners)

        # initial setup
        if self.update_state is UpdateState.initial_setup:
            self.file.seek(0)  # clear the file on initial setup
            self.file.truncate()
            self.last_image = frame
            self.last_quads = self.__split_frame(self.last_image)
            self.current_image = frame
            self.current_quads = self.__split_frame(self.current_image)
            self.update_state = UpdateState.process_frames

        # processing frames until reached desire frame_frequency
        if self.update_state is UpdateState.process_frames:
            if self.frames_elapsed == self.FRAME_FREQUENCY:
                self.frames_elapsed = 0  # reset frames elapsed
                self.update_state = UpdateState.perform_comparison

        # if reached required frame frequency to perform boiling comparison
        if self.update_state is UpdateState.perform_comparison:
            # shift the images
            self.last_image = self.current_image
            self.current_image = frame

            # splits the frames
            self.last_quads = self.__split_frame(self.last_image)
            self.current_quads = self.__split_frame(self.current_image)

            burner_tuple = zip(burners, self.masks, self.last_quads, self.current_quads)

            # Detects boiling on active burners
            for idx, (burner, burner_mask, last_quad, current_quad) in enumerate(burner_tuple):
                # if there is a pot on burner
                if not burner.pot_detected:  # change back to not
                    score = self.___get_score(burner_mask, last_quad, current_quad)
                    self.file.write("S {}\n".format(score))
                    self.file.flush()
                    # if score is too low, means pot might have been moved/change occurs
                    # break out of program to recalculate masks on the next call to update
                    if score <= self.MASK_THRESH:
                        break

                    self.median_SSIM[idx].process(score)

                    # median is calculated when enough SSIMs have been recorded
                    if len(self.median_SSIM[idx].recorded_values) == self.SSIM_COUNT:
                        med = np.median(self.median_SSIM[idx].recorded_values)
                        self.median_SSIM[idx].recorded_values.clear()  # clear median queue
                        self.boiling[idx].process(med)

                    # check that at least 1 value is in boiling list
                    if len(self.boiling[idx].recorded_values) > 0:
                        # not boiling
                        if self.boil_state[idx] is BoilState.not_boiling:
                            # if it began to boil
                            if self.__check_boiling(self.boiling[idx].recorded_values, self.THRESH):
                                self.boil_state[idx] = BoilState.is_simmering
                                self.start_boiling[idx] = time.time()  # keeps track of time when started boiling
                        # began to boil
                        elif self.boil_state[idx] is BoilState.is_simmering:
                            # boiling if +30 seconds passed
                            if time.time() - self.start_boiling[idx] >= 30:
                                self.boil_state[idx] = BoilState.is_boiling
                            # not boiling if check_boiling returns False
                            elif not self.__check_boiling(self.boiling[idx].recorded_values, self.THRESH):
                                self.boil_state[idx] = BoilState.not_boiling
                        # confirmed to be boiling
                        elif self.boil_state[idx] is BoilState.is_boiling:
                            # if it stops boiling after having been confirmed
                            if not self.__check_boiling(self.boiling[idx].recorded_values, self.THRESH):
                                self.boil_state[idx] = BoilState.not_boiling
            # switch back to processing frames
            self.update_state = UpdateState.process_frames
        # sets appropriate stove burners to boiling
        for (burner, burner_boil) in zip(burners, self.boil_state):
            if burner_boil is BoilState.is_boiling and burner.temp >= self.MIN_BOILING_TEMP:
                burner.boiling = True  # Boiling is True
            else:
                burner.boiling = False  # False if not boiling / temp too low
        self.file.close()
